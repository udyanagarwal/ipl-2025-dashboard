import streamlit as st
import pandas as pd
import plotly.express as px

IPL_BLUE = "#172152"
IPL_ACCENT = "#FFB300"
BAT_COLOR = "#0072ff"
BOWL_COLOR = "#DE425B"
CARD_BG = "#f4f7fb"
label_font = dict(color=IPL_BLUE, size=18)

st.set_page_config(page_title="IPL 2024-25 Deliveries Dashboard", layout="wide")
st.markdown(f"<h1 style='color:{IPL_ACCENT}; text-align:center;'>🏏 IPL 2024 vs 2025 Dashboard</h1>", unsafe_allow_html=True)

# DATA LOAD AND COLUMN STANDARDIZATION
df24 = pd.read_csv("IPL24_All_Matches_Dataset_utf8.csv")
df25 = pd.read_csv("ipl_2025_deliveries.csv")

df24 = df24.rename(columns={
    "matchID": "match_id",
    "homeTeam": "batting_team",
    "bowlingTeam": "bowling_team",
    "batsmanName": "striker",
    "bowlerName": "bowler",
    "batsmanRuns": "runs_of_bat",
    "isWicket": "is_wicket"
})

if "season" not in df24.columns:
    df24['season'] = 2024
if "season" not in df25.columns:
    df25['season'] = 2025

for col in ["match_id","batting_team","bowling_team","striker","bowler","runs_of_bat","is_wicket"]:
    if col not in df24.columns:
        df24[col] = 0
    if col not in df25.columns:
        df25[col] = 0

df = pd.concat([df24, df25], ignore_index=True)

st.sidebar.markdown(f"<h3 style='color:{IPL_ACCENT};text-align:center;'>IPL Comparison</h3>", unsafe_allow_html=True)
season_options = sorted(df['season'].unique().tolist())
selected_season = st.sidebar.selectbox("Select Season", ["Both"] + [str(y) for y in season_options])

filtered_df = df.copy() if selected_season == "Both" else df[df['season'] == int(selected_season)]

def clean_team_list(series):
    teams = series.dropna().astype(str).unique().tolist()
    teams = [team for team in teams if team.lower() not in ["nan", "unknown"] and team.strip() != ""]
    return sorted(set(teams))

# Batting team
teams = clean_team_list(filtered_df['batting_team'])
selected_team = st.sidebar.selectbox("Select Batting Team", ["All"] + teams)

# Bowling team, with robust fallback and info message
bowling_teams = clean_team_list(filtered_df['bowling_team'])
if len(bowling_teams) > 0:
    selected_bowling_team = st.sidebar.selectbox("Select Bowling Team", ["All"] + bowling_teams)
else:
    selected_bowling_team = "All"
    st.sidebar.info("No valid bowling team data found for this season/data.")

stat_type = st.sidebar.selectbox("Choose Stats Type", ["Batting", "Bowling"])

if stat_type == "Batting":
    player_list = filtered_df["striker"].dropna().astype(str).unique().tolist()
    player_list = [x for x in player_list if x.lower() != "nan" and x.strip() != ""]
    selected_player = st.sidebar.selectbox("Choose Batter", ["All"] + sorted(player_list))
    filtered_player = filtered_df if selected_player == "All" else filtered_df[filtered_df["striker"] == selected_player]
else:
    player_list = filtered_df["bowler"].dropna().astype(str).unique().tolist()
    player_list = [x for x in player_list if x.lower() != "nan" and x.strip() != ""]
    selected_player = st.sidebar.selectbox("Choose Bowler", ["All"] + sorted(player_list))
    filtered_player = filtered_df if selected_player == "All" else filtered_df[filtered_df["bowler"] == selected_player]

if selected_team != "All":
    filtered_player = filtered_player[filtered_player['batting_team'] == selected_team]
if selected_bowling_team != "All":
    filtered_player = filtered_player[filtered_player['bowling_team'] == selected_bowling_team]

# KPI CARDS
if stat_type == "Batting":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Total Runs</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['runs_of_bat'].sum())}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Matches</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player['match_id'].nunique()}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Balls</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player.shape[0]}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Top 10 Batters {('for ' + selected_team) if selected_team!='All' else ''} (Runs, Season)</h2>", unsafe_allow_html=True)
    filter_for_top = filtered_df if selected_team == "All" else filtered_df[filtered_df["batting_team"] == selected_team]
    top_batters = filter_for_top.groupby(['season', 'striker'])['runs_of_bat'].sum().reset_index()
    top_batters = top_batters.groupby('season').apply(lambda x: x.nlargest(10, 'runs_of_bat')).reset_index(drop=True)
    fig_bat = px.bar(
        top_batters, x='striker', y='runs_of_bat', color='season',
        barmode='group', text='runs_of_bat',
        labels={'striker':'Player', 'runs_of_bat':'Runs','season':'Season'},
        category_orders={'season': season_options}
    )
    fig_bat.update_traces(textposition='outside')
    fig_bat.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Player", tickfont=label_font),
        yaxis=dict(title="Runs", tickfont=label_font))
    st.plotly_chart(fig_bat, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs by Team (Comparison)</h2>", unsafe_allow_html=True)
    team_runs = filtered_df.groupby(['season', 'batting_team'])['runs_of_bat'].sum().reset_index()
    fig_team = px.bar(
        team_runs, x='batting_team', y='runs_of_bat', color='season',
        barmode='group', text='runs_of_bat',
        labels={'batting_team':'Team', 'runs_of_bat':'Total Runs','season':'Season'},
        category_orders={'season': season_options}
    )
    fig_team.update_traces(textposition='outside')
    fig_team.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Team", tickfont=label_font),
        yaxis=dict(title="Total Runs", tickfont=label_font))
    st.plotly_chart(fig_team, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs Distribution</h2>", unsafe_allow_html=True)
    fig_hist = px.histogram(filtered_player, x='runs_of_bat', nbins=8, color='season', text_auto=True, barmode='group')
    fig_hist.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Runs per Ball", tickfont=label_font),
        yaxis=dict(title="Count", tickfont=label_font))
    st.plotly_chart(fig_hist, use_container_width=True)

    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_player.head(50))

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Total Wickets</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['is_wicket'].sum())}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Balls</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player.shape[0]}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Runs Conceded</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['runs_of_bat'].sum())}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Top 10 Bowlers (Wickets, Season)</h2>", unsafe_allow_html=True)
    top_bowlers = filtered_df.groupby(['season', 'bowler'])['is_wicket'].sum().reset_index()
    top_bowlers = top_bowlers.groupby('season').apply(lambda x: x.nlargest(10, 'is_wicket')).reset_index(drop=True)
    fig_bowl = px.bar(
        top_bowlers, x='bowler', y='is_wicket', color='season',
        barmode='group', text='is_wicket',
        labels={'bowler':'Bowler', 'is_wicket':'Wickets','season':'Season'},
        category_orders={'season': season_options}
    )
    fig_bowl.update_traces(textposition='outside')
    fig_bowl.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Bowler", tickfont=label_font),
        yaxis=dict(title="Wickets", tickfont=label_font))
    st.plotly_chart(fig_bowl, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Top 5 Bowlers for {selected_bowling_team if selected_bowling_team!='All' else 'All Teams'} (Season)</h2>", unsafe_allow_html=True)
    filtered_bowl_for_team = filtered_df if selected_bowling_team == "All" else filtered_df[filtered_df['bowling_team'] == selected_bowling_team]
    top_bowlers_team = filtered_bowl_for_team.groupby(['season','bowler'])['is_wicket'].sum().reset_index()
    top_bowlers_team = top_bowlers_team.groupby(['season']).apply(lambda x: x.nlargest(5, 'is_wicket')).reset_index(drop=True)
    fig_team_bowl = px.bar(
        top_bowlers_team, x='bowler', y='is_wicket', color='season',
        barmode='group', text='is_wicket',
        labels={'bowler':'Bowler', 'is_wicket':'Wickets','season':'Season'},
        category_orders={'season': season_options}
    )
    fig_team_bowl.update_traces(textposition='outside')
    fig_team_bowl.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Bowler", tickfont=label_font),
        yaxis=dict(title="Wickets", tickfont=label_font))
    st.plotly_chart(fig_team_bowl, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs Conceded by Team (Comparison)</h2>", unsafe_allow_html=True)
    bowl_team_runs = filtered_df.groupby(['season', 'bowling_team'])['runs_of_bat'].sum().reset_index()
    fig_bowlteam = px.bar(
        bowl_team_runs, x='bowling_team', y='runs_of_bat', color='season',
        barmode='group', text='runs_of_bat',
        labels={'bowling_team':'Bowling Team', 'runs_of_bat':'Runs Conceded','season':'Season'},
        category_orders={'season': season_options}
    )
    fig_bowlteam.update_traces(textposition='outside')
    fig_bowlteam.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Bowling Team", tickfont=label_font),
        yaxis=dict(title="Runs Conceded", tickfont=label_font))
    st.plotly_chart(fig_bowlteam, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Wicket Distribution</h2>", unsafe_allow_html=True)
    fig_wickhist = px.histogram(filtered_player, x='is_wicket', color='season', nbins=2, text_auto=True, barmode='group')
    fig_wickhist.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="is_wicket", tickfont=label_font),
        yaxis=dict(title="Count", tickfont=label_font))
    st.plotly_chart(fig_wickhist, use_container_width=True)

    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_player.head(50))

st.markdown(f"""
<style>
.sidebar .sidebar-content {{background-color: {IPL_BLUE} !important; color: #fff;}}
.reportview-container, .main {{background: #181c25;}}
</style>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.express as px

# IPL Color Pallete & Card Styling
IPL_BLUE = "#172152"
IPL_ACCENT = "#FFB300"
BAT_COLOR = "#0072ff"
BOWL_COLOR = "#DE425B"
CARD_BG = "#f4f7fb"

st.set_page_config(page_title="IPL 2025 Deliveries Dashboard", layout="wide")
st.markdown(f"<h1 style='color:{IPL_ACCENT}; text-align:center;'>🏏 IPL 2025 Deliveries Dashboard</h1>", unsafe_allow_html=True)

df = pd.read_csv("ipl_2025_deliveries.csv")

# Sidebar filters
st.sidebar.markdown(f"<h3 style='color:{IPL_ACCENT};text-align:center;'>IPL Analytics</h3>", unsafe_allow_html=True)
stat_type = st.sidebar.selectbox("Choose Stats Type", ["Batting", "Bowling"])
teams = df['batting_team'].unique().tolist()
selected_team = st.sidebar.selectbox("Select Batting Team", ["All"] + teams)
filtered_df = df if selected_team == "All" else df[df['batting_team'] == selected_team]

# Per-player pick
if stat_type == "Batting":
    player_list = filtered_df["striker"].unique().tolist()
    selected_player = st.sidebar.selectbox("Choose Batter", ["All"] + player_list)
    filtered_player = filtered_df if selected_player == "All" else filtered_df[filtered_df["striker"] == selected_player]
else:
    player_list = filtered_df["bowler"].unique().tolist()
    selected_player = st.sidebar.selectbox("Choose Bowler", ["All"] + player_list)
    filtered_player = filtered_df if selected_player == "All" else filtered_df[filtered_df["bowler"] == selected_player]

label_font = dict(color=IPL_BLUE, size=18)

if stat_type == "Batting":
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Total Runs</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['runs_of_bat'].sum())}</span></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Matches</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player['match_id'].nunique()}</span></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BAT_COLOR};'>Balls</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player.shape[0]}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Top 10 Batters (Runs)</h2>", unsafe_allow_html=True)
    leaderboard = filtered_df.groupby('striker')['runs_of_bat'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bat = px.bar(leaderboard, x='striker', y='runs_of_bat', text='runs_of_bat',
                     color='runs_of_bat', color_continuous_scale=[BAT_COLOR, IPL_ACCENT])
    fig_bat.update_traces(textposition='outside')
    fig_bat.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Player", tickfont=label_font),
        yaxis=dict(title="Runs", tickfont=label_font),
    )
    st.plotly_chart(fig_bat, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs by Team</h2>", unsafe_allow_html=True)
    team_runs = df.groupby('batting_team')['runs_of_bat'].sum().sort_values(ascending=False).reset_index()
    fig_team = px.bar(team_runs, x='batting_team', y='runs_of_bat', text='runs_of_bat',
                      color='runs_of_bat', color_continuous_scale=[BAT_COLOR, IPL_ACCENT])
    fig_team.update_traces(textposition='outside')
    fig_team.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Team", tickfont=label_font),
        yaxis=dict(title="Total Runs", tickfont=label_font),
    )
    st.plotly_chart(fig_team, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs Distribution</h2>", unsafe_allow_html=True)
    fig_hist = px.histogram(filtered_player, x='runs_of_bat', nbins=8, color_discrete_sequence=[BAT_COLOR], text_auto=True)
    fig_hist.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Runs per Ball", tickfont=label_font),
        yaxis=dict(title="Count", tickfont=label_font),
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_player.head(50))

else:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Total Wickets</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['is_wicket'].sum())}</span></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Balls</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{filtered_player.shape[0]}</span></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div style='background:{CARD_BG};padding:14px;border-radius:10px'><span style='font-size:26px;color:{BOWL_COLOR};'>Runs Conceded</span><br><span style='font-size:32px;font-weight:bold;color:{IPL_BLUE};'>{int(filtered_player['runs_of_bat'].sum())}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Top 10 Bowlers (Wickets)</h2>", unsafe_allow_html=True)
    leaderboard = filtered_df.groupby('bowler')['is_wicket'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bowl = px.bar(leaderboard, x='bowler', y='is_wicket', text='is_wicket',
                      color='is_wicket', color_continuous_scale=[BOWL_COLOR, IPL_ACCENT])
    fig_bowl.update_traces(textposition='outside')
    fig_bowl.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Bowler", tickfont=label_font),
        yaxis=dict(title="Wickets", tickfont=label_font),
    )
    st.plotly_chart(fig_bowl, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Runs Conceded by Team</h2>", unsafe_allow_html=True)
    bowl_team_runs = df.groupby('bowling_team')['runs_of_bat'].sum().sort_values(ascending=False).reset_index()
    fig_bowlteam = px.bar(bowl_team_runs, x='bowling_team', y='runs_of_bat', text='runs_of_bat',
                          color='runs_of_bat', color_continuous_scale=[BOWL_COLOR, IPL_ACCENT])
    fig_bowlteam.update_traces(textposition='outside')
    fig_bowlteam.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="Bowling Team", tickfont=label_font),
        yaxis=dict(title="Runs Conceded", tickfont=label_font),
    )
    st.plotly_chart(fig_bowlteam, use_container_width=True)

    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:24px;'>Wicket Distribution</h2>", unsafe_allow_html=True)
    fig_wickhist = px.histogram(filtered_player, x='is_wicket', nbins=2, color_discrete_sequence=[BOWL_COLOR], text_auto=True)
    fig_wickhist.update_layout(
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font=dict(color=IPL_BLUE),
        xaxis=dict(title="is_wicket", tickfont=label_font),
        yaxis=dict(title="Count", tickfont=label_font),
    )
    st.plotly_chart(fig_wickhist, use_container_width=True)
    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_player.head(50))

st.markdown(f"""
<style>
.sidebar .sidebar-content {{background-color: {IPL_BLUE} !important; color: #fff;}}
.reportview-container, .main {{background: #181c25;}}
</style>
""", unsafe_allow_html=True)

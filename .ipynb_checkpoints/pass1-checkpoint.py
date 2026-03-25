import streamlit as st
import pandas as pd
import plotly.express as px

IPL_BLUE = "#172152"
IPL_ACCENT = "#FFB300"
BAT_COLOR = "#eaf2fd"
BOWL_COLOR = "#fdeaea"
CARD_BG = "#f4f7fb"
DARK_BG = "#181c25"
TEXT_COLOR = "#FFFFFF"

st.set_page_config(page_title="IPL 2021 vs 2025 Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
    <style>
        body, .reportview-container, .main {{
            background-color: {DARK_BG};
            color: {TEXT_COLOR};
            font-family: 'Inter', 'Segoe UI', Verdana, sans-serif;
        }}
        .sidebar .sidebar-content {{
            background: {IPL_BLUE};
            color: {TEXT_COLOR};
        }}
        h1, h2, h3, h4 {{
            font-weight: 900;
        }}
        .main-title {{
            color: {IPL_ACCENT} !important;
            text-align: center;
            font-size: 2.7rem;
            letter-spacing: 3px;
            margin-bottom: 0.5rem;
        }}
        hr {{
            border-top: 2px solid {IPL_ACCENT};
            margin: 1.3rem 0;
        }}
        .stat-card {{
            background: {CARD_BG};
            border-radius: 16px;
            padding: 1.6rem 1.2rem;
            margin-bottom: 17px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.12);
            color: {IPL_BLUE};
            text-align: center;
            font-weight: 700;
            transition: box-shadow .3s;
        }}
        .stat-card:hover {{
            box-shadow: 0 8px 30px #FFB30033;
        }}
        .css-1aumxhk {{
            background-color: {CARD_BG};
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏏 IPL 2021 vs 2025 Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr />", unsafe_allow_html=True)

# --- Load Data ---
try:
    df25 = pd.read_csv("ipl_2025_deliveries.csv")
except Exception as e:
    st.error("Error loading ipl_2025_deliveries.csv. Please check the file exists and is not empty.")
    st.stop()
try:
    df21 = pd.read_csv("IPL_ball_by_ball_updated.csv")
except Exception as e:
    st.error("Error loading IPL_ball_by_ball_updated.csv. Please check the file exists and is not empty.")
    st.stop()

df25 = df25.rename(columns={"batting_name": "batting_team", "bowling_team": "bowling_team", "runs_of_bat": "runs_off_bat"})
df21 = df21.rename(columns={"batting_name": "batting_team", "bowling_name": "bowling_team", "runs_off_bat": "runs_off_bat"})

for df in [df25, df21]:
    if "wicket_type" not in df.columns:
        df["wicket_type"] = None
    df["is_wicket"] = df["wicket_type"].notnull().astype(int)
    df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0)
    df["is_wicket"] = pd.to_numeric(df["is_wicket"], errors="coerce").fillna(0)

if "season" in df21.columns:
    df21 = df21[df21['season'] == 2021].copy()
df25['season'] = 2025

year_opts = ["2021", "2025"]
opt_year = st.sidebar.selectbox("Select Year", year_opts)
stat_type = st.sidebar.radio("Stats Section", ["Batting", "Bowling"], index=0)

if opt_year == "2021":
    df = df21
    teams = sorted(set(pd.concat([df['batting_team'], df['bowling_team']]).dropna().unique()))
    players = sorted(set(df['striker'].dropna().unique()).union(df['bowler'].dropna().unique()))
    team_label = "Team (2021)"
    player_label = "Player (2021)"
    coltheme = "Blues"
    year_label = "2021"
else:
    df = df25
    teams = sorted(set(pd.concat([df['batting_team'], df['bowling_team']]).dropna().unique()))
    players = sorted(set(df['striker'].dropna().unique()).union(df['bowler'].dropna().unique()))
    team_label = "Team (2025)"
    player_label = "Player (2025)"
    coltheme = "Oranges"
    year_label = "2025"

selected_team = st.sidebar.selectbox(team_label, ["All"] + teams)
selected_player = st.sidebar.selectbox(player_label, ["All Players"] + players)

def stat_card(label, value, icon, bg_color, col):
    col.markdown(f"""
        <div class="stat-card" style="background:{bg_color};">
            <div style="font-size:2.2rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:1.15rem; font-weight:600;">{label}</div>
            <div style="font-size:1.9rem; font-weight:500; margin-top:0.4rem;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Main Interface as before ---

# --- NEW FEATURE: Top 10 Bowlers Against Team ---

if selected_team != "All":
    st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers vs {selected_team} ({year_label})</h3>", unsafe_allow_html=True)
    # Filter where batting_team is the selected team: i.e., who bowled against them
    filter_df = df[df["batting_team"] == selected_team]
    # Now group by bowler and sum wickets
    bowlers_against = filter_df.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
    if not bowlers_against.empty:
        fig = px.bar(
            bowlers_against,
            y=bowlers_against.values,
            x=bowlers_against.index,
            text=bowlers_against.values,
            labels={"x": "Bowler", "y": "Wickets"},
            color=bowlers_against.values,
            color_continuous_scale=coltheme,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor=DARK_BG,
            paper_bgcolor=DARK_BG,
            font_color=TEXT_COLOR,
            margin=dict(t=40, b=40, l=40, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No bowling data available for the selected team.")

# --- Rest of your interface (player/team cards etc) ---

if selected_player != "All Players":
    batting_df = df[df['striker'] == selected_player]
    bowling_df = df[df['bowler'] == selected_player]
    st.markdown(f"""
        <div style='background:{CARD_BG}; border-radius:20px; text-align:left; padding:1.1rem 1.8rem 1.3rem 1.8rem; margin-bottom:4px; box-shadow: 0 2px 8px rgba(16,32,80,0.13); width:65%;'>
            <span style='font-size:2rem;'>👤</span>
            <strong style='font-size:1.9rem; color:{IPL_ACCENT};'>{selected_player}</strong>
            <span style='font-size:1.1rem; color:#4a4c5b; margin-left:1.2rem;'>Team: <b>{selected_team}</b> | Season: <b>{year_label}</b></span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr />", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{IPL_ACCENT}; margin-top:0;'>Batting & Bowling Stats</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    stat_card("Total Runs", int(batting_df['runs_off_bat'].sum()), "🏏", BAT_COLOR, col1)
    stat_card("Balls Faced", batting_df.shape[0], "🎯", BAT_COLOR, col2)
    stat_card("Matches Batted", batting_df['match_id'].nunique() if 'match_id' in batting_df else "-", "📋", BAT_COLOR, col3)

    col4, col5, col6 = st.columns(3)
    stat_card("Total Wickets", int(bowling_df['is_wicket'].sum()), "⚡", BOWL_COLOR, col4)
    stat_card("Balls Bowled", bowling_df.shape[0], "🟠", BOWL_COLOR, col5)
    stat_card("Runs Conceded", int(bowling_df['runs_off_bat'].sum()), "💸", BOWL_COLOR, col6)

    matches_bowled = bowling_df['match_id'].nunique() if 'match_id' in bowling_df else "-"
    st.markdown(f"""
        <div style='width:28%; display:inline-block;'>
            <div style='background:{BOWL_COLOR}; border-radius:16px; padding:0.9rem 0.8rem; margin-bottom:18px; box-shadow:0 4px 12px rgba(0,0,0,0.14); text-align:center;'>
                <span style='font-size:1.7rem;'>📋</span>
                <h4 style='margin:0; color:#b53835;'>{'Matches Bowled'}</h4>
                <p style='font-size:1.5rem; margin:0; color:#9e1c1c;'>{matches_bowled}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if selected_team != "All":
        st.markdown(f"<hr />", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:0.5rem;'>Stats against {selected_team}</h3>", unsafe_allow_html=True)
        vs_bowl_df = df[(df['striker'] == selected_player) & (df['bowling_team'] == selected_team)]
        vs_bat_df = df[(df['bowler'] == selected_player) & (df['batting_team'] == selected_team)]

        col7, col8 = st.columns(2)
        col7.markdown(f"**Batting vs {selected_team}**")
        bat_team_runs = int(vs_bowl_df['runs_off_bat'].sum())
        balls_team = vs_bowl_df.shape[0]
        matches_team = vs_bowl_df['match_id'].nunique() if 'match_id' in vs_bowl_df else '-'
        col7.markdown(f"- Runs: `{bat_team_runs}`\n- Balls: `{balls_team}`\n- Matches: `{matches_team}`")
        col8.markdown(f"**Bowling vs {selected_team}**")
        bowl_team_wickets = int(vs_bat_df['is_wicket'].sum())
        balls_bowl_team = vs_bat_df.shape[0]
        runs_conceded_team = int(vs_bat_df['runs_off_bat'].sum())
        matches_bowl_team = vs_bat_df['match_id'].nunique() if 'match_id' in vs_bat_df else '-'
        col8.markdown(f"- Wickets: `{bowl_team_wickets}`\n- Balls: `{balls_bowl_team}`\n- Runs Conceded: `{runs_conceded_team}`\n- Matches: `{matches_bowl_team}`")

    st.markdown("<hr />", unsafe_allow_html=True)
    with st.expander(f"Preview Batting Data ({selected_player}, {year_label})"):
        st.dataframe(batting_df.head(20), use_container_width=True)
    with st.expander(f"Preview Bowling Data ({selected_player}, {year_label})"):
        st.dataframe(bowling_df.head(20), use_container_width=True)

else:
    # Team/Overall stats
    if stat_type == "Batting":
        filtered = df if selected_team == "All" else df[df["batting_team"] == selected_team]
        col1, col2, col3 = st.columns(3)
        stat_card("Total Runs", int(filtered['runs_off_bat'].sum()), "🏏", BAT_COLOR, col1)
        stat_card("Unique Matches", filtered['match_id'].nunique() if "match_id" in filtered.columns else "-", "📋", BAT_COLOR, col2)
        stat_card("Balls", len(filtered), "🎯", BAT_COLOR, col3)

        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Batters for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
        topbat = filtered.groupby("striker")['runs_off_bat'].sum().sort_values(ascending=False).head(10)
        if not topbat.empty:
            fig = px.bar(
                topbat, y=topbat.values, x=topbat.index, text=topbat.values,
                labels={'x':'Batter', 'y':'Runs'}, color=topbat.values, color_continuous_scale=coltheme
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font_color=TEXT_COLOR, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No batting data available for the selected options.")

    else:
        filtered = df if selected_team == "All" else df[df["bowling_team"] == selected_team]
        col1, col2, col3 = st.columns(3)
        stat_card("Total Wickets", int(filtered['is_wicket'].sum()), "⚡", BOWL_COLOR, col1)
        stat_card("Balls", len(filtered), "🟠", BOWL_COLOR, col2)
        stat_card("Runs Conceded", int(filtered['runs_off_bat'].sum()), "💸", BOWL_COLOR, col3)

        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
        topbowl = filtered.groupby("bowler")['is_wicket'].sum().sort_values(ascending=False).head(10)
        if not topbowl.empty:
            fig = px.bar(
                topbowl, y=topbowl.values, x=topbowl.index, text=topbowl.values,
                labels={'x':'Bowler', 'y':'Wickets'}, color=topbowl.values, color_continuous_scale=coltheme
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font_color=TEXT_COLOR, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No bowling data available for the selected options.")

    st.markdown("<hr />", unsafe_allow_html=True)
    with st.expander(f"Preview {year_label} Data"):
        st.dataframe(filtered.head(30), use_container_width=True)

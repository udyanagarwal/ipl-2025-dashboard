import streamlit as st
import pandas as pd
import plotly.express as px

IPL_BLUE = "#172152"
IPL_ACCENT = "#FFB300"
BAT_COLOR = "#0072ff"
BOWL_COLOR = "#DE425B"
CARD_BG = "#f4f7fb"

st.set_page_config(page_title="IPL 2021 vs 2025 Dashboard", layout="wide")
st.markdown(f"<h1 style='color:{IPL_ACCENT}; text-align:center;'>🏏 IPL 2021 vs 2025 Dashboard</h1>", unsafe_allow_html=True)

# ---- Load Data ----
df25 = pd.read_csv("ipl_2025_deliveries.csv")
df21 = pd.read_csv("IPL_ball_by_ball_updated.csv")

# ---- Standardize Columns ----
df25 = df25.rename(columns={
    "batting_name": "batting_team",
    "bowling_team": "bowling_team",
    "runs_of_bat": "runs_off_bat"
})
df21 = df21.rename(columns={
    "batting_name": "batting_team",
    "bowling_name": "bowling_team",
    "runs_off_bat": "runs_off_bat"
})

for df in [df25, df21]:
    df["is_wicket"] = df["wicket_type"].notnull().astype(int)
    df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0)
    df["is_wicket"] = pd.to_numeric(df["is_wicket"], errors="coerce").fillna(0)

if "season" in df21.columns:
    df21 = df21[df21['season'] == 2021].copy()
df25['season'] = 2025

# ---- Sidebar Controls ----
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

# ---- Data Filtering and Display Logic ----
if selected_player != "All Players":
    # Overall Player Stats
    batting_df = df[df['striker'] == selected_player]
    bowling_df = df[df['bowler'] == selected_player]

    st.markdown(f"<h2 style='color:{IPL_ACCENT};'>Player Stats: {selected_player} ({year_label})</h2>", unsafe_allow_html=True)
    st.subheader("Overall Batting Stats")
    st.write(f"**Total Runs:** {int(batting_df['runs_off_bat'].sum())}")
    st.write(f"**Balls Faced:** {batting_df.shape[0]}")
    st.write(f"**Unique Matches Batted:** {batting_df['match_id'].nunique() if 'match_id' in batting_df else '-'}")

    st.subheader("Overall Bowling Stats")
    st.write(f"**Total Wickets:** {int(bowling_df['is_wicket'].sum())}")
    st.write(f"**Balls Bowled:** {bowling_df.shape[0]}")
    st.write(f"**Runs Conceded:** {int(bowling_df['runs_off_bat'].sum())}")
    st.write(f"**Unique Matches Bowled:** {bowling_df['match_id'].nunique() if 'match_id' in bowling_df else '-'}")

    # If a specific team is selected, show "against" that team stats
    if selected_team != "All":
        st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Stats against {selected_team}</h3>", unsafe_allow_html=True)
        
        # Player's batting against selected team (team = bowling_team)
        vs_bowl_df = df[(df['striker'] == selected_player) & (df['bowling_team'] == selected_team)]
        st.write("**Batting against team:**")
        st.write(f"Total Runs: {int(vs_bowl_df['runs_off_bat'].sum())}")
        st.write(f"Balls Faced: {vs_bowl_df.shape[0]}")
        st.write(f"Unique Matches: {vs_bowl_df['match_id'].nunique() if 'match_id' in vs_bowl_df else '-'}")

        # Player's bowling against selected team (team = batting_team)
        vs_bat_df = df[(df['bowler'] == selected_player) & (df['batting_team'] == selected_team)]
        st.write("**Bowling against team:**")
        st.write(f"Total Wickets: {int(vs_bat_df['is_wicket'].sum())}")
        st.write(f"Balls Bowled: {vs_bat_df.shape[0]}")
        st.write(f"Runs Conceded: {int(vs_bat_df['runs_off_bat'].sum())}")
        st.write(f"Unique Matches: {vs_bat_df['match_id'].nunique() if 'match_id' in vs_bat_df else '-'}")

    with st.expander(f"Preview Batting Data ({selected_player}, {year_label})"):
        st.dataframe(batting_df.head(30))
    with st.expander(f"Preview Bowling Data ({selected_player}, {year_label})"):
        st.dataframe(bowling_df.head(30))
else:
    # Team stats as before
    if stat_type == "Batting":
        filtered = df if selected_team == "All" else df[df["batting_team"] == selected_team]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Runs", int(filtered['runs_off_bat'].sum()))
        col2.metric("Unique Matches", filtered['match_id'].nunique() if "match_id" in filtered.columns else "-")
        col3.metric("Balls", len(filtered))
        st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Batters for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
        topbat = filtered.groupby("striker")['runs_off_bat'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(topbat, y=topbat.values, x=topbat.index, text=topbat.values,
                     labels={'x':'Batter', 'y':'Runs'}, color=topbat.values, color_continuous_scale=coltheme)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        filtered = df if selected_team == "All" else df[df["bowling_team"] == selected_team]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Wickets", int(filtered['is_wicket'].sum()))
        col2.metric("Balls", len(filtered))
        col3.metric("Runs Conceded", int(filtered['runs_off_bat'].sum()))
        st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Bowlers for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
        topbowl = filtered.groupby("bowler")['is_wicket'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(topbowl, y=topbowl.values, x=topbowl.index, text=topbowl.values,
                     labels={'x':'Bowler', 'y':'Wickets'}, color=topbowl.values, color_continuous_scale=coltheme)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    with st.expander(f"Preview {year_label} Data"):
        st.dataframe(filtered.head(30))

st.markdown(f"""
<style>
.sidebar .sidebar-content {{background-color: {IPL_BLUE} !important; color: #fff;}}
.reportview-container, .main {{background: #181c25;}}
</style>
""", unsafe_allow_html=True)

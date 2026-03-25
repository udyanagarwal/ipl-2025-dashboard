import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IPL 2025 Deliveries Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:#ff4b4b;'>🏏 IPL 2025 Deliveries Dashboard</h1>", unsafe_allow_html=True)

df = pd.read_csv("ipl_2025_deliveries.csv")

# === Sidebar: Stats filters ===
stat_type = st.sidebar.selectbox("Select Stats Type", ["Batting", "Bowling"])
teams = df['batting_team'].unique().tolist()
selected_team = st.sidebar.selectbox("Select Batting Team", ["All"] + teams)
if selected_team != "All":
    filtered_df = df[df['batting_team'] == selected_team]
else:
    filtered_df = df

if stat_type == "Batting":
    players = filtered_df["striker"].unique().tolist()
    selected_player = st.sidebar.selectbox("Select Batter", ["All"] + players)
    if selected_player != "All":
        filtered_df = filtered_df[filtered_df["striker"] == selected_player]

    total_runs = int(filtered_df['runs_of_bat'].sum())
    total_matches = filtered_df['match_id'].nunique()
    total_balls = filtered_df.shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Runs", f"{total_runs}")
    col2.metric("Unique Matches", f"{total_matches}")
    col3.metric("Total Balls", f"{total_balls}")

    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_df.head(50))

    st.subheader("Top 10 Batters (Runs)")
    top_batters = filtered_df.groupby('striker')['runs_of_bat'].sum().sort_values(ascending=False).head(10)
    fig_bat = px.bar(top_batters, x=top_batters.index, y='runs_of_bat', labels={'x':'Player', 'runs_of_bat':'Runs'})
    st.plotly_chart(fig_bat, use_container_width=True)

    st.subheader("Total Runs by Batting Team")
    team_runs = df.groupby('batting_team')['runs_of_bat'].sum().sort_values(ascending=False)
    fig_team = px.bar(team_runs, x=team_runs.index, y='runs_of_bat', labels={'x':'Team', 'runs_of_bat':'Total Runs'}, color=team_runs.index)
    st.plotly_chart(fig_team, use_container_width=True)

    st.subheader("Runs Distribution Per Ball")
    fig_hist = px.histogram(filtered_df, x='runs_of_bat', nbins=8, color_discrete_sequence=['#636efa'])
    st.plotly_chart(fig_hist, use_container_width=True)

elif stat_type == "Bowling":
    players_bowl = filtered_df["bowler"].unique().tolist()
    selected_bowler = st.sidebar.selectbox("Select Bowler", ["All"] + players_bowl)
    if selected_bowler != "All":
        filtered_df = filtered_df[filtered_df["bowler"] == selected_bowler]

    total_wickets = int(filtered_df['is_wicket'].sum()) if 'is_wicket' in filtered_df.columns else 0
    total_balls = filtered_df.shape[0]
    runs_conceded = int(filtered_df['runs_of_bat'].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Wickets", f"{total_wickets}")
    col2.metric("Total Balls", f"{total_balls}")
    col3.metric("Runs Conceded", f"{runs_conceded}")

    with st.expander("Preview DataFrame"):
        st.dataframe(filtered_df.head(50))

    st.subheader("Top 10 Bowlers (Wickets)")
    if 'is_wicket' in df.columns:
        top_bowlers = filtered_df.groupby('bowler')['is_wicket'].sum().sort_values(ascending=False).head(10)
        fig_bowl = px.bar(top_bowlers, x=top_bowlers.index, y='is_wicket', labels={'x':'Bowler', 'is_wicket':'Wickets'})
        st.plotly_chart(fig_bowl, use_container_width=True)
    else:
        st.warning("No 'is_wicket' column found. Can't visualize wickets stats.")

    st.subheader("Total Runs Conceded by Bowling Team")
    bowling_team_runs = df.groupby('bowling_team')['runs_of_bat'].sum().sort_values(ascending=False)
    fig_bowlteam = px.bar(bowling_team_runs, x=bowling_team_runs.index, y='runs_of_bat', labels={'x':'Team', 'runs_of_bat':'Runs Conceded'}, color=bowling_team_runs.index)
    st.plotly_chart(fig_bowlteam, use_container_width=True)

    if 'is_wicket' in df.columns:
        st.subheader("Wickets Distribution Per Ball")
        fig_wickhist = px.histogram(filtered_df, x='is_wicket', nbins=2, color_discrete_sequence=['#ffa15a'], labels={'is_wicket':'Wicket (0: No, 1: Yes)'})
        st.plotly_chart(fig_wickhist, use_container_width=True)

st.markdown("""
<style>
    .sidebar .sidebar-content { background-color: #232946 !important; }
    .reportview-container { background: #16161a }
</style>
""", unsafe_allow_html=True)

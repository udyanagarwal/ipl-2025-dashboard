import streamlit as st
import pandas as pd
import plotly.express as px

# === Page settings ===
st.set_page_config(page_title="IPL 2025 Deliveries Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:#ff4b4b;'>🏏 IPL 2025 Deliveries Dashboard</h1>", unsafe_allow_html=True)

# === Load data ===
df = pd.read_csv("ipl_2025_deliveries.csv")

# === Filters ===
teams = df['batting_team'].unique().tolist()
selected_team = st.sidebar.selectbox("Select Batting Team", ["All"] + teams)
if selected_team != "All":
    filtered_df = df[df['batting_team'] == selected_team]
else:
    filtered_df = df

# === KPIs ===
total_runs = int(filtered_df['runs_of_bat'].sum())
total_matches = filtered_df['match_id'].nunique()
total_balls = filtered_df.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Runs (filtered)", f"{total_runs}")
col2.metric("Unique Matches (filtered)", f"{total_matches}")
col3.metric("Total Balls (filtered)", f"{total_balls}")

# === Data Preview ===
with st.expander("Preview DataFrame"):
    st.dataframe(filtered_df.head(50))

# === Top Batters Bar Chart ===
st.subheader("Top 10 Batters (Runs)")
top_batters = filtered_df.groupby('striker')['runs_of_bat'].sum().sort_values(ascending=False).head(10)
fig_bat = px.bar(top_batters, x=top_batters.index, y='runs_of_bat', labels={'x':'Player', 'runs_of_bat':'Runs'})
st.plotly_chart(fig_bat, use_container_width=True)

# === Team Runs Comparison ===
st.subheader("Total Runs by Batting Team")
team_runs = df.groupby('batting_team')['runs_of_bat'].sum().sort_values(ascending=False)
fig_team = px.bar(team_runs, x=team_runs.index, y='runs_of_bat', labels={'x':'Team', 'runs_of_bat':'Total Runs'},
                  color=team_runs.index)
st.plotly_chart(fig_team, use_container_width=True)

# === Runs Distribution ===
st.subheader("Runs Distribution Per Ball")
fig_hist = px.histogram(filtered_df, x='runs_of_bat', nbins=8, color_discrete_sequence=['#636efa'])
st.plotly_chart(fig_hist, use_container_width=True)

# === Custom Style Notes ===
st.markdown("""
<style>
    .sidebar .sidebar-content { background-color: #232946 !important; }
    .reportview-container { background: #16161a }
</style>
""", unsafe_allow_html=True)



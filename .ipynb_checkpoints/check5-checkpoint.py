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

# --------------- LOAD DATA ---------------
df21 = pd.read_csv("IPL_ball_by_ball_updated.csv")
df25 = pd.read_csv("ipl_2025_deliveries.csv")

# 2021 column mappings (as in your screenshots)
df21 = df21.rename(columns={
    "batting_team": "batting_team",
    "bowling_team": "bowling_team",
    "striker": "striker",
    "bowler": "bowler",
    "runs_off_bat": "runs_off_bat",
    "is_wicket": "is_wicket"
})
df21['season'] = 2021

# 2025 column mappings (map as per your sheet: batting_te, bowling_te, runs_of_b)
df25 = df25.rename(columns={
    "batting_te": "batting_team",
    "bowling_te": "bowling_team",
    "striker": "striker",
    "bowler": "bowler",
    "runs_of_b": "runs_off_bat",
    "is_wicket": "is_wicket"
})
df25['season'] = 2025

# CONVERT columns to numeric for aggregation (avoids error shown in your screenshot)
for df in [df21, df25]:
    for col in ["runs_off_bat", "is_wicket"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# --- SIDEBAR CONTROLS ---
year_opts = ["2021", "2025"]
opt_year = st.sidebar.selectbox("Select Year", year_opts)
stat_type = st.sidebar.selectbox("Choose Stats Type", ["Batting", "Bowling"])

teams21 = sorted(set(pd.concat([df21['batting_team'], df21['bowling_team']]).dropna()))
teams25 = sorted(set(pd.concat([df25['batting_team'], df25['bowling_team']]).dropna()))
selected_team_21 = st.sidebar.selectbox("Team (2021)", ["All"] + teams21)
selected_team_25 = st.sidebar.selectbox("Team (2025)", ["All"] + teams25)

# --- SELECTION LOGIC ---
if opt_year == "2021":
    df_selected = df21
    selected_team = selected_team_21
    coltheme = "Blues"
    year_label = '2021'
else:
    df_selected = df25
    selected_team = selected_team_25
    coltheme = "Oranges"
    year_label = '2025'

# --------- DASHBOARD KPIs AND CHARTS ----------
if stat_type == "Batting":
    filter_df = df_selected if selected_team == "All" else df_selected[df_selected['batting_team'] == selected_team]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Total Runs</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(filter_df['runs_off_bat'].sum())}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Unique Matches</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{filter_df['match_id'].nunique() if 'match_id' in filter_df.columns else 'N/A'}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{filter_df.shape[0]}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Batters for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
    groupbat = filter_df.groupby("striker")["runs_off_bat"].sum().reset_index()
    topbat = groupbat.sort_values("runs_off_bat", ascending=False).head(10)
    fig = px.bar(topbat, x="striker", y="runs_off_bat", text="runs_off_bat",
                   labels={"striker": "Batter", "runs_off_bat": "Runs"}, color="runs_off_bat", color_continuous_scale=coltheme)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
else:
    filter_df = df_selected if selected_team == "All" else df_selected[df_selected['bowling_team'] == selected_team]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Total Wickets</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(filter_df['is_wicket'].sum())}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{filter_df.shape[0]}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Runs Conceded</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(filter_df['runs_off_bat'].sum())}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Bowlers for {selected_team if selected_team != 'All' else 'All Teams'} ({year_label})</h3>", unsafe_allow_html=True)
    groupbowl = filter_df.groupby("bowler")["is_wicket"].sum().reset_index()
    topbowl = groupbowl.sort_values("is_wicket", ascending=False).head(10)
    figb = px.bar(topbowl, x="bowler", y="is_wicket", text="is_wicket",
                   labels={"bowler": "Bowler", "is_wicket": "Wickets"}, color="is_wicket", color_continuous_scale=coltheme)
    figb.update_traces(textposition='outside')
    st.plotly_chart(figb, use_container_width=True)

with st.expander(f"Preview {year_label} DataFrame (First 30 rows)"):
    st.dataframe(filter_df.head(30))

st.markdown(f"""
<style>
.sidebar .sidebar-content {{background-color: {IPL_BLUE} !important; color: #fff;}}
.reportview-container, .main {{background: #181c25;}}
</style>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.express as px

IPL_BLUE = "#172152"
IPL_ACCENT = "#FFB300"
BAT_COLOR = "#0072ff"
BOWL_COLOR = "#DE425B"
CARD_BG = "#f4f7fb"
label_font = dict(color=IPL_BLUE, size=18)

st.set_page_config(page_title="IPL 2024 vs 2025 Dashboard", layout="wide")
st.markdown(f"<h1 style='color:{IPL_ACCENT}; text-align:center;'>🏏 IPL 2024 vs 2025 Dashboard</h1>", unsafe_allow_html=True)

# --- Load Data
df24 = pd.read_csv("IPL24_All_Matches_Dataset_utf8.csv")
df25 = pd.read_csv("ipl_2025_deliveries.csv")

df24 = df24.rename(columns={
    "matchID": "match_id",
    "homeTeam": "batting_team",
    "batsmanName": "striker",
    "bowlerName": "bowler",
    "batsmanRuns": "runs_of_bat",
    "isWicket": "is_wicket"
    # NO 'bowling_team' in 2024 data!
})
df24["season"] = 2024
df25["season"] = 2025
for col in ["match_id","batting_team","bowling_team","striker","bowler","runs_of_bat","is_wicket"]:
    if col not in df24.columns:
        df24[col] = None
    if col not in df25.columns:
        df25[col] = None

# --- Sidebar Controls (Single, applies to both sections)
st.sidebar.markdown(f"<h3 style='color:{IPL_ACCENT};text-align:center;'>IPL Side-by-Side</h3>", unsafe_allow_html=True)
stat_type = st.sidebar.selectbox("Choose Stats Type", ["Batting", "Bowling"])

teams24 = sorted([x for x in df24['batting_team'].dropna().unique() if str(x).strip()])
teams25 = sorted([x for x in df25['batting_team'].dropna().unique() if str(x).strip()])

selected_team_24 = st.sidebar.selectbox("Team (2024)", ["All"] + teams24)
selected_team_25 = st.sidebar.selectbox("Team (2025)", ["All"] + teams25)

# ------------------- 2024 SECTION ----------------------
st.markdown("---")
st.markdown(f"<h2 style='color:{IPL_ACCENT};'>IPL 2024</h2>", unsafe_allow_html=True)
if stat_type == "Batting":
    df24_team = df24 if selected_team_24 == "All" else df24[df24["batting_team"] == selected_team_24]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Total Runs</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df24_team['runs_of_bat'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Matches</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df24_team['match_id'].nunique()}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df24_team.shape[0]}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Batters for {selected_team_24 if selected_team_24 != 'All' else 'All Teams'} (2024)</h3>", unsafe_allow_html=True)
    groupbat24 = df24_team.groupby("striker")["runs_of_bat"].sum().reset_index()
    topbat24 = groupbat24.nlargest(10, "runs_of_bat")
    fig24 = px.bar(topbat24, x="striker", y="runs_of_bat", text="runs_of_bat",
                   labels={"striker": "Batter", "runs_of_bat": "Runs"}, color="runs_of_bat", color_continuous_scale="Blues")
    fig24.update_traces(textposition='outside')
    st.plotly_chart(fig24, use_container_width=True)
else:
    st.markdown(f"<div style='padding:12px;color:orange;border-radius:7px;background:#fff3cd'>Only 'All Teams' bowling stats possible for IPL 2024 (no bowling team in data).</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Total Wickets</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df24['is_wicket'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df24.shape[0]}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Runs Conceded</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df24['runs_of_bat'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Bowlers (All Teams, 2024)</h3>", unsafe_allow_html=True)
    groupbowl24 = df24.groupby("bowler")["is_wicket"].sum().reset_index()
    topbowl24 = groupbowl24.nlargest(10, "is_wicket")
    fig24b = px.bar(topbowl24, x="bowler", y="is_wicket", text="is_wicket",
                   labels={"bowler": "Bowler", "is_wicket": "Wickets"}, color="is_wicket", color_continuous_scale="Blues")
    fig24b.update_traces(textposition='outside')
    st.plotly_chart(fig24b, use_container_width=True)

# ------------------- 2025 SECTION ----------------------
st.markdown("---")
st.markdown(f"<h2 style='color:{IPL_ACCENT};'>IPL 2025</h2>", unsafe_allow_html=True)
if stat_type == "Batting":
    df25_team = df25 if selected_team_25 == "All" else df25[df25["batting_team"] == selected_team_25]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Total Runs</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df25_team['runs_of_bat'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Matches</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df25_team['match_id'].nunique()}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BAT_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df25_team.shape[0]}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Batters for {selected_team_25 if selected_team_25 != 'All' else 'All Teams'} (2025)</h3>", unsafe_allow_html=True)
    groupbat25 = df25_team.groupby("striker")["runs_of_bat"].sum().reset_index()
    topbat25 = groupbat25.nlargest(10, "runs_of_bat")
    fig25 = px.bar(topbat25, x="striker", y="runs_of_bat", text="runs_of_bat",
                   labels={"striker": "Batter", "runs_of_bat": "Runs"}, color="runs_of_bat", color_continuous_scale="Oranges")
    fig25.update_traces(textposition='outside')
    st.plotly_chart(fig25, use_container_width=True)
else:
    df25_team = df25 if selected_team_25 == "All" else df25[df25["bowling_team"] == selected_team_25]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Total Wickets</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df25_team['is_wicket'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Balls</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{df25_team.shape[0]}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:{CARD_BG};padding:15px;border-radius:10px'><span style='font-size:22px;color:{BOWL_COLOR};'>Runs Conceded</span><br><span style='font-size:27px;font-weight:bold;color:{IPL_BLUE};'>{int(df25_team['runs_of_bat'].sum() or 0)}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Bowlers for {selected_team_25 if selected_team_25 != 'All' else 'All Teams'} (2025)</h3>", unsafe_allow_html=True)
    groupbowl25 = df25_team.groupby("bowler")["is_wicket"].sum().reset_index()
    topbowl25 = groupbowl25.nlargest(10, "is_wicket")
    fig25b = px.bar(topbowl25, x="bowler", y="is_wicket", text="is_wicket",
                   labels={"bowler": "Bowler", "is_wicket": "Wickets"}, color="is_wicket", color_continuous_scale="Oranges")
    fig25b.update_traces(textposition='outside')
    st.plotly_chart(fig25b, use_container_width=True)

st.markdown(f"""
<style>
.sidebar .sidebar-content {{background-color: {IPL_BLUE} !important; color: #fff;}}
.reportview-container, .main {{background: #181c25;}}
</style>
""", unsafe_allow_html=True)

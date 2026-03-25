import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────── THEME CONSTANTS ────────────────────────────
IPL_ACCENT  = "#FFB300"
IPL_BLUE    = "#172152"
BAT_COLOR   = "#eaf2fd"
BOWL_COLOR  = "#fdeaea"
CARD_BG     = "#f4f7fb"
DARK_BG     = "#181c25"
TEXT_COLOR  = "#FFFFFF"

st.set_page_config(
    page_title="IPL 2025 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
    <style>
        body, .reportview-container, .main {{
            background-color: {DARK_BG};
            color: {TEXT_COLOR};
            font-family: 'Inter', 'Segoe UI', Verdana, sans-serif;
        }}
        .sidebar .sidebar-content {{ background: {IPL_BLUE}; color: {TEXT_COLOR}; }}
        h1, h2, h3, h4 {{ font-weight: 900; }}
        .main-title {{
            color: {IPL_ACCENT} !important;
            text-align: center;
            font-size: 2.7rem;
            letter-spacing: 3px;
            margin-bottom: 0.5rem;
        }}
        hr {{ border-top: 2px solid {IPL_ACCENT}; margin: 1.3rem 0; }}
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
        .stat-card:hover {{ box-shadow: 0 8px 30px #FFB30033; }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏏 IPL 2025 Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr />", unsafe_allow_html=True)

# ──────────────────────────── LOAD DATA ─────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("ipl_2025_deliveries.csv")
    except Exception:
        st.error("❌ Could not load ipl_2025_deliveries.csv — make sure it's in the same folder.")
        st.stop()

    if "runs_of_bat" in df.columns:
        df = df.rename(columns={"runs_of_bat": "runs_off_bat"})

    if "wicket_type" not in df.columns:
        df["wicket_type"] = None
    if "is_wicket" not in df.columns:
        df["is_wicket"] = df["wicket_type"].notnull().astype(int)

    df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0)
    df["is_wicket"]    = pd.to_numeric(df["is_wicket"],    errors="coerce").fillna(0)
    return df

@st.cache_data
def build_player_team_map(df):
    bat_map  = df.groupby("striker")["batting_team"].agg(lambda x: x.mode()[0])
    bowl_map = df.groupby("bowler")["bowling_team"].agg(lambda x: x.mode()[0])
    combined = pd.concat([bat_map, bowl_map])
    return combined[~combined.index.duplicated(keep="first")].to_dict()

df = load_data()
player_team_map = build_player_team_map(df)

# ─────────────────────────── SIDEBAR ────────────────────────────────────
stat_type = st.sidebar.radio("Stats Section", ["Batting", "Bowling"], index=0)

all_teams     = sorted(set(df["batting_team"]) | set(df["bowling_team"]))
selected_team = st.sidebar.selectbox("Team", ["All"] + all_teams)

if selected_team == "All":
    all_players = sorted(set(df["striker"].dropna()) | set(df["bowler"].dropna()))
else:
    all_players = sorted([p for p, t in player_team_map.items() if t == selected_team])

selected_player = st.sidebar.selectbox("Player", ["All Players"] + all_players)

if selected_player != "All Players":
    opponent_teams   = sorted([t for t in all_teams if t != selected_team])
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Stats vs Opponent**")
    selected_opponent = st.sidebar.selectbox("Opponent Team", ["Select opponent..."] + opponent_teams)
else:
    selected_opponent = "Select opponent..."

# ────────────────────────── HELPERS ──────────────────────────────────────
def stat_card(label, value, icon, bg_color, col):
    col.markdown(f"""
        <div class="stat-card" style="background:{bg_color};">
            <div style="font-size:2.2rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:1.15rem; font-weight:600;">{label}</div>
            <div style="font-size:1.9rem; font-weight:500; margin-top:0.4rem;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def make_bar(series, x_label, y_label):
    fig = px.bar(
        series,
        x=series.index,
        y=series.values,
        text=series.values,
        labels={"x": x_label, "y": y_label},
        color=series.values,
        color_continuous_scale="Oranges",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_BG,
        font_color=TEXT_COLOR,
        margin=dict(t=40, b=40, l=40, r=40),
        coloraxis_showscale=False,
    )
    return fig

# ═══════════════════════════ PLAYER VIEW ════════════════════════════════
if selected_player != "All Players":
    batting_df = df[df["striker"] == selected_player]
    bowling_df = df[df["bowler"]  == selected_player]
    player_team = player_team_map.get(selected_player, selected_team)

    st.markdown(f"""
        <div style='background:{CARD_BG}; border-radius:20px; padding:1.1rem 1.8rem;
                    margin-bottom:4px; box-shadow:0 2px 8px rgba(16,32,80,0.13); width:65%;'>
            <span style='font-size:2rem;'>👤</span>
            <strong style='font-size:1.9rem; color:{IPL_ACCENT};'> {selected_player}</strong>
            <span style='font-size:1.1rem; color:#4a4c5b; margin-left:1.2rem;'>
                Team: <b>{player_team}</b> | Season: <b>2025</b>
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr />", unsafe_allow_html=True)

    # ── Overall Batting Stats ────────────────────────────────────────────
    st.markdown(f"<h2 style='color:{IPL_ACCENT}; margin-top:0;'>🏏 Batting Stats</h2>", unsafe_allow_html=True)
    runs_total   = int(batting_df["runs_off_bat"].sum())
    balls_total  = batting_df.shape[0]
    matches_bat  = batting_df["match_id"].nunique() if "match_id" in batting_df else "-"
    sr_total     = round((runs_total / balls_total) * 100, 2) if balls_total > 0 else 0
    fours_total  = int(batting_df[batting_df["runs_off_bat"] == 4].shape[0])
    sixes_total  = int(batting_df[batting_df["runs_off_bat"] == 6].shape[0])

    col1, col2, col3 = st.columns(3)
    stat_card("Total Runs",    runs_total,  "🏏", BAT_COLOR, col1)
    stat_card("Balls Faced",   balls_total, "🎯", BAT_COLOR, col2)
    stat_card("Strike Rate",   sr_total,    "📈", BAT_COLOR, col3)
    col4, col5, col6 = st.columns(3)
    stat_card("Fours",         fours_total,  "4️⃣", BAT_COLOR, col4)
    stat_card("Sixes",         sixes_total,  "6️⃣", BAT_COLOR, col5)
    stat_card("Matches Batted",matches_bat,  "📋", BAT_COLOR, col6)

    # ── Overall Bowling Stats ────────────────────────────────────────────
    st.markdown(f"<h2 style='color:{IPL_ACCENT};'>⚡ Bowling Stats</h2>", unsafe_allow_html=True)
    wkts_total   = int(bowling_df["is_wicket"].sum())
    bballs_total = bowling_df.shape[0]
    runs_con_tot = int(bowling_df["runs_off_bat"].sum())
    matches_bowl = bowling_df["match_id"].nunique() if "match_id" in bowling_df else "-"
    econ_total   = round((runs_con_tot / bballs_total) * 6, 2) if bballs_total > 0 else 0

    col7, col8, col9 = st.columns(3)
    stat_card("Total Wickets",  wkts_total,    "⚡", BOWL_COLOR, col7)
    stat_card("Balls Bowled",   bballs_total,  "🟠", BOWL_COLOR, col8)
    stat_card("Runs Conceded",  runs_con_tot,  "💸", BOWL_COLOR, col9)
    col10, col11, _ = st.columns(3)
    stat_card("Economy",        econ_total,    "📉", BOWL_COLOR, col10)
    stat_card("Matches Bowled", matches_bowl,  "📋", BOWL_COLOR, col11)

    # ── vs Opponent ──────────────────────────────────────────────────────
    if selected_opponent != "Select opponent...":
        st.markdown("<hr />", unsafe_allow_html=True)
        st.markdown(f"""
            <h2 style='color:{IPL_ACCENT};'>
                {selected_player} — {player_team} vs {selected_opponent}
            </h2>
        """, unsafe_allow_html=True)

        vs_bat  = df[(df["striker"] == selected_player) & (df["bowling_team"] == selected_opponent)]
        vs_bowl = df[(df["bowler"]  == selected_player) & (df["batting_team"] == selected_opponent)]

        # Batting vs opponent
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:0;'>🏏 Batting vs {selected_opponent}</h3>",
                    unsafe_allow_html=True)
        if vs_bat.shape[0] > 0:
            runs    = int(vs_bat["runs_off_bat"].sum())
            balls   = vs_bat.shape[0]
            matches = vs_bat["match_id"].nunique() if "match_id" in vs_bat else "-"
            sr      = round((runs / balls) * 100, 2) if balls > 0 else 0
            fours   = int(vs_bat[vs_bat["runs_off_bat"] == 4].shape[0])
            sixes   = int(vs_bat[vs_bat["runs_off_bat"] == 6].shape[0])
            col1, col2, col3 = st.columns(3)
            stat_card("Runs",        runs,    "🏏", BAT_COLOR, col1)
            stat_card("Balls Faced", balls,   "🎯", BAT_COLOR, col2)
            stat_card("Strike Rate", sr,      "📈", BAT_COLOR, col3)
            col4, col5, col6 = st.columns(3)
            stat_card("Fours",       fours,   "4️⃣", BAT_COLOR, col4)
            stat_card("Sixes",       sixes,   "6️⃣", BAT_COLOR, col5)
            stat_card("Matches",     matches, "📋", BAT_COLOR, col6)
        else:
            st.info(f"No batting data for {selected_player} vs {selected_opponent}.")

        # Bowling vs opponent
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>⚡ Bowling vs {selected_opponent}</h3>",
                    unsafe_allow_html=True)
        if vs_bowl.shape[0] > 0:
            wickets   = int(vs_bowl["is_wicket"].sum())
            balls_b   = vs_bowl.shape[0]
            runs_con  = int(vs_bowl["runs_off_bat"].sum())
            matches_b = vs_bowl["match_id"].nunique() if "match_id" in vs_bowl else "-"
            economy   = round((runs_con / balls_b) * 6, 2) if balls_b > 0 else 0
            col7, col8, col9 = st.columns(3)
            stat_card("Wickets",       wickets,   "⚡", BOWL_COLOR, col7)
            stat_card("Runs Conceded", runs_con,  "💸", BOWL_COLOR, col8)
            stat_card("Economy",       economy,   "📉", BOWL_COLOR, col9)
            col10, col11, _ = st.columns(3)
            stat_card("Balls Bowled",  balls_b,   "🟠", BOWL_COLOR, col10)
            stat_card("Matches",       matches_b, "📋", BOWL_COLOR, col11)
        else:
            st.info(f"No bowling data for {selected_player} vs {selected_opponent}.")

    st.markdown("<hr />", unsafe_allow_html=True)
    with st.expander(f"Preview Batting Data — {selected_player}"):
        st.dataframe(batting_df.head(20), use_container_width=True)
    with st.expander(f"Preview Bowling Data — {selected_player}"):
        st.dataframe(bowling_df.head(20), use_container_width=True)

# ═══════════════════════ TEAM / OVERALL VIEW ════════════════════════════
else:
    team_col = "batting_team" if stat_type == "Batting" else "bowling_team"
    filtered = df if selected_team == "All" else df[df[team_col] == selected_team]
    team_lbl = selected_team if selected_team != "All" else "All Teams"

    col1, col2, col3 = st.columns(3)
    if stat_type == "Batting":
        stat_card("Total Runs",     int(filtered["runs_off_bat"].sum()),                              "🏏", BAT_COLOR, col1)
        stat_card("Unique Matches", filtered["match_id"].nunique() if "match_id" in filtered else "-","📋", BAT_COLOR, col2)
        stat_card("Total Balls",    len(filtered),                                                    "🎯", BAT_COLOR, col3)

        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Batters — {team_lbl}</h3>",
                    unsafe_allow_html=True)
        topbat = filtered.groupby("striker")["runs_off_bat"].sum().sort_values(ascending=False).head(10)
        if not topbat.empty:
            st.plotly_chart(make_bar(topbat, "Batter", "Runs"), use_container_width=True)
        else:
            st.warning("No batting data for the selected options.")

    else:
        stat_card("Total Wickets",  int(filtered["is_wicket"].sum()),    "⚡", BOWL_COLOR, col1)
        stat_card("Total Balls",    len(filtered),                        "🟠", BOWL_COLOR, col2)
        stat_card("Runs Conceded",  int(filtered["runs_off_bat"].sum()), "💸", BOWL_COLOR, col3)

        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers — {team_lbl}</h3>",
                    unsafe_allow_html=True)
        topbowl = filtered.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
        if not topbowl.empty:
            st.plotly_chart(make_bar(topbowl, "Bowler", "Wickets"), use_container_width=True)
        else:
            st.warning("No bowling data for the selected options.")

    if selected_team != "All":
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers vs {selected_team}</h3>",
                    unsafe_allow_html=True)
        bowlers_against = (
            df[df["batting_team"] == selected_team]
            .groupby("bowler")["is_wicket"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if not bowlers_against.empty:
            st.plotly_chart(make_bar(bowlers_against, "Bowler", "Wickets"), use_container_width=True)
        else:
            st.warning("No bowling data for the selected team.")

    st.markdown("<hr />", unsafe_allow_html=True)
    with st.expander("Preview Data"):
        st.dataframe(filtered.head(30), use_container_width=True)
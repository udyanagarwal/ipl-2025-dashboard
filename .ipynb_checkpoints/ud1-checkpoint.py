import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────── THEME CONSTANTS ────────────────────────────
IPL_BLUE    = "#172152"
IPL_ACCENT  = "#FFB300"
BAT_COLOR   = "#eaf2fd"
BOWL_COLOR  = "#fdeaea"
CARD_BG     = "#f4f7fb"
DARK_BG     = "#181c25"
TEXT_COLOR  = "#FFFFFF"

st.set_page_config(
    page_title="IPL 2021 vs 2025 Dashboard",
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

st.markdown("<h1 class='main-title'>🏏 IPL 2021 vs 2025 Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr />", unsafe_allow_html=True)

# ─────────────────────── TEAM NAME NORMALIZER ───────────────────────────
# Maps every full/alternate name found in the 2021 dataset → short code
TEAM_MAP = {
    "Mumbai Indians":                  "MI",
    "Chennai Super Kings":             "CSK",
    "Royal Challengers Bangalore":     "RCB",
    "Royal Challengers Bengaluru":     "RCB",
    "Kolkata Knight Riders":           "KKR",
    "Sunrisers Hyderabad":             "SRH",
    "Delhi Capitals":                  "DC",
    "Punjab Kings":                    "PBKS",
    "Kings XI Punjab":                 "PBKS",
    "Rajasthan Royals":                "RR",
    "Gujarat Titans":                  "GT",
    "Lucknow Super Giants":            "LSG",
    # short codes pass through unchanged
    "MI": "MI", "CSK": "CSK", "RCB": "RCB", "KKR": "KKR",
    "SRH": "SRH", "DC": "DC", "PBKS": "PBKS", "RR": "RR",
    "GT": "GT", "LSG": "LSG",
}

def normalize_teams(df):
    df["batting_team"]  = df["batting_team"].map(lambda x: TEAM_MAP.get(x, x))
    df["bowling_team"]  = df["bowling_team"].map(lambda x: TEAM_MAP.get(x, x))
    return df

# ──────────────────────────── LOAD DATA ─────────────────────────────────
@st.cache_data
def load_data():
    try:
        df25 = pd.read_csv("ipl_2025_deliveries.csv")
    except Exception:
        st.error("❌ Could not load ipl_2025_deliveries.csv — make sure the file is in the same folder.")
        st.stop()

    try:
        df21 = pd.read_csv("IPL_ball_by_ball_updated.csv")
    except Exception:
        st.error("❌ Could not load IPL_ball_by_ball_updated.csv — make sure the file is in the same folder.")
        st.stop()

    # ── Standardize column names ──────────────────────────────────────────
    if "runs_of_bat" in df25.columns:
        df25 = df25.rename(columns={"runs_of_bat": "runs_off_bat"})

    rename_21 = {}
    if "batting_name" in df21.columns: rename_21["batting_name"] = "batting_team"
    if "bowling_name" in df21.columns: rename_21["bowling_name"] = "bowling_team"
    if "runs_of_bat"  in df21.columns: rename_21["runs_of_bat"]  = "runs_off_bat"
    if rename_21:
        df21 = df21.rename(columns=rename_21)

    # ── Filter 2021 season ────────────────────────────────────────────────
    if "season" in df21.columns:
        df21 = df21[df21["season"] == 2021].copy()
    df25["season"] = 2025

    # ── Normalize team names ──────────────────────────────────────────────
    df25 = normalize_teams(df25)
    df21 = normalize_teams(df21)

    # ── Ensure required columns exist ─────────────────────────────────────
    for df in [df25, df21]:
        if "wicket_type" not in df.columns:
            df["wicket_type"] = None
        if "is_wicket" not in df.columns:
            df["is_wicket"] = df["wicket_type"].notnull().astype(int)
        df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0)
        df["is_wicket"]    = pd.to_numeric(df["is_wicket"],    errors="coerce").fillna(0)

    return df21, df25

def build_player_team_map(df):
    """Map each player to their primary team using striker→batting_team and bowler→bowling_team."""
    bat_map  = df.groupby("striker")["batting_team"].agg(lambda x: x.mode()[0])
    bowl_map = df.groupby("bowler")["bowling_team"].agg(lambda x: x.mode()[0])
    combined = pd.concat([bat_map, bowl_map])
    # if a player appears in both, keep batting_team (more reliable)
    return combined[~combined.index.duplicated(keep="first")].to_dict()

df21, df25 = load_data()
player_team_25 = build_player_team_map(df25)
player_team_21 = build_player_team_map(df21)

# ─────────────────────────── SIDEBAR ────────────────────────────────────
year_opts = ["2021", "2025", "Both"]
opt_year  = st.sidebar.selectbox("Select Year Section", year_opts)
stat_type = st.sidebar.radio("Stats Section", ["Batting", "Bowling"], index=0)

# Build team list from whichever dataset(s) are active
if opt_year == "Both":
    all_teams = sorted(set(df21["batting_team"]) | set(df21["bowling_team"]) |
                       set(df25["batting_team"]) | set(df25["bowling_team"]))
else:
    df_active = df21 if opt_year == "2021" else df25
    all_teams = sorted(set(df_active["batting_team"]) | set(df_active["bowling_team"]))

selected_team = st.sidebar.selectbox("Team", ["All"] + all_teams)

if opt_year != "Both":
    df_active       = df21 if opt_year == "2021" else df25
    player_team_map = player_team_21 if opt_year == "2021" else player_team_25

    if selected_team == "All":
        all_players = sorted(
            set(df_active["striker"].dropna()) | set(df_active["bowler"].dropna())
        )
    else:
        # Only show players whose primary team matches selected_team
        all_players = sorted([p for p, t in player_team_map.items() if t == selected_team])

    selected_player = st.sidebar.selectbox("Player", ["All Players"] + all_players)

    # Opponent team selector — only shown when a specific player is selected
    if selected_player != "All Players":
        opponent_teams = sorted([t for t in all_teams if t != selected_team])
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Stats vs Opponent**")
        selected_opponent = st.sidebar.selectbox("Opponent Team", ["Select opponent..."] + opponent_teams)
    else:
        selected_opponent = "Select opponent..."

coltheme = "Blues" if opt_year == "2021" else "Oranges"

# ────────────────────────── HELPER: STAT CARD ────────────────────────────
def stat_card(label, value, icon, bg_color, col):
    col.markdown(f"""
        <div class="stat-card" style="background:{bg_color};">
            <div style="font-size:2.2rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:1.15rem; font-weight:600;">{label}</div>
            <div style="font-size:1.9rem; font-weight:500; margin-top:0.4rem;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def make_bar(series, x_label, y_label, theme):
    fig = px.bar(
        series,
        x=series.index,
        y=series.values,
        text=series.values,
        labels={"x": x_label, "y": y_label},
        color=series.values,
        color_continuous_scale=theme,
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

# ═══════════════════════════ BOTH YEARS ════════════════════════════════
if opt_year == "Both":
    st.markdown(f"<h2 style='color:{IPL_ACCENT};margin-top:1.3rem;'>Year-on-Year Comparison: IPL 2021 vs 2025</h2>",
                unsafe_allow_html=True)

    runs_21     = int(df21["runs_off_bat"].sum())
    runs_25     = int(df25["runs_off_bat"].sum())
    wickets_21  = int(df21["is_wicket"].sum())
    wickets_25  = int(df25["is_wicket"].sum())
    balls_21    = len(df21)
    balls_25    = len(df25)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Runs — 2021 / 2025",    f"{runs_21:,}",    f"{runs_25:,}")
    col2.metric("Total Wickets — 2021 / 2025", f"{wickets_21:,}", f"{wickets_25:,}")
    col3.metric("Total Balls — 2021 / 2025",   f"{balls_21:,}",   f"{balls_25:,}")

    df_compare = pd.DataFrame({
        "Year":    ["2021", "2025"],
        "Runs":    [runs_21, runs_25],
        "Wickets": [wickets_21, wickets_25],
        "Balls":   [balls_21, balls_25],
    })
    compare_opt = st.selectbox("Select Metric for Chart", ["Runs", "Wickets", "Balls"])
    fig = px.bar(
        df_compare, x="Year", y=compare_opt, text=compare_opt, color="Year",
        color_discrete_map={"2021": "#2962ff", "2025": "#FFB300"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font_color=TEXT_COLOR)
    st.plotly_chart(fig, use_container_width=True)

    if selected_team != "All":
        st.markdown(f"<h3 style='color:{IPL_ACCENT};'>Top 10 Bowlers vs {selected_team} (2021 & 2025 Combined)</h3>",
                    unsafe_allow_html=True)
        both_df = pd.concat([df21, df25])
        bowlers_vs = (
            both_df[both_df["batting_team"] == selected_team]
            .groupby("bowler")["is_wicket"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if not bowlers_vs.empty:
            st.plotly_chart(make_bar(bowlers_vs, "Bowler", "Wickets", "Oranges"), use_container_width=True)
        else:
            st.warning("No bowling data for the selected team across both years.")

    st.markdown("<hr />", unsafe_allow_html=True)

# ═══════════════════════ SINGLE YEAR (2021 / 2025) ══════════════════════
else:
    df = df21 if opt_year == "2021" else df25
    year_label = opt_year

    # ── PLAYER VIEW ──────────────────────────────────────────────────────
    if selected_player != "All Players":
        batting_df = df[df["striker"] == selected_player]
        bowling_df = df[df["bowler"]  == selected_player]

        st.markdown(f"""
            <div style='background:{CARD_BG}; border-radius:20px; padding:1.1rem 1.8rem;
                        margin-bottom:4px; box-shadow:0 2px 8px rgba(16,32,80,0.13); width:65%;'>
                <span style='font-size:2rem;'>👤</span>
                <strong style='font-size:1.9rem; color:{IPL_ACCENT};'> {selected_player}</strong>
                <span style='font-size:1.1rem; color:#4a4c5b; margin-left:1.2rem;'>
                    Team: <b>{selected_team}</b> | Season: <b>{year_label}</b>
                </span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr />", unsafe_allow_html=True)

        st.markdown(f"<h2 style='color:{IPL_ACCENT}; margin-top:0;'>Batting Stats</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        stat_card("Total Runs",     int(batting_df["runs_off_bat"].sum()), "🏏", BAT_COLOR, col1)
        stat_card("Balls Faced",    batting_df.shape[0],                   "🎯", BAT_COLOR, col2)
        stat_card("Matches Batted",
                  batting_df["match_id"].nunique() if "match_id" in batting_df else "-",
                  "📋", BAT_COLOR, col3)

        st.markdown(f"<h2 style='color:{IPL_ACCENT};'>Bowling Stats</h2>", unsafe_allow_html=True)
        col4, col5, col6 = st.columns(3)
        stat_card("Total Wickets",   int(bowling_df["is_wicket"].sum()),     "⚡", BOWL_COLOR, col4)
        stat_card("Balls Bowled",    bowling_df.shape[0],                    "🟠", BOWL_COLOR, col5)
        stat_card("Runs Conceded",   int(bowling_df["runs_off_bat"].sum()),  "💸", BOWL_COLOR, col6)

        # ── vs opponent team ─────────────────────────────────────────────
        if selected_opponent != "Select opponent...":
            st.markdown("<hr />", unsafe_allow_html=True)
            st.markdown(f"""
                <h2 style='color:{IPL_ACCENT};'>
                    {selected_player} — {selected_team} vs {selected_opponent}
                </h2>
            """, unsafe_allow_html=True)

            vs_bat  = df[(df["striker"] == selected_player) & (df["bowling_team"] == selected_opponent)]
            vs_bowl = df[(df["bowler"]  == selected_player) & (df["batting_team"] == selected_opponent)]

            # batting vs opponent
            st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:0;'>🏏 Batting vs {selected_opponent}</h3>", unsafe_allow_html=True)
            if vs_bat.shape[0] > 0:
                runs       = int(vs_bat["runs_off_bat"].sum())
                balls      = vs_bat.shape[0]
                matches    = vs_bat["match_id"].nunique() if "match_id" in vs_bat else "-"
                strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0
                fours      = int(vs_bat[vs_bat["runs_off_bat"] == 4].shape[0])
                sixes      = int(vs_bat[vs_bat["runs_off_bat"] == 6].shape[0])
                col1, col2, col3 = st.columns(3)
                stat_card("Runs",        runs,        "🏏", BAT_COLOR, col1)
                stat_card("Balls Faced", balls,       "🎯", BAT_COLOR, col2)
                stat_card("Strike Rate", strike_rate, "📈", BAT_COLOR, col3)
                col4, col5, col6 = st.columns(3)
                stat_card("Fours",   fours,   "4️⃣",  BAT_COLOR, col4)
                stat_card("Sixes",   sixes,   "6️⃣",  BAT_COLOR, col5)
                stat_card("Matches", matches, "📋", BAT_COLOR, col6)
            else:
                st.info(f"No batting data for {selected_player} vs {selected_opponent}.")

            # bowling vs opponent
            st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>⚡ Bowling vs {selected_opponent}</h3>", unsafe_allow_html=True)
            if vs_bowl.shape[0] > 0:
                wickets    = int(vs_bowl["is_wicket"].sum())
                balls_bowl = vs_bowl.shape[0]
                runs_con   = int(vs_bowl["runs_off_bat"].sum())
                matches_b  = vs_bowl["match_id"].nunique() if "match_id" in vs_bowl else "-"
                economy    = round((runs_con / balls_bowl) * 6, 2) if balls_bowl > 0 else 0
                col7, col8, col9 = st.columns(3)
                stat_card("Wickets",       wickets,    "⚡", BOWL_COLOR, col7)
                stat_card("Runs Conceded", runs_con,   "💸", BOWL_COLOR, col8)
                stat_card("Economy",       economy,    "📉", BOWL_COLOR, col9)
                col10, col11, _ = st.columns(3)
                stat_card("Balls Bowled",  balls_bowl, "🟠", BOWL_COLOR, col10)
                stat_card("Matches",       matches_b,  "📋", BOWL_COLOR, col11)
            else:
                st.info(f"No bowling data for {selected_player} vs {selected_opponent}.")

        st.markdown("<hr />", unsafe_allow_html=True)
        with st.expander(f"Preview Batting Data ({selected_player}, {year_label})"):
            st.dataframe(batting_df.head(20), use_container_width=True)
        with st.expander(f"Preview Bowling Data ({selected_player}, {year_label})"):
            st.dataframe(bowling_df.head(20), use_container_width=True)

    # ── TEAM / OVERALL VIEW ───────────────────────────────────────────────
    else:
        team_col = "batting_team" if stat_type == "Batting" else "bowling_team"
        filtered = df if selected_team == "All" else df[df[team_col] == selected_team]
        team_lbl = selected_team if selected_team != "All" else "All Teams"

        col1, col2, col3 = st.columns(3)
        if stat_type == "Batting":
            stat_card("Total Runs",     int(filtered["runs_off_bat"].sum()),                           "🏏", BAT_COLOR,  col1)
            stat_card("Unique Matches", filtered["match_id"].nunique() if "match_id" in filtered else "-", "📋", BAT_COLOR, col2)
            stat_card("Total Balls",    len(filtered),                                                  "🎯", BAT_COLOR,  col3)

            st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Batters — {team_lbl} ({year_label})</h3>",
                        unsafe_allow_html=True)
            topbat = filtered.groupby("striker")["runs_off_bat"].sum().sort_values(ascending=False).head(10)
            if not topbat.empty:
                st.plotly_chart(make_bar(topbat, "Batter", "Runs", coltheme), use_container_width=True)
            else:
                st.warning("No batting data for the selected options.")

        else:  # Bowling
            stat_card("Total Wickets",  int(filtered["is_wicket"].sum()),     "⚡", BOWL_COLOR, col1)
            stat_card("Total Balls",    len(filtered),                         "🟠", BOWL_COLOR, col2)
            stat_card("Runs Conceded",  int(filtered["runs_off_bat"].sum()),  "💸", BOWL_COLOR, col3)

            st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers — {team_lbl} ({year_label})</h3>",
                        unsafe_allow_html=True)
            topbowl = filtered.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
            if not topbowl.empty:
                st.plotly_chart(make_bar(topbowl, "Bowler", "Wickets", coltheme), use_container_width=True)
            else:
                st.warning("No bowling data for the selected options.")

        # Top 10 bowlers vs selected team
        if selected_team != "All":
            st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers vs {selected_team} ({year_label})</h3>",
                        unsafe_allow_html=True)
            bowlers_against = (
                df[df["batting_team"] == selected_team]
                .groupby("bowler")["is_wicket"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            if not bowlers_against.empty:
                st.plotly_chart(make_bar(bowlers_against, "Bowler", "Wickets", coltheme), use_container_width=True)
            else:
                st.warning("No bowling data for the selected team.")

        st.markdown("<hr />", unsafe_allow_html=True)
        with st.expander(f"Preview {year_label} Data"):
            st.dataframe(filtered.head(30), use_container_width=True)
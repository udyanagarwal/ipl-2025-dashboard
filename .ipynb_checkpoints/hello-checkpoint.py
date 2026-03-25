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

st.set_page_config(page_title="IPL 2021 vs 2025 Dashboard", layout="wide")
st.markdown(f"""<style>
body, .reportview-container, .main {{background-color:{DARK_BG};color:{TEXT_COLOR};font-family:'Inter', 'Segoe UI', Verdana, sans-serif;}}
.sidebar .sidebar-content {{background: {IPL_BLUE};color:{TEXT_COLOR};}}
h1, h2, h3, h4 {{font-weight:900;}}
.main-title {{color:{IPL_ACCENT} !important;text-align:center;font-size:2.7rem;letter-spacing:3px;margin-bottom:0.5rem;}}
hr {{border-top:2px solid {IPL_ACCENT};margin:1.3rem 0;}}
.stat-card {{background:{CARD_BG};border-radius:16px;padding:1.6rem 1.2rem;margin-bottom:17px;box-shadow:0 4px 18px rgba(0,0,0,0.12);color:{IPL_BLUE};text-align:center;font-weight:700;}}
.stat-card:hover {{box-shadow:0 8px 30px #FFB30033;}}
.css-1aumxhk {{background-color:{CARD_BG};}}
</style>""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏏 IPL 2021 vs 2025 Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr />", unsafe_allow_html=True)

# Load Data
df25 = pd.read_csv("ipl_2025_deliveries.csv")
df21 = pd.read_csv("IPL_ball_by_ball_updated.csv")
df25 = df25.rename(columns={"batting_name":"batting_team", "bowling_team":"bowling_team", "runs_of_bat":"runs_off_bat"})
df21 = df21.rename(columns={"batting_name":"batting_team", "bowling_name":"bowling_team", "runs_off_bat":"runs_off_bat"})
for df in [df25, df21]:
    if "wicket_type" not in df.columns: df["wicket_type"] = None
    df["is_wicket"] = df["wicket_type"].notnull().astype(int)
    df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0)
    df["is_wicket"] = pd.to_numeric(df["is_wicket"], errors="coerce").fillna(0)
if "season" in df21.columns: df21 = df21[df21['season'] == 2021].copy()
df25['season'] = 2025

year_opts = ["2021", "2025", "Both"]
opt_year = st.sidebar.selectbox("Select Year Section", year_opts)
stat_type = st.sidebar.radio("Stats Section", ["Batting", "Bowling"], index=0)

if opt_year in ["2021", "2025"]:
    # Regular per-year logic (unchanged)
    df = df21 if opt_year == "2021" else df25
    teams = sorted(set(pd.concat([df['batting_team'], df['bowling_team']]).dropna().unique()))
    players = sorted(set(df['striker'].dropna().unique()).union(df['bowler'].dropna().unique()))
    team_label = f"Team ({opt_year})"
    player_label = f"Player ({opt_year})"
    coltheme = "Blues" if opt_year == "2021" else "Oranges"
    year_label = opt_year
    selected_team = st.sidebar.selectbox(team_label, ["All"] + teams)
    selected_player = st.sidebar.selectbox(player_label, ["All Players"] + players)
    
    def stat_card(label, value, icon, bg_color, col):
        col.markdown(f"""<div class="stat-card" style="background:{bg_color};">
        <div style="font-size:2.2rem; margin-bottom:0.5rem;">{icon}</div>
        <div style="font-size:1.15rem; font-weight:600;">{label}</div>
        <div style="font-size:1.9rem; font-weight:500; margin-top:0.4rem;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    # Per-year blocks, cards, top 10 batters/bowlers, per-team logic unchanged etc.
    # ... Your existing dashboard code for player, team, stats, visuals goes here ...
    # Example: show top 10 bowlers vs selected team in that year
    if selected_team != "All":
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers vs {selected_team} ({year_label})</h3>", unsafe_allow_html=True)
        filter_df = df[df["batting_team"] == selected_team]
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

elif opt_year == "Both":
    # ONLY show combined features/comparisons in "Both" tab
    teams = sorted(set(pd.concat([df21['batting_team'], df21['bowling_team'],
                                 df25['batting_team'], df25['bowling_team']]).dropna().unique()))
    selected_team = st.sidebar.selectbox("Team (Both Years)", ["All"] + teams)
    runs_2021 = int(df21['runs_off_bat'].sum())
    runs_2025 = int(df25['runs_off_bat'].sum())
    wickets_2021 = int(df21['is_wicket'].sum())
    wickets_2025 = int(df25['is_wicket'].sum())
    balls_2021 = len(df21)
    balls_2025 = len(df25)
    # Cards Compare
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Runs: 2021 ➔ 2025", f"{runs_2021:,}", f"{runs_2025:,}")
    c2.metric("Total Wickets: 2021 ➔ 2025", f"{wickets_2021:,}", f"{wickets_2025:,}")
    c3.metric("Total Balls: 2021 ➔ 2025", f"{balls_2021:,}", f"{balls_2025:,}")
    # Year-on-year bar chart
    df_compare = pd.DataFrame({
        "Year": ["2021", "2025"],
        "Runs": [runs_2021, runs_2025],
        "Wickets": [wickets_2021, wickets_2025],
        "Balls": [balls_2021, balls_2025]
    })
    metric = st.selectbox("Select Metric to Compare", ["Runs", "Wickets", "Balls"])
    fig = px.bar(df_compare, x="Year", y=metric, text=metric, color="Year",
        color_discrete_map={"2021": "#1976d2", "2025": "#FFB300"},
        labels={'Year': 'IPL Year', metric: f'Total {metric}'})
    fig.update_traces(textposition='outside')
    fig.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font_color=TEXT_COLOR)
    st.plotly_chart(fig, use_container_width=True)
    # Top 10 bowlers vs team (combined years)
    if selected_team != "All":
        st.markdown(f"<h3 style='color:{IPL_ACCENT}; margin-top:1rem;'>Top 10 Bowlers vs {selected_team} (2021+2025 Combined)</h3>", unsafe_allow_html=True)
        both_df = pd.concat([df21, df25])
        bowlers_vs_team = both_df[both_df["batting_team"] == selected_team].groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
        if not bowlers_vs_team.empty:
            fig_both = px.bar(
                bowlers_vs_team,
                y=bowlers_vs_team.values,
                x=bowlers_vs_team.index,
                text=bowlers_vs_team.values,
                labels={"x": "Bowler", "y": "Wickets"},
                color=bowlers_vs_team.values,
                color_continuous_scale="Oranges",
            )
            fig_both.update_traces(textposition="outside")
            fig_both.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
                                  font_color=TEXT_COLOR, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig_both, use_container_width=True)
        else:
            st.warning("No bowling data available for the selected team across both years.")
    st.markdown("<hr />", unsafe_allow_html=True)

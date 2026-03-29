# 🏏 IPL 2025 Analytics Dashboard

An interactive cricket analytics dashboard built with Python, Streamlit, and Plotly — analyzing ball-by-ball IPL 2025 data across 10 teams, 200+ players, and 74 matches.

🔗 **[Live Demo → ud-ipl-2025.streamlit.app](https://ud-ipl-2025.streamlit.app)**

---

## 📊 Features

### Player Analytics
- Batting stats — Runs, Strike Rate, Batting Average, Fours, Sixes, Dot Ball %
- Bowling stats — Wickets, Economy, Bowling Average, Bowling SR, Dot Ball %
- Head-to-head stats against any opponent team

### Team & Overall Analytics
- Top 10 batters and bowlers for any team
- Top 10 bowlers vs a selected team

### Phase-wise Analysis
- Performance breakdown across Group Stage, Qualifier 1, Eliminator, Qualifier 2 and Final
- Switchable metrics — Runs, Wickets, Run Rate

### Powerplay / Middle / Death Overs
- Run rate comparison across all 3 over phases
- Runs per over line chart across all 20 overs

### 🤖 ML Score Predictor
- Predicts a batter's likely runs in the next match using Linear Regression
- Match-by-match performance chart with 3-match rolling average and trend line
- Model RMSE displayed for transparency

---

## 🛠️ Tech Stack

| Tool | Usage |
|---|---|
| Python | Core language |
| Streamlit | Web app framework |
| Pandas | Data processing & aggregation |
| Plotly | Interactive visualizations |
| Scikit-learn | Linear Regression ML model |
| NumPy | Numerical computations |

---

## 📁 Dataset

- `ipl_2025_deliveries.csv` — Ball-by-ball data for IPL 2025
- 50,000+ delivery records across 74 matches
- Columns: match_id, date, venue, batting_team, bowling_team, striker, bowler, runs_of_bat, extras, wicket_type, is_wicket, phase, over, and more

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/udyanagarwal/ipl-2025-dashboard.git
cd ipl-2025-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run ipl_2025_dashboard.py
```

---

## 📌 Key Insights from the Data

- **Death overs (16-20)** have the highest run rate at **9.94** across IPL 2025
- **Powerplay run rate** is 8.78 — teams are aggressive from ball one
- Top run scorer: **Sai Sudharsan** with 759 runs at a consistent average

---

## 👤 Author

**Udyan Agarwal**
- 📧 agarwaludyan2005@gmail.com
- 🔗 [GitHub](https://github.com/udyanagarwal)
- 🎓 Computer Engineering, Bharati Vidyapeeth College of Engineering, Pune (2023–2027)

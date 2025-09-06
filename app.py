import streamlit as st
import pandas as pd
import base64
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Rose Lavelle in 2022",
    page_icon="⚽",
    layout="wide"
)

st.title("Rose Lavelle for :blue[Seattle Reign]")
st.write("How did she perform for the :blue-background[Seattle Reign] in 2022?")

@st.cache_data
def load_data():
    match_log = pd.read_csv("data/rose_match_data.csv")
    profile = pd.read_csv("data/rose_player_profile.csv")
    season_stats = pd.read_csv("data/player_season_stats.csv")
    return match_log, profile, season_stats

match_log, profile, season_stats = load_data()

### Player Profile ##
# --- Get Rose's info directly from the CSV
row = profile.iloc[0]
photo_path = "rose_lavelle_photo.png"
name = row.get("player_short_first_name", "") + " " + row.get("player_last_name", "")
team = "Seattle Reign"  # hardcode if not in CSV
country = row.get("player_nationality", "Unknown")
pos = row.get("player_position")

with open(photo_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
photo_src = f"data:image/png;base64,{b64}"

# Layout: make card in a narrow column
left_col, right_col = st.columns([1, 3])  # 1/5 width for card

with left_col:
    st.markdown(
    f"""
    <div style="
        background: linear-gradient(180deg, #111827 0%, #0b1220 100%);
        border-radius: 20px;
        padding: 24px 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.5);
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    ">
        <img src="{photo_src}" style="
            width: auto;
            height: auto;
            border-radius: 2%;
            border: 1px solid #fff;
            display: block;      /* allow margin auto centering */
            margin: 4px auto 14px auto;
        ">
        <p style="color:#fff; font-size:22px; font-weight:700; margin:0;">{name}</p>    
        <p style="color:#22d3ee; margin:0 0 6px 0; font-size:16px;">
            {team}
        </p>
        <p style="color:#94a3b8; font-size:13px; margin:0;">
            {country} • {pos}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with right_col:
    season = season_stats.iloc[0]
    st.header("**Season Summary**")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        st.metric("**Appearances**", len(match_log)-1, delta="+6", border = True)

        passes_diff = season.get("passes_total") - 497
        st.metric("**Completed Passes**", season.get("passes_total"), delta = f"{passes_diff:+}", border = True)
    with c2: 
        st.metric("**Game Starts**", season.get("starts"), delta = "+6", border = True) 

        duels_diff = season.get("duels_won") - 79
        st.metric("**Duels Won**", season.get("duels_won"), delta = f"{duels_diff:+}", border = True)
    with c3: 
        minutes_diff = season.get("minutes") - 1026
        st.metric("**Minutes Played**", season.get("minutes"), delta = f"{minutes_diff:+} minutes",border = True) 

        recoveries_diff = season.get("recoveries") - 70
        st.metric("**Recoveries**", season.get("recoveries"), delta =f"{recoveries_diff:+}", border = True)  
    with c4: 
        st.metric("**Goals**",season.get("goals"), delta="+4", border = True)


        shots_diff = season.get("shots_total") - 29
        st.metric("**Total Shots**", season.get("shots_total"), delta = f"{shots_diff:+}", border = True)
        
    with c5: 
        st.metric("**Assists**", season.get("assists"), delta=0, delta_color="off", border = True)
        
        targetshots_diff = season.get("shots_on_target") - 11
        st.metric("**Shots on Target**", season.get("shots_on_target"), delta = f"{targetshots_diff:+}", border = True)

st.header("Rose Lavelle's Game Precision")
# Prepare data
df = match_log.copy()
df["date"] = df["match_id"].str.extract(r"(\d{4}-\d{2}-\d{2})")
df = df.sort_values("date")

SHOTS_COL = "shots_total"
SOT_COL = "shots_on_target"

# Calculate shot accuracy %
df["shot_accuracy_pct"] = np.where(
    df[SHOTS_COL] > 0, (df[SOT_COL] / df[SHOTS_COL]) * 100, np.nan
)

# Create subplots with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Bar: Total Shots
fig.add_trace(
    go.Bar(
        x=df["date"],
        y=df[SHOTS_COL],
        name="Shots",
        marker_color="#00429d",  # blue
        hovertemplate="%{x|%b %d, %Y}<br>Shots: %{y}<extra></extra>",
    ),
    secondary_y=False,
)

# Bar: Shots on Target
fig.add_trace(
    go.Bar(
        x=df["date"],
        y=df[SOT_COL],
        name="Shots on Target",
        marker_color="#22d3ee",  # cyan
        hovertemplate="%{x|%b %d, %Y}<br>SOT: %{y}<extra></extra>",
    ),
    secondary_y=False,
)

# Line: Shot Accuracy %
fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["shot_accuracy_pct"],
        mode="lines+markers",
        name="Shot Accuracy %",
        line=dict(color="#e15759", width=3),
        marker=dict(size=8),
        hovertemplate="%{x|%b %d, %Y}<br>Accuracy: %{y:.1f}%<extra></extra>",
    ),
    secondary_y=True,
)

# Layout styling
fig.update_layout(
    template="plotly_dark",
    title="Shots vs Shots on Target + Accuracy %",

    barmode="group",
    height=450,
    legend=dict(title="", orientation="h", yanchor = "bottom", y=-0.2, xanchor="center", x=0.5),
    margin=dict(l=10, r=10, t=50, b=10),
)

# Y-axes
fig.update_yaxes(title_text="Shots / Shots on Target", secondary_y=False)
fig.update_yaxes(title_text="Shot Accuracy (%)", range=[0, 100], secondary_y=True)

# Show chart in Streamlit
st.plotly_chart(fig, use_container_width=True)
    
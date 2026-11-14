import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="PressurePlay | T20 Intelligence", page_icon="🏏", layout="wide")
DATA = Path(__file__).parent / "data"

@st.cache_data
def load_csv(name):
    path = DATA / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def fmt_num(v, digits=1):
    try:
        return f"{float(v):,.{digits}f}"
    except (TypeError, ValueError):
        return "—"

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0b1729 0%,#10243d 55%,#132d49 100%); color:#f3f6fb;}
[data-testid="stMetric"] {background:#172e49; border:1px solid #315477; padding:14px; border-radius:12px;}
div[data-testid="stDataFrame"] {border:1px solid #315477; border-radius:10px;}
section[data-testid="stSidebar"] {background:#101f33;}
h1,h2,h3 {color:#f7f9fc;}
.small-note {color:#b8c7d8;font-size:0.88rem;}
</style>
""", unsafe_allow_html=True)

st.title("🏏 PressurePlay")
st.caption("T20 Pressure Performance Intelligence | Rajasthan Royals · IPL 2027 auction context")
st.markdown("Explore pressure performers, compare pressure and non-pressure output, and inspect historical consistency.")

with st.sidebar:
    st.header("Explore")
    fmt = st.selectbox("Format", ["IPL", "T20I"])
    role = st.radio("Player role", ["Batter", "Bowler"], horizontal=True)
    st.divider()
    page = st.radio("Dashboard view", ["Rankings", "Player explorer", "Historical trends", "Methodology"])

bat = role == "Batter"
rank_file = f"top10_{fmt}_{'batters' if bat else 'bowlers'}.csv"
rankings = load_csv(rank_file)
summary = load_csv("batter_consistency_summary.csv" if bat else "bowler_consistency_summary.csv")
season = load_csv("batter_season_pressure.csv" if bat else "bowler_season_pressure.csv")
match = load_csv("batter_match_consistency.csv" if bat else "bowler_match_consistency.csv")
id_col = "striker_id" if bat else "bowler_id"
name_col = "striker_name" if bat else "bowler_name"

if page == "Rankings":
    st.header(f"{fmt} · Top pressure {role.lower()}s")
    if rankings.empty:
        st.error(f"Could not load {rank_file}. Check the data folder.")
    else:
        top = rankings.copy()
        top["Player"] = top["player_name_clean"]
        top["Rank"] = top["rank"].astype(int)
        top["Pressure score"] = top["pressure_score"].round(2)
        cols = ["Rank","Player","Pressure score"]
        if bat:
            cols += ["runs_pressure","balls_faced_pressure","average_pressure","strike_rate_pressure","matches_pressure"]
            labels={"runs_pressure":"Pressure runs","balls_faced_pressure":"Balls faced","average_pressure":"Average","strike_rate_pressure":"Strike rate","matches_pressure":"Matches"}
        else:
            cols += ["wickets_pressure","legal_balls_pressure","economy_pressure","bowling_strike_rate_pressure","matches_pressure"]
            labels={"wickets_pressure":"Wickets","legal_balls_pressure":"Legal balls","economy_pressure":"Economy","bowling_strike_rate_pressure":"Bowling SR","matches_pressure":"Matches"}
        labels.update({"Rank":"Rank"})
        display=top[cols].rename(columns=labels)
        a,b,c=st.columns(3)
        a.metric("Players ranked",len(top))
        a.metric("Top pressure score",fmt_num(top["pressure_score"].max(),2))
        a.metric("Format",fmt if fmt=="IPL" else "T20 International")
        st.dataframe(display,use_container_width=True,hide_index=True)
        fig=px.bar(top.sort_values("pressure_score"),x="pressure_score",y="player_name_clean",orientation="h",
                   color="pressure_score",color_continuous_scale=["#4d7295","#e6b84f"],
                   labels={"pressure_score":"Pressure score","player_name_clean":"Player"})
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=480)
        st.plotly_chart(fig,use_container_width=True)
        st.download_button("Download this ranking as CSV",top.to_csv(index=False).encode(),file_name=f"{fmt}_{role}_top10.csv",mime="text/csv")

elif page == "Player explorer":
    st.header(f"{fmt} · {role} explorer")
    if rankings.empty:
        st.warning("Ranking file is missing.")
    else:
        names=rankings["player_name_clean"].dropna().tolist()
        selected=st.selectbox("Choose a ranked player",names)
        row=rankings.loc[rankings["player_name_clean"]==selected].iloc[0]
        hist=summary.copy()
        if not hist.empty:
            hist=hist[hist["match_format"].astype(str).str.upper().eq(fmt.upper())]
            hist=hist[hist[id_col].astype(str)==str(row["player_id"])]
        st.subheader(selected)
        c1,c2,c3=st.columns(3)
        c1.metric("Pressure score",fmt_num(row["pressure_score"],2))
        c2.metric("Pressure matches",fmt_num(row["matches_pressure"],0))
        c3.metric("Historical seasons",fmt_num(hist["seasons_with_pressure"].iloc[0],0) if not hist.empty else "—")
        if bat:
            c1,c2,c3=st.columns(3)
            c1.metric("Pressure runs",fmt_num(row["runs_pressure"],0))
            c2.metric("Pressure average",fmt_num(row["average_pressure"],2))
            c3.metric("Pressure strike rate",fmt_num(row["strike_rate_pressure"],2))
            c1,c2=st.columns(2)
            c1.metric("Non-pressure average",fmt_num(row["average_non_pressure"],2))
            c2.metric("Non-pressure strike rate",fmt_num(row["strike_rate_non_pressure"],2))
            if not hist.empty:
                st.markdown("#### Historical match-level summary")
                hr=hist.iloc[0]
                st.write(f"Mean pressure runs per match: **{fmt_num(hr['mean_pressure_runs_per_match'],2)}** · Median: **{fmt_num(hr['median_pressure_runs_per_match'],2)}**")
                st.write(f"Mean match-level pressure strike rate: **{fmt_num(hr['mean_pressure_strike_rate'],2)}** · Median: **{fmt_num(hr['median_pressure_strike_rate'],2)}**")
        else:
            c1,c2,c3=st.columns(3)
            c1.metric("Pressure wickets",fmt_num(row["wickets_pressure"],0))
            c2.metric("Pressure economy",fmt_num(row["economy_pressure"],2))
            c3.metric("Pressure bowling SR",fmt_num(row["bowling_strike_rate_pressure"],2))
            c1,c2=st.columns(2)
            c1.metric("Non-pressure economy",fmt_num(row["economy_non_pressure"],2))
            c2.metric("Non-pressure bowling SR",fmt_num(row["bowling_strike_rate_non_pressure"],2))
            if not hist.empty:
                hr=hist.iloc[0]
                st.markdown("#### Historical match-level summary")
                st.write(f"Mean pressure wickets per match: **{fmt_num(hr['mean_pressure_wickets_per_match'],2)}**")
                st.write(f"Mean pressure economy: **{fmt_num(hr['mean_pressure_economy'],2)}** · Median: **{fmt_num(hr['median_pressure_economy'],2)}**")
        st.info("Player explorer currently searches the Top 10 ranking cohort. Historical summary files cover a wider player pool.")

elif page == "Historical trends":
    st.header(f"{fmt} · Historical pressure trends")
    if season.empty:
        st.warning("Season-level file is missing.")
    else:
        s=season[season["match_format"].astype(str).str.upper().eq(fmt.upper())].copy()
        if s.empty:
            st.info("No seasonal records for this format.")
        else:
            s["player_label"]=s[name_col].astype(str)
            options=sorted(s["player_label"].dropna().unique())
            selected=st.selectbox("Select player",options)
            one=s[s["player_label"]==selected].sort_values("season_start_year")
            metric="pressure_strike_rate" if bat else "economy"
            metric_label="Pressure strike rate" if bat else "Pressure economy"
            st.subheader(selected)
            fig=px.line(one,x="season",y=metric,markers=True,title=f"{metric_label} by season")
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
            st.dataframe(one,use_container_width=True,hide_index=True)
            if not match.empty:
                m=match[match["match_format"].astype(str).str.upper().eq(fmt.upper())]
                m=m[m[name_col].astype(str)==selected]
                st.caption(f"Match-level observations available: {len(m)}")
                if not m.empty:
                    st.dataframe(m,use_container_width=True,hide_index=True)

else:
    st.header("How PressurePlay works")
    st.subheader("Pressure situation definition")
    st.markdown("""
    Pressure is assessed immediately **before each delivery** in a second-innings chase. A delivery is marked as pressure if at least one condition applies:
    - Required run rate ≥ 12 with ≤ 60 legal balls remaining.
    - Required run rate ≥ 10 with ≤ 30 legal balls remaining.
    - ≤ 5 wickets remaining, ≤ 30 legal balls remaining and required run rate ≥ 8.
    - ≤ 12 legal balls remaining and at least 20 runs still required.
    """)
    st.subheader("Eligibility")
    st.write("Batters: at least 30 pressure balls faced and 5 pressure matches. Bowlers: at least 60 pressure legal balls and 5 pressure matches.")
    st.subheader("Important interpretation")
    st.markdown("""
    - Rankings are separate for IPL and T20I, and for batters and bowlers.
    - Pressure score is a relative weighted-percentile index, not a probability of future success.
    - Historical coverage is supporting evidence; it does not automatically change the Top 10 order.
    - The non-pressure comparison is a broad baseline, not a matched control group.
    - The current app ships with the latest precomputed ranking and historical CSV outputs. It does not recalculate rankings from newly uploaded ball-by-ball data.
    """)
    st.subheader("Historical confidence screen")
    st.write("Stronger historical coverage means at least 8 pressure matches across at least 3 seasons. This is an analyst-selected threshold, not an official competition rule.")

st.divider()
st.markdown('<p class="small-note">PressurePlay prototype · Based on the latest supplied project CSV outputs · IPL and T20I comparisons remain separate.</p>',unsafe_allow_html=True)

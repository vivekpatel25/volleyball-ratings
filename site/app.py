import pandas as pd
import streamlit as st

st.set_page_config(page_title="Volleyball Ratings", layout="wide")

st.title("🏐 ACAC Volleyball Ratings")
st.markdown("### O-Rtg (Offense), D-Rtg (Defense), T-Rtg (Total) Leaderboards")

# Load leaderboards
men = pd.read_csv("data/leaderboard_men_2025.csv")
women = pd.read_csv("data/leaderboard_women_2025.csv")

tab1, tab2 = st.tabs(["Men", "Women"])

with tab1:
    st.subheader("Men's Leaderboard")
    st.dataframe(men.sort_values("T-Rtg", ascending=False).head(20))

with tab2:
    st.subheader("Women's Leaderboard")
    st.dataframe(women.sort_values("T-Rtg", ascending=False).head(20))

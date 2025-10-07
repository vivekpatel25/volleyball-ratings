import pandas as pd
import streamlit as st
from datetime import date

# --- Page setup ---
st.set_page_config(page_title="ACAC Volleyball 2025-26 Ratings", layout="wide")

# --- Header Section ---
st.markdown("""
# 🏐 The Best ACAC Volleyball Players by Rating (2025-26)

*Updated weekly — last update:* **{today}**

These ratings combine offensive, defensive, and total impact metrics.
O-Rtg measures scoring contribution, D-Rtg measures defensive control,
and T-Rtg represents the overall player impact.
""".format(today=date.today().strftime("%a %b %d %Y")))

st.markdown("### Click any column header (O-Rtg, D-Rtg, or T-Rtg) to sort interactively.")

st.markdown("---")

# --- Load data ---
try:
    men = pd.read_csv("data/leaderboard_men_2025.csv")
    women = pd.read_csv("data/leaderboard_women_2025.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Columns to display ---
cols = ["Player", "Team", "O-Rtg", "D-Rtg", "T-Rtg"]

# --- Prepare Men Data ---
if all(c in men.columns for c in cols):
    men = men[cols]
else:
    st.warning("Some columns missing in men's data. Showing full file.")
men = men.sort_values("T-Rtg", ascending=False).head(20)

# --- Prepare Women Data ---
if all(c in women.columns for c in cols):
    women = women[cols]
else:
    st.warning("Some columns missing in women's data. Showing full file.")
women = women.sort_values("T-Rtg", ascending=False).head(20)

# --- Tabs for Men and Women ---
tab1, tab2 = st.tabs(["Men", "Women"])

with tab1:
    st.subheader("Men's Leaderboard — Top 20")
    st.dataframe(men, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Women's Leaderboard — Top 20")
    st.dataframe(women, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("© 2025 ACAC Volleyball Ratings — Created by Vivek Patel | Data refreshed weekly")

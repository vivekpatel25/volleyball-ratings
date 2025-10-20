import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import date
import requests

SEASON = "2025/26"
st.set_page_config(page_title="ACAC Volleyball Ratings", page_icon="🏐", layout="wide")

# ---------- FETCH LAST UPDATE ----------
def get_last_update_from_github(repo_owner, repo_name, branch="main"):
    try:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{branch}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        from datetime import datetime
        dt = datetime.strptime(data["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return "N/A"

repo_owner = "vivekpatel25"
repo_name = "volleyball-ratings"
last_update = get_last_update_from_github(repo_owner, repo_name)

# ---------- HEADER ----------
st.markdown(f"""
<div style="background:linear-gradient(90deg,#0066cc,#00aaff);
            padding:1.6rem 2rem;border-radius:8px;color:white;">
  <h1 style="margin-bottom:0;">🏐 ACAC Volleyball Ratings — {SEASON}</h1>
  <p style="margin-top:0.4rem;font-size:1rem;opacity:0.9;">
     Last updated on • <b>{last_update}</b>
  </p>
</div>
""", unsafe_allow_html=True)

# ---------- INTRO ----------
st.markdown("""
### 📊 About These Ratings
Each player’s **Total Rating (T-Rtg)** combines both offensive and defensive impact per set.  
- **O-Rtg:** Offensive contribution (kills – errors + serve + assists)  
- **D-Rtg:** Defensive control (digs + blocks – reception errors)  
- **T-Rtg:** Combined overall impact per set  
---
""")

# ---------- LOAD LEADERBOARDS ----------
@st.cache_data
def load_board(gender):
    try:
        df = pd.read_csv(f"data/leaderboard_{gender}_2025.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading {gender} data: {e}")
        return pd.DataFrame()

# ---------- SORT SCRIPT ----------
SORT_SCRIPT = """
<script>
let sortDirections = {};
function sortTable(n) {
  const table = event.target.closest("table");
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const currentDir = sortDirections[n] || "desc";
  const newDir = currentDir === "asc" ? "desc" : "asc";
  sortDirections[n] = newDir;

  rows.sort((a, b) => {
    const aText = a.cells[n].innerText.trim();
    const bText = b.cells[n].innerText.trim();
    const aNum = parseFloat(aText);
    const bNum = parseFloat(bText);
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return newDir === "asc" ? aNum - bNum : bNum - aNum;
    }
    return newDir === "asc"
      ? aText.localeCompare(bText)
      : bText.localeCompare(aText);
  });
  rows.forEach(r => tbody.appendChild(r));
}
</script>
"""

# ---------- TABLE RENDERER ----------
def render_table(df):
    dark = st.get_option("theme.base") == "dark"
    if dark:
        border_color, text_color, header_bg, row_hover, table_bg = (
            "#fff", "#fff", "#222", "rgba(255,255,255,0.1)", "#111"
        )
    else:
        border_color, text_color, header_bg, row_hover, table_bg = (
            "#000", "#000", "#f2f2f2", "rgba(0,0,0,0.05)", "#fff"
        )

    for col in ["O-Rtg", "D-Rtg", "T-Rtg"]:
        if col in df.columns and df[col].notna().any():
            vmin, vmax = df[col].min(), df[col].max()
            rng = vmax - vmin if vmax != vmin else 1
            df[f"_{col}_norm"] = (df[col] - vmin) / rng
        else:
            df[f"_{col}_norm"] = 0.0

    headers = ["Jersey", "Player", "Team", "SP", "O-Rtg", "D-Rtg", "T-Rtg"]
    html = f"""
    <div style="overflow-x:auto;margin:0;padding:0;">
      <table style="width:100%;border-collapse:collapse;font-size:16px;
                    color:{text_color};background-color:{table_bg};
                    border:2px solid {border_color};border-radius:6px;">
        <thead><tr style="background:{header_bg};color:{text_color};">
    """
    for i, col in enumerate(headers):
        # Only SP, O-Rtg, D-Rtg, T-Rtg sortable
        cursor = "pointer" if col in ["SP", "O-Rtg", "D-Rtg", "T-Rtg"] else "default"
        html += (
            f"<th onclick='sortTable({i})' style='border:1px solid {border_color};white-space:nowrap;"
            f"cursor:{cursor};padding:8px 10px;'>{col} ⬍</th>"
            if cursor == "pointer"
            else f"<th style='border:1px solid {border_color};white-space:nowrap;padding:8px 10px;'>{col}</th>"
        )
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += f"<tr onmouseover=\"this.style.background='{row_hover}'\" onmouseout=\"this.style.background='transparent'\">"
        for c in headers:
            bg = "transparent"
            if c == "O-Rtg":
                intensity = row.get("_O-Rtg_norm", 0)
                bg = f"rgba(255,0,0,{0.15 + 0.75*intensity})"
            elif c == "D-Rtg":
                intensity = row.get("_D-Rtg_norm", 0)
                bg = f"rgba(0,255,0,{0.15 + 0.75*intensity})"
            elif c == "T-Rtg":
                intensity = row.get("_T-Rtg_norm", 0)
                bg = f"rgba(0,0,255,{0.15 + 0.75*intensity})"

            weight = "bold" if c == "T-Rtg" else "normal"
            html += (
                f"<td style='border:1px solid {border_color};text-align:center;white-space:nowrap;"
                f"padding:8px 10px;font-weight:{weight};background-color:{bg};'>"
                f"{row.get(c,'')}</td>"
            )
        html += "</tr>"
    html += "</tbody></table></div>"
    return html + SORT_SCRIPT

# ---------- MAIN ----------
tabs = st.tabs(["👨 Men", "👩 Women"])
for tab, gender in zip(tabs, ["men", "women"]):
    with tab:
        df = load_board(gender)
        if df.empty:
            st.info(f"No leaderboard yet for {gender}.")
            continue

        df = df.rename(columns=str.strip)
        df = df.rename(columns={
            next((c for c in df.columns if "jersey" in c.lower()), "Jersey"): "Jersey",
            next((c for c in df.columns if "player" in c.lower()), "Player"): "Player",
            next((c for c in df.columns if "team" in c.lower()), "Team"): "Team",
            next((c for c in df.columns if "sp" in c.lower()), "SP"): "SP",
            next((c for c in df.columns if "o-rtg" in c.lower()), "O-Rtg"): "O-Rtg",
            next((c for c in df.columns if "d-rtg" in c.lower()), "D-Rtg"): "D-Rtg",
            next((c for c in df.columns if "t-rtg" in c.lower()), "T-Rtg"): "T-Rtg",
        })

        keep = [c for c in ["Jersey","Player","Team","SP","O-Rtg","D-Rtg","T-Rtg"] if c in df.columns]
        df = df[keep].copy()

        for c in ["O-Rtg","D-Rtg","T-Rtg"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
        if "T-Rtg" in df.columns:
            df = df.sort_values("T-Rtg", ascending=False).head(20)

        st.subheader(f"🏐 ACAC {gender.capitalize()} Leaderboard — Top 20")
        st.caption("Click **SP**, **O-Rtg**, **D-Rtg**, or **T-Rtg** to sort.")
        components.html(render_table(df), height=len(df)*38 + 100, scrolling=False)

# ---------- FOOTER ----------
st.markdown("""
<div style="margin-top:2rem;text-align:center;color:gray;font-size:0.9rem;">
<hr>
© 2025 ACAC Volleyball Ratings • Designed by Vivek Patel
</div>
""", unsafe_allow_html=True)

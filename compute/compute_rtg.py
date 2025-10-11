import pandas as pd
import os
from glob import glob

# ========== CONFIGURATION ==========
BOX_PATH = "data/boxscores/"
ROSTER_MEN = "data/roster_men_25-26.csv"
ROSTER_WOMEN = "data/roster_women_25-26.csv"
OUT_MEN = "data/leaderboard_men_2025.csv"
OUT_WOMEN = "data/leaderboard_women_2025.csv"

# ========== FORMULAS ==========
def compute_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Compute O-Rtg, D-Rtg, and T-Rtg for each player."""
    df["O-Rtg"] = ((df["K"] - df["E"]) +
                   (df["SA"] - df["SE"]) +
                   (df["A"] * 0.3)) / df["SP"]

    df["D-Rtg"] = ((df["DIGS"] * 0.5) +
                   (df["BS"] + 0.5 * df["BA"]) -
                   (df["BE"] + df["RE"])) / df["SP"]

    df["T-Rtg"] = df["O-Rtg"] + df["D-Rtg"]
    return df


def combine_boxscores(folder: str) -> pd.DataFrame:
    """Read all team boxscores and combine season totals."""
    all_files = glob(os.path.join(folder, "*.csv"))
    if not all_files:
        print(f"⚠️ No boxscore files found in {folder}")
        return pd.DataFrame()

    dfs = []
    for f in all_files:
        try:
            temp = pd.read_csv(f)
            temp["source_file"] = os.path.basename(f)
            dfs.append(temp)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    if not dfs:
        print("⚠️ No valid boxscore data found.")
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Standardize columns
    df.columns = [c.strip().upper() for c in df.columns]
    required_cols = ["PLAYER", "TEAM", "SP","K","E","TA","A","SA","SE","RE",
                     "DIGS","BS","BA","BE","BHE","PTS"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"⚠️ Missing columns in some files: {missing}")

    # Group by player + team for cumulative totals
    agg_dict = {c: "sum" for c in required_cols if c not in ["PLAYER","TEAM"]}
    df = df.groupby(["PLAYER", "TEAM"], as_index=False).agg(agg_dict)
    return df


def merge_roster_stats(stats_df: pd.DataFrame, roster_path: str, gender: str) -> pd.DataFrame:
    """Merge cumulative stats with roster (adds Player_ID, Jersey) and warn on mismatches."""
    if stats_df.empty:
        return pd.DataFrame()

    try:
        roster = pd.read_csv(roster_path)
    except Exception as e:
        print(f"❌ Error reading roster {roster_path}: {e}")
        return stats_df

    roster.columns = [c.strip().title() for c in roster.columns]
    stats_df.columns = [c.strip().title() for c in stats_df.columns]

    merged = stats_df.merge(roster, on=["Player", "Team"], how="left")

    # Warn if any player not found in roster
    missing = merged[merged["Player_Id"].isna()][["Player", "Team"]]
    if not missing.empty:
        print(f"⚠️ {len(missing)} {gender} players not found in roster:")
        for _, row in missing.iterrows():
            print(f"   • {row['Player']} ({row['Team']})")

    return merged


# ========== MAIN WORKFLOW ==========
if __name__ == "__main__":
    print("\n🏐 Updating Volleyball Ratings...\n")

    # --- MEN ---
    men_df = combine_boxscores(BOX_PATH)
    men_rtg = compute_ratings(men_df)
    men_merged = merge_roster_stats(men_rtg, ROSTER_MEN, "men")
    men_merged.to_csv(OUT_MEN, index=False)
    print(f"✅ Men's leaderboard saved → {OUT_MEN}\n")

    # --- WOMEN ---
    women_df = combine_boxscores(BOX_PATH)
    women_rtg = compute_ratings(women_df)
    women_merged = merge_roster_stats(women_rtg, ROSTER_WOMEN, "women")
    women_merged.to_csv(OUT_WOMEN, index=False)
    print(f"✅ Women's leaderboard saved → {OUT_WOMEN}\n")

    print("🎯 Update complete — all ratings recalculated season-to-date.\n")

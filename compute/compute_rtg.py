import pandas as pd
import os
from glob import glob

# ========== CONFIGURATION ==========
BOX_PATH_MEN = "data/boxscores/men/"
BOX_PATH_WOMEN = "data/boxscores/women/"
ROSTER_MEN = "data/roster_men_25-26.csv"
ROSTER_WOMEN = "data/roster_women_25-26.csv"
OUT_MEN = "data/leaderboard_men_2025.csv"
OUT_WOMEN = "data/leaderboard_women_2025.csv"

# ========== HELPER FUNCTIONS ==========
def rename_columns(df):
    """Rename columns from raw boxscore headers to standard names."""
    mapping = {
        "player_name": "Player",
        "team_name": "Team",
        "jersey_no": "Jersey",
        "sets_played": "SP",
        "attack_kills": "K",
        "attack_errors": "E",
        "attack_total_attempts": "TA",
        "setting_assists": "A",
        "serve_aces": "SA",
        "serve_errors": "SE",
        "reception_erros": "RE",
        "digs": "DIGS",
        "block_single": "BS",
        "block_assists": "BA",
        "block_errors": "BE",
        "ball_handling_errors": "BHE"
    }
    df = df.rename(columns={c: mapping.get(c.lower().strip(), c) for c in df.columns})
    return df


def clean_player_names(df):
    """Remove asterisk (*) and extra spaces from player names."""
    if "Player" in df.columns:
        df["Player"] = (
            df["Player"]
            .astype(str)
            .str.replace("*", "", regex=False)
            .str.strip()
        )
    return df


def compute_ratings(df):
    """Compute O-Rtg, D-Rtg, and T-Rtg for each player."""
    df["O-Rtg"] = ((df["K"] - df["E"]) +
                   (df["SA"] - df["SE"]) +
                   (df["A"] * 0.3)) / df["SP"]

    df["D-Rtg"] = ((df["DIGS"] * 0.5) +
                   (df["BS"] + 0.5 * df["BA"]) -
                   (df["BE"] + df["RE"])) / df["SP"]

    df["T-Rtg"] = df["O-Rtg"] + df["D-Rtg"]
    return df


def combine_boxscores(folder):
    """Combine all team boxscores in a folder into season totals."""
    files = glob(os.path.join(folder, "*.csv"))
    if not files:
        print(f"⚠️ No boxscore files found in {folder}")
        return pd.DataFrame()

    df_list = []
    for f in files:
        try:
            temp = pd.read_csv(f)
            temp = rename_columns(temp)
            temp = clean_player_names(temp)
            df_list.append(temp)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    df = pd.concat(df_list, ignore_index=True)

    # Convert numeric columns safely
    num_cols = ["SP","K","E","TA","A","SA","SE","RE","DIGS","BS","BA","BE","BHE"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Group by player + team for cumulative totals
    df = df.groupby(["Player", "Team"], as_index=False).sum(numeric_only=True)
    return df


def merge_with_roster(df, roster_path, gender):
    """Merge stats with roster and warn if missing."""
    if df.empty:
        return pd.DataFrame()

    try:
        roster = pd.read_csv(roster_path)
    except Exception as e:
        print(f"❌ Error reading roster {roster_path}: {e}")
        return df

    roster = clean_player_names(roster)

    merged = df.merge(roster, on=["Player", "Team"], how="left")

    missing = merged[merged["Player_ID"].isna()][["Player", "Team"]]
    if not missing.empty:
        print(f"⚠️ {len(missing)} {gender} players not found in roster:")
        for _, row in missing.iterrows():
            print(f"   • {row['Player']} ({row['Team']})")

    return merged


# ========== MAIN WORKFLOW ==========
if __name__ == "__main__":
    print("\n🏐 Updating Volleyball Ratings...\n")

    # --- MEN ---
    men_df = combine_boxscores(BOX_PATH_MEN)
    men_rtg = compute_ratings(men_df)
    men_final = merge_with_roster(men_rtg, ROSTER_MEN, "men")
    men_final.to_csv(OUT_MEN, index=False)
    print(f"✅ Men's leaderboard saved → {OUT_MEN}\n")

    # --- WOMEN ---
    women_df = combine_boxscores(BOX_PATH_WOMEN)
    women_rtg = compute_ratings(women_df)
    women_final = merge_with_roster(women_rtg, ROSTER_WOMEN, "women")
    women_final.to_csv(OUT_WOMEN, index=False)
    print(f"✅ Women's leaderboard saved → {OUT_WOMEN}\n")

    print("🎯 Update complete — all ratings recalculated season-to-date.\n")

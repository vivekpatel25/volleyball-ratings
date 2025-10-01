import pandas as pd

def compute_ratings(df):
    df["O-Rtg"] = ((df["K"] - df["E"]) +
                   (df["SA"] - df["SE"]) +
                   (df["A"] * 0.3)) / df["SP"]

    df["D-Rtg"] = ((df["DIGS"] * 0.5) +
                   (df["BS"] + 0.5*df["BA"]) -
                   (df["BE"] + df["RE"])) / df["SP"]

    df["T-Rtg"] = df["O-Rtg"] + df["D-Rtg"]
    return df

if __name__ == "__main__":
    # Load boxscores (make sure CSV has all required columns)
    men = pd.read_csv("data/boxscores/men_boxscores.csv")
    women = pd.read_csv("data/boxscores/women_boxscores.csv")

    men_rtg = compute_ratings(men)
    women_rtg = compute_ratings(women)

    men_rtg.to_csv("data/leaderboard_men_2025.csv", index=False)
    women_rtg.to_csv("data/leaderboard_women_2025.csv", index=False)

    print("Leaderboards updated.")

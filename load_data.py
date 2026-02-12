import pandas as pd


def min_sec_to_deltatime_format(s: int) -> str:
    return "00:" + str(s)


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, decimal=".", thousands=",", na_values=["--"])

    # Strings
    str_cols = ["Aktivitetstyp", "Namn", "Medelkontakttidsbalans"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Boolean columns
    df["Favorit"] = (
        df["Favorit"].astype(str).str.lower().map({"true": True, "false": False})
    )
    df["Dekompression"] = (
        df["Dekompression"].astype(str).str.strip().map({"Ja": True, "Nej": False})
    )

    # Datetime
    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    df = df.set_index("Datum")

    # Convert all activity distances to km
    meter_activities = ["Simbassäng", "Simning"]
    mask = df["Aktivitetstyp"].isin(meter_activities)
    # Convert only those rows from meters to km
    df.loc[mask, "Distans"] = df.loc[mask, "Distans"] / 1000.0

    min_sec_cols = ["Medeltempo", "Bästa tempo"]
    for col in min_sec_cols:
        if col in df.columns:
            df[col] = df[col].map(min_sec_to_deltatime_format)

    # Time/duration columns
    time_cols = [
        "Tid",
        "Medeltempo",
        "Bästa tempo",
        "Medelvärde GAP",
        "Bästa varvtid",
        "Start för stress",
        "Slut för stress",
        "Färdtid",
        "Total tid",
    ]
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_timedelta(df[col], errors="coerce")

    # Hour format time
    hour_format_cols = [
        "Tid",
        "Färdtid",
        "Total tid",
    ]
    for col in hour_format_cols:
        if col in df.columns:
            df[col] = df[col].dt.total_seconds() / 3600

    return df

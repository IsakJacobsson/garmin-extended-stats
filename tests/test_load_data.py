import pandas as pd

from load_data import load_data

csv_file = "tests/testfiles/activities.csv"


def test_string_columns():
    df = load_data(csv_file)
    string_cols = ["Aktivitetstyp", "Namn", "Medelkontakttidsbalans"]
    for col in string_cols:
        assert df[col].dtype == object
        # Check no leading/trailing spaces
        assert all(df[col].str.strip() == df[col])

    assert df.iloc[0]["Namn"] == "Väldigt konstigt namn."


def test_boolean_columns():
    df = load_data(csv_file)
    boolean_cols = ["Favorit", "Dekompression"]
    for col in boolean_cols:
        assert df[col].dtype == bool


def test_index_is_datetime():
    df = load_data(csv_file)
    assert isinstance(df.index, pd.DatetimeIndex)


def test_steps():
    df = load_data(csv_file)
    assert df.iloc[0]["Steg"] == 6234


def test_swim_distance():
    df = load_data(csv_file)
    swim_rows = df[df["Aktivitetstyp"] == "Simbassäng"]
    assert swim_rows.iloc[0]["Distans"] == 1.0


def test_numeric_columns():
    df = load_data(csv_file)
    numeric_cols = [
        "Distans",
        "Kalorier",
        "Medelpuls",
        "Maxpuls",
        "Aerobisk Training Effect",
        "Medellöpkadens",
        "Maximal löpkadens",
        "Total stigning",
        "Totalt nedför",
        "Medelsteglängd",
        "Medelvärde för vertikal kvot",
        "Medelvärde för vertikal rörelse",
        "Medeltid för markkontakt",
        "Normalized Power® (NP®)",
        "Training Stress Score®",
        "Med. kraft",
        "Maxkraft",
        "Totalt antal årtag",
        "Medel-Swolf",
        "Medelårtagstempo",
        "Steg",
        "Totalt antal repetitioner",
        "Totalt antal set",
        "Urladdning av Body Battery",
        "Minsta temperatur",
        "Antal varv",
        "Maximal temperatur",
        "Genomsnittlig andning",
        "Minsta andningshastighet",
        "Maximal andningshastighet",
        "Stressändring",
        "Medestress",
        "Maxbelastning",
        "Min. höjd",
        "Max. höjd",
    ]
    for col in numeric_cols:
        pd.api.types.is_numeric_dtype(df[col])


def test_timedelta_columns():
    df = load_data(csv_file)
    time_cols = [
        "Medeltempo",
        "Bästa tempo",
        "Medelvärde GAP",
        "Bästa varvtid",
        "Start för stress",
        "Slut för stress",
    ]
    for col in time_cols:
        assert pd.api.types.is_timedelta64_dtype(df[col])

    assert df.iloc[0]["Medeltempo"].seconds == 6 * 60 + 22
    assert df.iloc[0]["Bästa tempo"].seconds == 2 * 60 + 34
    assert df.iloc[0]["Bästa varvtid"].total_seconds() == 56.9


def test_hour_format_columns():
    df = load_data(csv_file)
    hour_format_cols = [
        "Tid",
        "Färdtid",
        "Total tid",
    ]

    for col in hour_format_cols:
        pd.api.types.is_numeric_dtype(df[col])

    assert df.iloc[0]["Tid"] == (46 * 60 + 46) / 3600
    assert df.iloc[0]["Färdtid"] == (38 * 60 + 47) / 3600
    assert df.iloc[0]["Total tid"] == (46 * 60 + 48) / 3600

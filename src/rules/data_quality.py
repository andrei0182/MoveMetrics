import pandas as pd


def clean_provider_names(df):

    data = df.copy()


    invalid = [
        "AL4170",
        "AL4470",
        "WB1031-DUP"
    ]


    data.loc[
        data["Sursa"].isin(invalid),
        "Sursa"
    ] = "unknown"


    return data



def data_quality_report(df):

    report = {}


    report["Rows"] = len(df)

    report["Missing Values"] = (
        df.isna()
        .sum()
        .sum()
    )


    report["Duplicates"] = (
        df.duplicated()
        .sum()
    )


    return report
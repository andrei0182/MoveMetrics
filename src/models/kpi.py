import pandas as pd


def clean_currency(value):
    """
    Convert $1,050.00 -> 1050.0
    """

    if pd.isna(value):
        return 0.0

    value = str(value)

    value = (
        value
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)
    except:
        return 0.0



def calculate_kpis(df):

    data = df.copy()


    # Convert money columns
    money_columns = [
        "Charged",
        "Deposit/Quote",
        "Total job (iulie)",
        "Rest de încasat"
    ]


    for col in money_columns:

        if col in data.columns:
            data[col] = (
                data[col]
                .apply(clean_currency)
            )


    kpis = {}


    kpis["Total Charged"] = (
        data["Charged"].sum()
    )


    kpis["Total Jobs"] = (
        data["Job #"].nunique()
    )


    kpis["Average Job Value"] = (
        data["Charged"].mean()
    )


    kpis["Refunds"] = (
        data[
            data["De verificat"]
            .astype(str)
            .str.contains(
                "REFUND",
                case=False,
                na=False
            )
        ]
        .shape[0]
    )


    kpis["Outstanding"] = (
        data["Rest de încasat"].sum()
    )


    return kpis
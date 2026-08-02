import pandas as pd


def get_sheets(file_path):

    excel = pd.ExcelFile(file_path)

    return excel.sheet_names



def load_excel(
    file_path,
    sheet_name
):

    # citim fără header
    raw = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None
    )


    # căutăm rândul care conține "Job #"
    header_row = None

    for index, row in raw.iterrows():

        values = row.astype(str).tolist()

        if "Job #" in values:
            header_row = index
            break


    if header_row is None:
        raise ValueError(
            "Nu am găsit header-ul Excel"
        )


    # recitim cu header corect
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=header_row
    )


    # eliminăm coloane goale
    df = df.dropna(
        axis=1,
        how="all"
    )


    # curățăm nume coloane
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    return df
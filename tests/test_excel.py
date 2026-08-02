from src.excel.excel_loader import load_excel


file = "data/raw/Report_AUG.xlsx"


df = load_excel(
    file,
    "CHARGED "
)


print(df.head())


print("\nCOLUMNS:")
print(df.columns.tolist())


print("\nROWS:")
print(df.shape)
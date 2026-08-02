from src.excel.excel_loader import load_excel
from src.analysis.financial_analysis import calculate_financials


file = "data/raw/Report_JUL.xlsx"


df = load_excel(
    file,
    "CHARGED"
)
print("\nULTIMELE 50 RANDURI:")
print(df.tail(50)[[
    "Job #",
    "Nume Client",
    "Sursa",
    "Data",
    "Status"
]].to_string())

print(df.columns)

print("\nRAW ROWS:")
print(len(df))


print("\nVALID JOBS:")
print(
    df["Job #"]
    .astype(str)
    .str.match(r"^(AL|HA|WB|MN|QU|GH|CF)[A-Z0-9-]+$", na=False)
    .sum()
)
print("\nULTIMELE JOBURI:")
print(df["Job #"].tail(20).to_string())


print("\nVALORI LUNGI:")
print(
    df["Job #"]
    .astype(str)
    .str.len()
    .value_counts()
)

financial = calculate_financials(df)


print("\nFINANCIAL KPI:")
for key, value in financial.items():
    print(
        key,
        ":",
        value
    )
print("\nAL4993 CHECK")

print(
    df[df["Job #"]=="AL4993"]
)


print("\nOLD PAYMENTS")

print(
    df[df["Status"].str.contains("plată_job_vechi", na=False)]
)    
from src.excel.excel_loader import load_excel
from src.analysis.provider_analysis import analyze_providers


file = "data/raw/Report_JUL.xlsx"


df = load_excel(
    file,
    "CHARGED "
)


result = analyze_providers(df)


print(result)
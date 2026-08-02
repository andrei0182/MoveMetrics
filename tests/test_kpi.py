from src.excel.excel_loader import load_excel
from src.models.kpi import calculate_kpis


file = "data/raw/Report_JUL.xlsx"


df = load_excel(
    file,
    "CHARGED "
)


kpis = calculate_kpis(df)


print(kpis)
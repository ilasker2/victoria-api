# Actuals

`01_income_statement_monthly_actuals.csv` is a derived export of the original workbook in `../source/`. It is historical actuals: one row per closed month.

The workbook in `source/` is the preserved original. Do not overwrite it. Regenerate the CSV with:

```bash
python3 -m server.finance
```

No forecast file is in this folder. Forecast figures live only in `../03-forecast.md` and must be labeled forecast.

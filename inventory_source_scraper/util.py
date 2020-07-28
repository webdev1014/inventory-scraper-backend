"""inventory_source_scraper Utility methods
"""
import os
import logging
from openpyxl import Workbook, load_workbook
from pathlib import Path

output = os.path.join(os.path.dirname(__file__), 'static', 'output.xlsx')


def remove_output_file():
    file = Path(output)
    try:
        file.unlink()
    except FileNotFoundError:
        print('No output file')


def save_data(name, upc, company, price_inventory, price_amazon, shipping_amazon):
    field_names = ['Product Name',
                   'UPC',
                   'Company',
                   'Wholesale Price',
                   'Amazon Price',
                   'Prime Shipping',
                   'Margin(%)',
                   'Margin($)']

    file = Path(output)
    if file.is_file() is False:
        wb = Workbook()
        ws = wb.active
        for i, field_name in enumerate(field_names, start=1):
            ws.cell(row=1, column=i, value=field_name)
    else:
        wb = load_workbook(filename=output)
        ws = wb.active

    row = ws.max_row + 1
    ws.cell(row=row, column=1, value=name)
    ws.cell(row=row, column=2, value=upc)
    ws.cell(row=row, column=3, value=company)
    ws.cell(row=row, column=4, value=price_inventory)
    ws.cell(row=row, column=5, value=price_amazon)
    ws.cell(row=row, column=6, value=shipping_amazon)
    ws.cell(row=row, column=7, value=f'=(E{row}-D{row})/D{row}*100')
    ws.cell(row=row, column=8, value=f'=E{row}-D{row}')

    wb.save(filename=output)



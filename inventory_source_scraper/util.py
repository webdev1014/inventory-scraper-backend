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


def save_data(products):
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

    for product in products:
        ws.cell(row=row, column=1, value=product['name'])
        ws.cell(row=row, column=2, value=product['upc'])
        ws.cell(row=row, column=3, value=product['company'])
        ws.cell(row=row, column=4, value=product['price_inventory'])
        ws.cell(row=row, column=5, value=product['price_amazon'])
        ws.cell(row=row, column=6, value=product['shipping_amazon'])
        ws.cell(row=row, column=7, value=f'=(E{row}-D{row})/D{row}*100')
        ws.cell(row=row, column=8, value=f'=E{row}-D{row}')
        row += 1

    wb.save(filename=output)



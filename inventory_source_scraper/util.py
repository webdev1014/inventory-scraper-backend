"""inventory_source_scraper Utility methods
"""
import os
import logging
import csv
from pathlib import Path

output = 'output.xlsx'

def remove_output_file():
    file = Path(output)
    try:
        file.unlink()
    except FileNotFoundError:
        print('No output file')


def save_data(corp_name,
              fei_ein_number,
              date_filed,
              status,
              last_event,
              principal_addr,
              mailing_addr,
              registered_agent_addr,
              officer_addr,
              url):
    file = Path(output)

    field_names = ['Corporation Name',
                   'FEI/EIN Number',
                   'Date Filed',
                   'Status',
                   'Last Event',
                   'Principal Address',
                   'Mailing Address',
                   'Registered Agent Name & Address',
                   'Officer Direct Detail Name & Address',
                   'Link']
    if file.is_file() is False:
        with open(output, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

    with open(output, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([corp_name,
                         fei_ein_number,
                         date_filed,
                         status,
                         last_event,
                         principal_addr,
                         mailing_addr,
                         registered_agent_addr,
                         officer_addr,
                         url])

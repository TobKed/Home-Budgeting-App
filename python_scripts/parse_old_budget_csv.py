""" A helper script to parse my old budget file to generic csv """
import argparse
import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.comments import Comment
from openpyxl.worksheet.worksheet import Worksheet

logging.basicConfig(level=logging.INFO)

ROWS = range(2, 32 + 1)
COLUMN_DATE = 1
COLUMNS = {
    1: "DATE",
    3: "bills-flat",
    4: "bills-other",
    6: "food-shop",
    7: "food-restaurant",
    8: "food-sweets",
    9: "food-alcohol",
    10: "cosmetics",
    11: "medicines",
    12: "domestic",
    13: "clothes",
    15: "party",
    16: "sport",
    17: "school",
    18: "other",
    19: "Mom",
}


@dataclass
class Expenditure:
    value: float
    date: datetime
    category: Optional[str]
    comment: Optional[str]


def get_filename_from_args() -> str:
    parser = argparse.ArgumentParser(description="Process some budget files.")
    parser.add_argument(
        "filename", metavar="F", type=str, help="Budget filename to be parsed"
    )
    args = parser.parse_args()
    return args.filename


def get_worksheets(file_path: str) -> List[Worksheet]:
    wb = load_workbook(file_path, data_only=True)
    logging.info('Opened workbook: "%s"', file_path)
    return [ws for ws in wb.worksheets if ws.title != "BUDGET"]


def sanitize_comment(comment: Comment) -> Optional[str]:
    if comment is None:
        return None
    ret_val = comment.content.strip()
    ret_val = ret_val.strip("\\n")
    ret_val = ret_val.strip("\n")
    ret_val = ret_val.strip(":")
    return ret_val


def parse_cell(
    cell: Cell, row_nr: int, column_nr: int, worksheet: Worksheet
) -> Expenditure:
    date = worksheet.cell(row=row_nr, column=COLUMN_DATE).value
    return Expenditure(
        value=float(cell.value),
        date=date,
        category=COLUMNS.get(column_nr),
        comment=sanitize_comment(cell.comment),
    )


def fetch_expendeitures(worksheets: List[Worksheet]) -> List[Expenditure]:
    expenditures = list()
    for worksheet in worksheets:
        for row_nr in ROWS:
            for column_nr in COLUMNS:
                if column_nr == COLUMN_DATE:  # skip date column
                    continue

                cell = worksheet.cell(row=row_nr, column=column_nr)
                if cell.value:
                    parsed_cell = parse_cell(cell, row_nr, column_nr, worksheet)
                    expenditures.append(parsed_cell)
    logging.info("Fetched %d expenditures", len(expenditures))
    return sorted(expenditures, key=lambda x: x.date)


def save_expenditures_to_csv(expenditures: List[Expenditure], file_path) -> None:
    with open(file_path, mode="w") as tobias_expenditures:
        writer = csv.writer(tobias_expenditures, delimiter=",")
        for e in expenditures:
            writer.writerow([e.date, e.value, e.category, e.comment])
    logging.info('Saved file: "%s"', file_path)


if __name__ == "__main__":
    file_path = get_filename_from_args()
    worksheets = get_worksheets(file_path)
    expenditures = fetch_expendeitures(worksheets)
    save_expenditures_to_csv(expenditures, "expenditures.csv")

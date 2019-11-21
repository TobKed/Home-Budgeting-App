"""Helper script to populate db from csv file."""
import argparse
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from autoapp import app
from python_scripts import expenditure
from python_scripts.execution_time import log_execution_time

from home_budgeting_app.expenditure.models import Category, Expenditure
from home_budgeting_app.extensions import db
from home_budgeting_app.user.models import User

logging.basicConfig(level=logging.INFO)

USER_ID: int = 1
MAIN_CATEGORIES: List[str] = [
    "Bills",
    "Food",
    "Cosmetics",
    "Medicines",
    "Domestic",
    "Clothes",
    "Party",
    "Sport",
    "School",
    "Other",
]

SUB_CATEGORIES: List[Tuple[str, str]] = [
    ("Flat", "Bills"),
    ("Other", "Bills"),
    ("Shop", "Food"),
    ("Restaurant", "Food"),
    ("Sweets", "Food"),
    ("Alcohol", "Food"),
    ("Mom", "Other"),
]

CATEGORIES_CATALOG: Dict[str, Category] = dict()


def get_filename_from_args() -> str:  # noqa: D103
    parser = argparse.ArgumentParser(description="Parse some budget files to db.")
    parser.add_argument(
        "filename", metavar="F", type=str, help="Budget csv filename to be parsed"
    )
    args = parser.parse_args()
    return args.filename


def create_main_categories(user_id: int = USER_ID) -> None:  # noqa: D103
    for category_name in MAIN_CATEGORIES:
        category = Category.query.filter_by(
            user_id=user_id, label=category_name
        ).first()
        if category:
            logging.info("Category found: %s", category_name)
        else:
            Category.create(user_id=user_id, label=category_name)
            logging.info("Category not found, created: %s", category_name)


def create_sub_categories() -> None:  # noqa: D103
    for category_name, parent_category_name in SUB_CATEGORIES:
        parent_category = Category.query.filter_by(
            user_id=USER_ID, label=parent_category_name
        ).first()

        category = Category.query.filter_by(
            user_id=USER_ID, label=category_name, parent_id=parent_category.id
        ).first()

        if not parent_category:
            raise Exception(
                f'Houston, we have problem. No category "{parent_category_name}" found'
            )

        if category:
            logging.info(
                "Category found: %s (parent: %s)", category_name, parent_category_name
            )
        else:
            Category.create(
                user_id=USER_ID, label=category_name, parent_id=parent_category.id
            )
            logging.info(
                "Category not found, created: %s (parent: %s)",
                category_name,
                parent_category_name,
            )


def date_from_string(date_time_str: str) -> datetime:  # noqa: D103
    return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")


def read_expenditures_from_csv(
    file: str,
) -> List[expenditure.Expenditure]:  # noqa: D103
    expenditures = list()
    with open(file, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            date = date_from_string(row[0])
            value = float(row[1])
            category = row[2]
            comment = row[3] or None
            e = expenditure.Expenditure(
                date=date, value=value, category=category, comment=comment
            )
            expenditures.append(e)

    logging.info("Read %d expenditures", len(expenditures))
    return sorted(expenditures, key=lambda x: x.date)


def find_category(
    category_name: str, parent_category_id: Optional[int] = None
) -> Category:  # noqa: D103
    """Match category from csv with category from DB."""
    if "-" in category_name:
        main_category_name, sub_category_name = category_name.split("-", 1)
        main_category_name, sub_category_name = (
            main_category_name.capitalize(),
            sub_category_name.capitalize(),
        )

        main_category = Category.query.filter_by(
            user_id=USER_ID, label=main_category_name, parent_id=parent_category_id
        ).first()
        if main_category:
            return find_category(sub_category_name, main_category.id)
        else:
            raise Exception("Oy oy!")

    category_name = category_name.capitalize()
    return Category.query.filter_by(
        user_id=USER_ID, label=category_name, parent_id=parent_category_id
    ).first()


def _translate_basic_to_db_expenditure(
    basic_expenditure: expenditure.Expenditure,
) -> Expenditure:  # noqa: D103
    category_name = basic_expenditure.category

    # to avoid hitting db constantly
    if category_name not in CATEGORIES_CATALOG:
        category = find_category(category_name=category_name)
        CATEGORIES_CATALOG[category_name] = category
    category = CATEGORIES_CATALOG[category_name]

    return Expenditure(
        user_id=USER_ID,
        value=basic_expenditure.value,
        comment=basic_expenditure.comment,
        category=category.id,
        spent_at=basic_expenditure.date,
    )


def translate_basic_to_db_expenditures(
    basic_expenditures: List[expenditure.Expenditure],
) -> List[Expenditure]:  # noqa: D103
    db_expenditures = list()
    for e in basic_expenditures:
        db_e = _translate_basic_to_db_expenditure(e)
        db_expenditures.append(db_e)

    return db_expenditures


@log_execution_time
def save_db_expenditures_to_db(expenditures: List[Expenditure]) -> None:  # noqa: D103
    e_to_be_saved, e_to_be_skipped = list(), list()
    for e in expenditures:
        if Expenditure.query.filter_by(
            user_id=e.user_id,
            spent_at=e.spent_at,
            value=e.value,
            comment=e.comment,
            category=e.category,
        ).first():
            e_to_be_skipped.append(e)
        else:
            e_to_be_saved.append(e)

    logging.info("Expenditures skipped: %d", len(e_to_be_skipped))

    session = db.session()
    session.bulk_save_objects(e_to_be_saved)
    session.commit()
    logging.info("Expenditures saved: %d", len(e_to_be_saved))


if __name__ == "__main__":
    app.app_context().push()

    file = get_filename_from_args()

    user = User.get_by_id(USER_ID)
    logging.info("Fetched user: %s", user)
    nr_of_user_expenditures_start = user.expenditures.count()

    create_main_categories()
    create_sub_categories()

    basic_expenditures = read_expenditures_from_csv(file)
    db_expenditures = translate_basic_to_db_expenditures(basic_expenditures)

    save_db_expenditures_to_db(db_expenditures)

    nr_of_user_expenditures_end = user.expenditures.count()
    logging.info(
        "User expenditures at the beelining: %d", nr_of_user_expenditures_start
    )
    logging.info("User expenditures at the end: %d", nr_of_user_expenditures_end)

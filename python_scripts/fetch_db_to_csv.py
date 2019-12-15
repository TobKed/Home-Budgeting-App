import argparse
import csv
import logging
from typing import List, Tuple

from autoapp import app
from python_scripts.execution_time import log_execution_time

from home_budgeting_app.expenditure.models import Category, Expenditure
from home_budgeting_app.extensions import db
from home_budgeting_app.user.models import User

logging.basicConfig(level=logging.INFO)

USER_ID: int = 1


def get_filename_from_args() -> str:  # noqa: D103
    parser = argparse.ArgumentParser(description="Parse budget from db to csv.")
    parser.add_argument(
        "filename", metavar="f", type=str, help="Budget csv filename to be parsed"
    )
    args = parser.parse_args()
    return args.filename


def get_expenditures() -> List[Expenditure]:
    return (
        db.session.query(Expenditure)
        .filter(Expenditure.user_id == USER_ID)
        .order_by(Expenditure.spent_at)
    ).all()


def get_categories_path(category: Category) -> str:
    return "-".join([c.label for c in category.path_to_root().all()][::-1]).lower()


def save_expenditures_to_csv(
    expenditures: List[Expenditure], file
) -> None:  # noqa: D103
    with open(file, mode="w") as f:
        writer = csv.writer(f, delimiter=",")
        total = len(expenditures)
        for i, e in enumerate(expenditures):
            category_path = get_categories_path(e.category)
            writer.writerow([e.spent_at, e.value, category_path, e.comment])
            print(f"{i:>10}/{total} - {e.value:>6}-{e.spent_at} (path:{category_path}")
    logging.info('Saved file: "%s"', file)


@log_execution_time
def main(file):
    app.app_context().push()

    user = User.get_by_id(USER_ID)
    if not user:
        raise Exception(f"User with id '{USER_ID}' not found!")
    logging.info("Fetched user: %s", user)

    expenditures = get_expenditures()
    save_expenditures_to_csv(expenditures, file)


if __name__ == "__main__":
    file = get_filename_from_args()

    main(file=file)

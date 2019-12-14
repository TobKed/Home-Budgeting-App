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

USER_ID: int = 2


def get_filename_from_args() -> str:  # noqa: D103
    parser = argparse.ArgumentParser(description="Parse budget from db to csv.")
    parser.add_argument(
        "filename", metavar="f", type=str, help="Budget csv filename to be parsed"
    )
    args = parser.parse_args()
    return args.filename


def get_expenditures() -> List[Tuple[Expenditure, Category]]:
    return (
        db.session.query(Expenditure, Category)
        .filter(Expenditure.user_id == USER_ID)
        .join(Category)
        .order_by(Expenditure.spent_at)
    ).all()


def get_categories_path(category: Category) -> str:
    return "-".join([c.label for c in category.path_to_root().all()][::-1]).lower()


def save_expenditures_to_csv(
    expenditures_categories: List[Tuple[Expenditure, Category]], file
) -> None:  # noqa: D103
    with open(file, mode="w") as f:
        writer = csv.writer(f, delimiter=",")
        total = len(expenditures_categories)
        for i, (e, c) in enumerate(expenditures_categories):
            writer.writerow([e.spent_at, e.value, get_categories_path(c), e.comment])
            print(f"{i:>10}/{total}")
    logging.info('Saved file: "%s"', file)


@log_execution_time
def main(file):
    app.app_context().push()

    user = User.get_by_id(USER_ID)
    if not user:
        raise Exception(f"User with id '{USER_ID}' not found!")
    logging.info("Fetched user: %s", user)

    expenditures_categories = get_expenditures()
    save_expenditures_to_csv(expenditures_categories, file)


if __name__ == "__main__":
    file = get_filename_from_args()

    main(file=file)

# -*- coding: utf-8 -*-
"""Expenditure views."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from .models import Category
from .service import add_expenditures_cumulative_count

blueprint = Blueprint(
    "expenditure", __name__, url_prefix="/expenditures", static_folder="../static"
)


@blueprint.route("/categories")
@login_required
def categories():
    """List categories."""
    categories_raw = [
        category.drilldown_tree()
        for category in Category.query.filter_by(
            user_id=current_user.id, parent_id=None
        ).all()
    ]
    correct_length = all(len(cat) == 1 for cat in categories_raw)
    if not correct_length:
        raise ValueError("Wrong structure of categories")

    categories = [cat[0] for cat in categories_raw]
    for category in categories:
        add_expenditures_cumulative_count(category)

    return render_template("expenditures/categories.html", categories=categories)

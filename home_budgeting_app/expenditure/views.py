# -*- coding: utf-8 -*-
"""Expenditure views."""
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from .models import Category, Expenditure
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


@blueprint.route("/expenditures")
@login_required
def expenditures():
    """List expenditures."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        Expenditure.query.filter(Expenditure.user_id == current_user.id)
        .order_by(Expenditure.spent_at.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("expenditures/expenditures.html", pagination=pagination)

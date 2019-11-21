# -*- coding: utf-8 -*-
"""Expenditure views."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from .models import Category

blueprint = Blueprint(
    "expenditure", __name__, url_prefix="/expenditures", static_folder="../static"
)


@blueprint.route("/categories")
@login_required
def categories():
    """List categories."""
    categories = Category.query.filter_by(user_id=current_user.id, parent_id=None)
    return render_template("expenditures/categories.html", categories=categories)

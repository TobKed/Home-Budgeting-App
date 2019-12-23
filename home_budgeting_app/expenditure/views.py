# -*- coding: utf-8 -*-
"""Expenditure views."""
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .forms import ExpenditureForm
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


@blueprint.route("/")
@login_required
def expenditures():
    """List expenditures."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        Expenditure.query.filter(Expenditure.user_id == current_user.id)
        .order_by(Expenditure.spent_at.desc())
        .paginate(page=page, per_page=10000)
    )
    return render_template("expenditures/expenditures.html", pagination=pagination)


@blueprint.route("/<int:exp_id>")
def expenditure_detail_view(exp_id):
    expenditure = Expenditure.get_by_id(exp_id)
    if not expenditure or expenditure.user_id != current_user.id:
        abort(404)
    referrer = request.referrer
    return render_template(
        "expenditures/expenditures-detail-view.html",
        expenditure=expenditure,
        referrer=referrer,
    )


@blueprint.route("/add", methods=["GET", "POST"])
def expenditure_add_view():
    view_name = "Add"
    form = ExpenditureForm()
    categories = (
        Category.query.filter(Category.user_id == current_user.id)
        .order_by(Category.expenditures_count.desc())
        .all()
    )
    choices = [(cat.id, "-".join(cat.path)) for cat in categories]
    form.category.choices = choices

    if form.validate_on_submit():
        expenditure = Expenditure.create(
            user_id=current_user.id,
            value=form.value.data,
            spent_at=form.spent_at.data,
            comment=form.comment.data,
            category_id=form.category.data,
            created_at=datetime.today(),
        )
        flash("Your post has been saved!", "success")
        return redirect(
            url_for("expenditure.expenditure_detail_view", exp_id=expenditure.id)
        )

    return render_template(
        "expenditures/expenditures-detail-edit.html", form=form, view_name=view_name
    )

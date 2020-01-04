# -*- coding: utf-8 -*-
"""Expenditure views."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .forms import ExpenditureForm
from .models import Category, Expenditure, get_by_id_for_current_user_or_abort
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
@login_required
def expenditure_detail(exp_id):
    expenditure = get_by_id_for_current_user_or_abort(Expenditure, exp_id)
    return render_template(
        "expenditures/expenditures_detail_view.html",
        expenditure=expenditure,
        exp_id=expenditure.id,
    )


@blueprint.route("/add", methods=["GET", "POST"])
@login_required
def expenditure_add():
    view_name = "Add"
    form = ExpenditureForm()

    if form.validate_on_submit():
        expenditure = Expenditure.create(
            user_id=current_user.id,
            value=form.value.data,
            spent_at=form.spent_at.data,
            comment=form.comment.data,
            category_id=form.category.data,
            created_at=datetime.today(),
        )
        flash("Your expenditure has been saved!", "success")
        return redirect(
            url_for("expenditure.expenditure_detail", exp_id=expenditure.id)
        )

    return render_template(
        "expenditures/expenditures_detail_edit.html",
        form=form,
        view_name=view_name,
        exp_id=None,
    )


@blueprint.route("<int:exp_id>/edit", methods=["GET", "POST"])
@login_required
def expenditure_edit(exp_id):
    expenditure = get_by_id_for_current_user_or_abort(Expenditure, exp_id)
    view_name = "Update"
    form = ExpenditureForm()

    if form.validate_on_submit():
        expenditure.update(
            user_id=current_user.id,
            value=form.value.data,
            spent_at=form.spent_at.data,
            comment=form.comment.data,
            category_id=form.category.data,
        )
        flash("Your expenditure has been updated!", "success")
        return redirect(
            url_for("expenditure.expenditure_detail", exp_id=expenditure.id)
        )
    elif request.method == "GET":
        form.value.data = expenditure.value
        form.spent_at.data = expenditure.spent_at
        form.comment.data = expenditure.comment
        form.category.data = expenditure.category_id

    return render_template(
        "expenditures/expenditures_detail_edit.html",
        form=form,
        view_name=view_name,
        exp_id=expenditure.id,
    )


@blueprint.route("<int:exp_id>/delete", methods=["POST"])
@login_required
def expenditure_delete(exp_id):
    expenditure = get_by_id_for_current_user_or_abort(Expenditure, exp_id)
    expenditure.delete()
    flash("Your expenditure has been deleted!", "success")
    return redirect(url_for("expenditure.expenditures"))

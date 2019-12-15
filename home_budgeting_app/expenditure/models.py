# -*- coding: utf-8 -*-
"""Expenditure models."""
import datetime as dt
from typing import List

from cached_property import cached_property
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import column_property
from sqlalchemy_mptt.mixins import BaseNestedSets

from home_budgeting_app.database import Column, Model, SurrogatePK
from home_budgeting_app.extensions import db


class Expenditure(SurrogatePK, Model):
    """A expenditure of the user."""

    __tablename__ = "expenditures"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    value = Column(db.Float(), nullable=False)
    spent_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    comment = Column(db.Text(), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self):  # noqa: D105
        return (
            f"Expenditure(value={self.value}, spent_at={self.spent_at}, comment='{self.comment}', "
            f"category={self.category}, user_id={self.user_id})"
        )


class Category(SurrogatePK, Model, BaseNestedSets):
    """A category of the expenditure."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = Column(db.String(128))
    expenditures = db.relationship("Expenditure", backref="category", lazy=True)
    expenditures_count = column_property(
        select([func.count(Expenditure.id)])
        .where(Expenditure.category_id == id)
        .correlate_except(Expenditure)
    )

    @cached_property
    def path(self) -> List[str]:
        """Returns list of the categories starting from root"""
        return [c.label for c in self.path_to_root().all()][::-1]

    def save(self, *args, **kwargs):
        """Save the record and prevent the same subcategory within category."""
        if self.query.filter_by(
            user_id=self.user_id, label=self.label, parent_id=self.parent_id
        ).first():
            raise SQLAlchemyError(
                f"Error when creating {self}. "
                f"There cannot be two cannot be be two categories with the same name and the same parent."
            )
        return super().save(*args, **kwargs)

    def __repr__(self):  # noqa: D105
        return f"Category(label='{self.label}', user_id={self.user_id}, parent_id={self.parent_id})"

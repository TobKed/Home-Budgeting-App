# -*- coding: utf-8 -*-
"""Expenditure models."""
import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from home_budgeting_app.database import Column, Model, SurrogatePK, relationship
from home_budgeting_app.extensions import db


class Category(SurrogatePK, Model):
    """A category of the expenditure."""

    __tablename__ = "categories"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = Column(db.String(128))
    parent_id = Column(db.Integer, db.ForeignKey("categories.id"))
    children = relationship(
        "Category", lazy="dynamic"
    )  # lazy="dynamic" / "joined" , join_depth=2
    expenditures = db.relationship("Expenditure", backref="expenditures", lazy=True)

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


class Expenditure(SurrogatePK, Model):
    """A expenditure of the user."""

    __tablename__ = "expenditures"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    value = Column(db.Float(), nullable=False)
    spent_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    comment = Column(db.Text(), nullable=True)
    category = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self):  # noqa: D105
        return (
            f"Expenditure(value={self.value}, spent_at={self.spent_at}, comment='{self.comment}', "
            f"category={self.category}, user_id={self.user_id})"
        )

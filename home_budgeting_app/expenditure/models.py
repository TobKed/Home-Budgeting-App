# -*- coding: utf-8 -*-
"""Expenditure models."""
import datetime as dt

from home_budgeting_app.database import Column, Model, SurrogatePK, relationship
from home_budgeting_app.extensions import db


class Category(SurrogatePK, Model):
    """A category of the expenditure."""

    __tablename__ = "categories"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = Column(db.String(128))
    parent_id = Column(db.Integer, db.ForeignKey("categories.id"))
    children = relationship("Category", lazy="joined", join_depth=2)  # lazy="dynamic"
    expenditures = db.relationship("Expenditure", backref="expenditures", lazy=True)

    def __repr__(self):
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

    def __repr__(self):
        return (
            f"Expenditure(value={self.value}, spent_at={self.spent_at}, comment='{self.comment}', "
            f"category={self.category}, user_id={self.user_id})"
        )

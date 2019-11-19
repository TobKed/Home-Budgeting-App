# -*- coding: utf-8 -*-
"""Expenditure views."""
from flask import Blueprint

from . import models  # noqa

blueprint = Blueprint(
    "expenditure", __name__, url_prefix="/expenditures", static_folder="../static"
)

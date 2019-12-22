# -*- coding: utf-8 -*-
"""Test forms."""
from datetime import datetime

from home_budgeting_app.expenditure.forms import ExpenditureForm


class TestExpenditureForm:
    """Expenditure form."""

    def test_expenditure_save_success(self, user):
        """Enter new expenditure."""

        form = ExpenditureForm(
            value=10.0, spent_at=datetime.today(), comment="No comment", category=1
        )
        form.category.choices = [(1, 1)]
        assert form.validate() is True

# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import Sequence
from tests.factories import BaseFactory

from home_budgeting_app.expenditure.models import Category, Expenditure


class CategoryFactory(BaseFactory):
    """Category factory."""

    label = Sequence(lambda n: "Category label{0}".format(n))

    class Meta:
        """Factory configuration."""

        model = Category


class ExpenditureFactory(BaseFactory):
    """Expenditure factory."""

    user_id = Sequence(lambda n: n + 1)
    value = Sequence(lambda n: n + 1)
    category_id = Sequence(lambda n: n + 1)

    class Meta:
        """Factory configuration."""

        model = Expenditure

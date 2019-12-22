# -*- coding: utf-8 -*-
"""Model unit tests."""
from home_budgeting_app.expenditure.models import Category, Expenditure

from .factories import CategoryFactory, ExpenditureFactory


class TestCategory:
    """Category tests."""

    def test_get_by_id(self, user):
        """Get Category by ID."""
        category = Category(user_id=user.id, label="Category 1")
        category.save()

        retrieved = Category.get_by_id(category.id)

        assert retrieved == category

    def test_factory(self, db):
        """Test category factory."""
        category = CategoryFactory(user_id=1)
        db.session.commit()
        assert bool(category.label)
        assert category.user_id == 1


class TestExpenditure:
    """Expenditure tests."""

    def test_get_by_id(self, user):
        """Get Category by ID."""
        expenditure = Expenditure(user_id=user.id, value="111", category_id=1)
        expenditure.save()

        retrieved = Expenditure.get_by_id(expenditure.id)

        assert retrieved == expenditure

    def test_factory(self, db):
        """Test expenditure factory."""
        expenditure = ExpenditureFactory(user_id=1)
        db.session.commit()
        assert bool(expenditure.value)
        assert bool(expenditure.user_id)
        assert bool(expenditure.category_id)

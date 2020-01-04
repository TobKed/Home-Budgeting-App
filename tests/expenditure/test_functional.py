# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for
from tests.expenditure.factories import CategoryFactory


def login(client, email, password):
    res = client.post(
        url_for("public.home"), params=dict(email=email, password=password)
    )
    assert res.follow().status_code == 200
    return res


def logout(client):
    res = client.get(url_for("public.home"))
    assert res.status_code == 200
    return res


class TestAddingExpenditure:
    """Add new expenditure."""

    def test_add_expenditure(self, user, testapp, db):
        """Add a new expenditure."""

        login(testapp, user.email, "myprecious")

        CategoryFactory(user_id=user.id)
        db.session.commit()

        res = testapp.get(url_for("expenditure.expenditure_add"))
        form = res.forms["expenditureForm"]
        form["value"] = 123
        form["spent_at"] = "2019-12-22T20:20"
        form["comment"] = "test comment"
        form["category"] = 1

        res = form.submit().follow()
        assert res.status_code == 200

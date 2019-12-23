# -*- coding: utf-8 -*-
"""Test service."""

from home_budgeting_app.expenditure.service import add_expenditures_cumulative_count


class FakeCategory:
    def __init__(self, node: str, expenditures_count: int = 0) -> None:
        self.node = node
        self.expenditures_count = expenditures_count

    def __repr__(self):
        return self.node

    @classmethod
    def get_fake_drilldown_tree(cls):
        return {
            "children": [
                {
                    "children": [
                        {
                            "children": [{"node": cls("<Category baz>", 3)}],
                            "node": cls("<Category bar>"),
                        }
                    ],
                    "node": cls("<Category foo>", 4),
                },
                {
                    "children": [
                        {"node": cls("<Category bar1>", 1)},
                        {"node": cls("<Category baz1>", 2)},
                    ],
                    "node": cls("<Category foo1>"),
                },
            ],
            "node": cls("<Category root>"),
        }


class TestExpendituresCumulativeCount:
    """Test add_expenditures_cumulative_count."""

    def test_expenditures_cumulative_count_green_path(self):
        """Basic add_expenditures_cumulative_count."""
        drilldown_tree = FakeCategory.get_fake_drilldown_tree()
        add_expenditures_cumulative_count(drilldown_tree)

        root = drilldown_tree["node"]
        foo = drilldown_tree["children"][0]["node"]
        bar = drilldown_tree["children"][0]["children"][0]["node"]
        baz = drilldown_tree["children"][0]["children"][0]["children"][0]["node"]
        foo1 = drilldown_tree["children"][1]["node"]
        bar1 = drilldown_tree["children"][1]["children"][0]["node"]
        baz1 = drilldown_tree["children"][1]["children"][1]["node"]

        assert root.node == "<Category root>"
        assert foo.node == "<Category foo>"
        assert bar.node == "<Category bar>"
        assert baz.node == "<Category baz>"
        assert foo1.node == "<Category foo1>"
        assert bar1.node == "<Category bar1>"
        assert baz1.node == "<Category baz1>"

        assert root.expenditures_cumulative_count == 10
        assert foo.expenditures_cumulative_count == 7
        assert bar.expenditures_cumulative_count == 3
        assert baz.expenditures_cumulative_count == 3
        assert foo1.expenditures_cumulative_count == 3
        assert bar1.expenditures_cumulative_count == 1
        assert baz1.expenditures_cumulative_count == 2

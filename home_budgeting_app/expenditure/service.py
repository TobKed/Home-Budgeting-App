"""Logic for expenditures."""
from typing import Dict, List, Union


def add_expenditures_cumulative_count(category_tree: Dict) -> None:
    """Add cumulative_count attribute to categories in category tree."""

    def _get_all_children_expenditure_counts(children: Union[List[Dict], None]) -> int:
        value = 0
        if children:
            for child in children:
                category = child["node"]
                value += category.expenditures_count
                category_children = child.get("children")
                value += _get_all_children_expenditure_counts(category_children)
        return value

    category = category_tree["node"]
    category_children = category_tree.get("children", [])
    children_count = (
        _get_all_children_expenditure_counts(category_children)
        if category_children
        else 0
    )
    category.expenditures_cumulative_count = (
        category.expenditures_count + children_count
    )
    for child in category_children:
        add_expenditures_cumulative_count(child)

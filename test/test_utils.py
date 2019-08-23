import sys

import pytest
import utils


sys.path.insert(0, "lib")


addon_order = [
    (["a", "b", "c"], ["a", "b", "c"], ""),
    (["c", "b", "a"], ["a", "b", "c"], ""),
    (["c", "a", "b"], ["a", "b", "c"], ""),
    (
        ['"b",', '"a",', '"aldryn-addons",', '"aldryn-django-cms",'],
        ['"aldryn-addons",', '"aldryn-django-cms",', '"a",', '"b",'],
        '"',
    ),
    (
        ['"b",', '"aldryn-django-cms",', '"a",', '"aldryn-addons",'],
        ['"aldryn-addons",', '"aldryn-django-cms",', '"a",', '"b",'],
        '"',
    ),
    (
        ["'b',", "'aldryn-django-cms',", "'a',", "'aldryn-addons',"],
        ["'aldryn-addons',", "'aldryn-django-cms',", "'a',", "'b',"],
        "'",
    ),
]


@pytest.mark.parametrize("input, expected, quote", addon_order)
def test_sort_addons(input, expected, quote):
    assert expected == utils.sort_addons(input, quotation=quote)

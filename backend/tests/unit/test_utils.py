import os

import pytest

from infrahub.utils import (
    compare_lists,
    deep_merge_dict,
    duplicates,
    get_fixtures_dir,
    str_to_bool,
)


def test_duplicates():
    assert duplicates([2, 4, 6, 8, 4, 6, 12]) == [4, 6]
    assert duplicates(["first", "second", "first", "third", "first", "last"]) == ["first"]
    assert duplicates([2, 8, 4, 6, 12]) == []


def test_get_fixtures_dir():
    assert os.path.exists(get_fixtures_dir())


def test_compare_lists():
    list_a = ["black", "blue", "red"]
    list_b = ["black", "green"]
    list_c = ["purple", "yellow"]

    both, in1, in2 = compare_lists(list_a, list_b)
    assert both == ["black"]
    assert in1 == ["blue", "red"]
    assert in2 == ["green"]

    both, in1, in2 = compare_lists(list_c, list_b)
    assert both == []
    assert in1 == list_c
    assert in2 == list_b

    both, in1, in2 = compare_lists(list_c, ["yellow"])
    assert both == ["yellow"]
    assert in1 == ["purple"]
    assert in2 == []


def test_deep_merge_dict():
    a = {"keyA": 1}
    b = {"keyB": {"sub1": 10}}
    c = {"keyB": {"sub2": 20}}
    assert deep_merge_dict(a, b) == {"keyA": 1, "keyB": {"sub1": 10}}
    assert deep_merge_dict(c, b) == {"keyB": {"sub1": 10, "sub2": 20}}


def test_str_to_bool():
    assert str_to_bool(True) is True
    assert str_to_bool(False) is False

    assert str_to_bool(1) is True
    assert str_to_bool(0) is False

    assert str_to_bool("True") is True
    assert str_to_bool("TRUE") is True
    assert str_to_bool("Yes") is True
    assert str_to_bool("yes") is True
    assert str_to_bool("1") is True
    assert str_to_bool("on") is True
    assert str_to_bool("y") is True

    assert str_to_bool("No") is False
    assert str_to_bool("False") is False
    assert str_to_bool("f") is False

    with pytest.raises(ValueError):
        str_to_bool("NotABool")

    with pytest.raises(TypeError):
        str_to_bool(tuple("a", "b", "c"))

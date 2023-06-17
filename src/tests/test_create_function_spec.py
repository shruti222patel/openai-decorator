from typing import List, Optional

import pytest

from openai_decorator.main import create_function_spec


def test_create_function_spec_no_params():
    def func_no_params():
        """
        A function with no parameters.
        """
        pass

    spec = create_function_spec(func_no_params)
    assert spec["name"] == "func_no_params"
    assert spec["description"] == "A function with no parameters."
    assert spec["parameters"]["properties"] == {}
    assert spec["parameters"]["required"] == []


def test_create_function_spec_required_params():
    def func_required_params(a: int, b: str):
        """
        A function with required parameters.

        Args:
            a (int): The first argument.
            b (str): The second argument.
        """
        pass

    spec = create_function_spec(func_required_params)
    assert spec["name"] == "func_required_params"
    assert spec["description"] == "A function with required parameters."
    assert spec["parameters"]["properties"] == {
        "a": {"type": "number", "description": "The first argument."},
        "b": {"type": "string", "description": "The second argument."},
    }
    assert spec["parameters"]["required"] == ["a", "b"]


def test_create_function_spec_mixed_params():
    def func_mixed_params(
        a: int, b: List[str], c: float = 3.0, d: Optional[str] = None
    ):
        """
        A function with mixed parameters.

        Args:
            a (int): The first argument.
            b (List[str]): The second argument.
            c (float, optional): The third argument with a default value.
            d (Optional[str], optional): The fourth argument with a default value.
        """
        pass

    spec = create_function_spec(func_mixed_params)
    assert spec["name"] == "func_mixed_params"
    assert spec["description"] == "A function with mixed parameters."
    assert spec["parameters"]["properties"] == {
        "a": {"type": "number", "description": "The first argument."},
        "b": {"type": "array", "description": "The second argument."},
        "c": {
            "type": "number",
            "description": "The third argument with a default value.",
        },
        "d": {
            "type": "string",
            "description": "The fourth argument with a default value.",
        },
    }
    assert spec["parameters"]["required"] == ["a", "b"]


def test_create_function_spec_no_type_annotation():
    def func_no_type_annotation(a, b="default"):
        """
        A function with no type annotation.

        Args:
            a: The first argument.
            b: The second argument.
        """
        pass

    with pytest.raises(TypeError):
        create_function_spec(func_no_type_annotation)

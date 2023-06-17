import json

import pytest

from openai_decorator.main import get_arguments_from_response


def test_get_arguments_from_response_valid_response():
    response = {
        "choices": [
            {
                "message": {
                    "function_call": {
                        "name": "test_func",
                        "arguments": '{"arg1": "value1", "arg2": "value2"}',
                    }
                }
            }
        ]
    }

    func_name, arguments = get_arguments_from_response(response)

    assert func_name == "test_func"
    assert arguments == {"arg1": "value1", "arg2": "value2"}


def test_get_arguments_from_response_no_choices():
    response = {}

    func_name, arguments = get_arguments_from_response(response)

    assert func_name is None
    assert arguments is None


def test_get_arguments_from_response_empty_choices():
    response = {"choices": []}

    func_name, arguments = get_arguments_from_response(response)

    assert func_name is None
    assert arguments is None


def test_get_arguments_from_response_invalid_arguments():
    response = {
        "choices": [
            {
                "message": {
                    "function_call": {
                        "name": "test_func",
                        "arguments": "{arg1: value1, arg2: value2}",  # Invalid JSON string
                    }
                }
            }
        ]
    }

    with pytest.raises(json.JSONDecodeError):
        get_arguments_from_response(response)

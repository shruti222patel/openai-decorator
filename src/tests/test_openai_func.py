from unittest.mock import Mock, patch

import pytest

from openai_decorator.main import openai_func


def test_openai_func():
    # Mocked response
    mocked_response = "mocked response"

    # Mocked function arguments
    mocked_arguments = {"arg1": "value1", "arg2": "value2"}

    with patch(
        "openai_decorator.main.generate_parameters", return_value=mocked_response
    ) as mock_gen_params, patch(
        "openai_decorator.main.get_arguments_from_response",
        return_value=("func", mocked_arguments),
    ) as mock_get_args:

        @openai_func("prompt")
        def func(arg1, arg2):
            return arg1, arg2

        # Assert the decorated function works correctly
        assert func() == ("value1", "value2")

        # Assert generate_parameters is called with the correct arguments
        # Get the function passed to generate_parameters -- this is because the decorator changes ghe function
        expected_func = mock_gen_params.call_args[1]["func"]
        mock_gen_params.assert_called_once_with(
            "prompt", func=expected_func, model="gpt-3.5-turbo-0613", temperature=0
        )

        # Assert get_arguments_from_response is called with the correct argument
        mock_get_args.assert_called_once_with(mocked_response)


def test_openai_func_callable_prompt():
    # Define a callable prompt
    def callable_prompt():
        return "This is a callable prompt"

    # Mocked response
    mocked_response = "mocked response"

    # Mocked function arguments
    mocked_arguments = {"arg1": "value1", "arg2": "value2"}

    with patch(
        "openai_decorator.main.generate_parameters", return_value=mocked_response
    ) as mock_gen_params, patch(
        "openai_decorator.main.get_arguments_from_response",
        return_value=("func", mocked_arguments),
    ) as mock_get_args:
        # Define a function to be decorated
        @openai_func(prompt=callable_prompt, model="gpt-3.5-turbo-0613", temperature=0)
        def func(arg1, arg2):
            return arg1, arg2

        # Assert the expected result
        assert func() == ("value1", "value2")

        # Assert generate_parameters is called with the correct arguments
        # Get the function passed to generate_parameters -- this is because the decorator changes ghe function
        expected_func = mock_gen_params.call_args[1]["func"]
        mock_gen_params.assert_called_once_with(
            "This is a callable prompt",
            func=expected_func,
            model="gpt-3.5-turbo-0613",
            temperature=0,
        )

        # Assert get_arguments_from_response is called with the correct argument
        mock_get_args.assert_called_once_with(mocked_response)

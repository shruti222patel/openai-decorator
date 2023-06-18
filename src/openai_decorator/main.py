import inspect
import json
import os
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import openai as openai
from docstring_parser import parse
from docstring_parser.common import Docstring
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Set your OpenAI API key and the model
openai.api_key = os.environ.get("OPENAI_API_KEY", None)


def get_parsed_docstring(func: Callable[..., Any]) -> Docstring:
    docstring = func.__doc__
    if not docstring:
        raise ValueError(f"{func.__name__} has no docstring.")
    parsed = parse(docstring)
    return parsed


def create_function_spec(func: Callable[..., Any]) -> Dict[str, Any]:
    signature = inspect.signature(func)
    parameters = signature.parameters

    parsed_docstring = get_parsed_docstring(func)

    properties = {}
    type_hints = get_type_hints(func)
    for param in parsed_docstring.params:
        python_type = type_hints.get(param.arg_name)
        if python_type is None:
            raise TypeError(f"Missing type annotation for parameter: {param.arg_name}")
        properties[param.arg_name] = {
            "type": get_json_property_type(python_type),
            "description": param.description,
        }

    required_params = [
        name
        for name, param in parameters.items()
        if param.default == inspect.Parameter.empty
        and not is_param_optional(type_hints.get(name))
    ]

    spec = {
        "name": func.__name__,
        "description": parsed_docstring.short_description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required_params,
        },
    }
    return spec


def is_param_optional(python_type: Any) -> bool:
    origin = get_origin(python_type)
    # Checks if the type is Optional[T] or Union[T, None]
    return origin is Union and type(None) in get_args(python_type)


def get_json_property_type(python_type: Any) -> str:
    type_map = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        set: "array",
        tuple: "array",
    }

    # If it's a base type, return the corresponding JSON Schema type
    if python_type in type_map:
        return type_map[python_type]
    elif python_type is Any:
        raise TypeError("Type annotation 'Any' is not supported")
    else:
        # Get the base of the generic type (e.g., Optional, List)
        origin = get_origin(python_type)
        if origin in type_map:
            return type_map[origin]
        elif origin is Union and type(None) in get_args(
            python_type
        ):  # Check if it's an Optional type
            # Optional type is represented as its first argument type
            return get_json_property_type(get_args(python_type)[0])
        else:
            print(f"Unsupported type annotation: {python_type}, defaulting to 'object'")
            return "object"


def openai_func(
    prompt: Union[str, Callable[[], str]],
    model: str = "gpt-3.5-turbo-0613",
    temperature: int = 0,
):
    def decorator(func: Callable[..., Any]):
        """A decorator to read the docstring of a function it wraps,
        create a JSON spec, and call OpenAI API."""

        nonlocal prompt
        # Call the prompt if it is a callable
        if callable(prompt):
            prompt = prompt()

        # Call the chat_completion_request
        response = generate_parameters(
            prompt, func=func, model=model, temperature=temperature
        )

        # TODO -- log message from openai

        func_name, arguments = get_arguments_from_response(response)
        if func_name is None or arguments is None:
            raise ValueError(
                f"Failed to get a parsable response from openai: {response}"
            )
        if func_name != func.__name__:
            raise ValueError(
                f"Function name from the code {func_name} does not match the name returned by OpenAi {func.__name__}"
            )
        if arguments is None:
            raise ValueError(f"Failed to get arguments from the response.")

        # Create the function that will replace the original decorated function
        def replacement_func():
            return func(**arguments)

        return replacement_func

    return decorator


def get_arguments_from_response(response: Dict[str, Any]) -> (str, Dict[str, Any]):
    if "choices" in response and response["choices"]:
        function_call = (
            response["choices"][0].get("message", {}).get("function_call", {})
        )
        func_name = function_call.get("name")
        arguments_str = function_call.get("arguments", {})
        arguments = json.loads(arguments_str)
        return func_name, arguments
    else:
        return None, None


def generate_parameters(
    prompt: str, func: Callable[..., Any], model, temperature
) -> (List[Dict[str, str]], Dict[str, Any], Dict[str, Any], str, int):
    messages = [
        {
            "role": "system",
            "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
        },
        {"role": "user", "content": prompt},
    ]
    functions = [create_function_spec(func)]
    function_call = {"name": func.__name__}

    return run_openai_chatcompletion(
        messages, functions, function_call, model, temperature
    )


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def run_openai_chatcompletion(messages, functions, function_call, model, temperature):
    if messages is None:
        raise ValueError("You must pass messages to generate_parameters")
    if functions is None:
        raise ValueError(
            "You must pass an array of function specs to generate_parameters"
        )
    if function_call is None:
        raise ValueError("You must pass a function call to generate_parameters")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call=function_call,
            temperature=temperature,
        )
        return response  # Parse the JSON response
    except Exception as e:
        raise e


if __name__ == "__main__":

    @openai_func("Create a greeting message for a new computer program.")
    def hello_world(name: Optional[str] = "world"):
        """
        A simple function that returns a greeting message.

        Args:
            name (str): The name to greet.

        Returns:
            str: A greeting message.
        """
        return f"Hello, {name}!"

    print(hello_world())

# OpenAI Decorator

The OpenAI Decorator is a Python package that enriches your Python functions with the capabilities of OpenAI's API. It leverages the function's signature and docstring to generate specifications comprehensible by OpenAI's API, subsequently making a request to the API.

## Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [Basic Usage](#basic-usage)
  - [Type Annotations & Optionals](#type-annotations-optionals)
  - [Passing a Callable Prompt](#passing-callable-prompts)
  - [Using the Decorator as a Regular Function](#using-the-decorator-as-a-regular-function)
- [Contributing](#contributing)
  - [Setup](#setup)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Key Features

- Automatic generation of specs from the function's signature and docstring.
- Integration with OpenAI's API using the generated specs and a customizable prompt.
- Inference of function arguments from the OpenAI API response, negating the need for manual input.
- Handling of various edge cases related to function signatures, including default and optional values.

## Installation

Install the package using pip:

```sh
pip install openai-decorator
```
Save your OpenAI key in an environment variable named `OPENAI_API_KEY`:
```sh
export OPENAI_API_KEY=<your key>
```

## Usage Guide

### Basic Usage
Apply the `openai_func` decorator to a function with type annotations and a well-formatted Google Style docstring. Then, it will seamlessly interact with OpenAI's API to generate the parameters for your function based on the prompt.

```python
from openai_decorator import openai_func

@openai_func(prompt="Your OpenAI prompt here")
def example_function(arg1: str, arg2: int) -> str:
    """
    This is an example function.

    Args:
        arg1 (str): Description for arg1
        arg2 (int): Description for arg2

    Returns:
        str: Description for return value
    """
    return f"Your output here: {arg1} and {arg2}"

result = example_function()
print(result)
```

### Type Annotations & Optionals

The decorator efficiently handles complex function signatures:

- **Default Values:** Parameters with a default value or `Optional` type annotation are marked as optional in the JSON specification.
- **Type Annotations:** Supports primitive types (int, str, bool, float) and complex types (List, Dict, Tuple, Set, Optional, custom classes).

```python
from openai_decorator import openai_func

@openai_func(prompt="Perform mathematical operations")
def example_function(a: int, b: int, c: float = 0.0, d: List[int] = []):
    """
    This is an example function.

    Args:
        a: The first integer.
        b: The second integer.
        c: An optional float.
        d: An optional list of integers.
    """
    # Function body here
```

### Passing Callable Prompts

In addition to static strings, you can also pass a callable to the `prompt` parameter in the `openai_func` decorator to dynamically generate prompts. This callable should take no arguments and return a string. Here's an example:

```python
from openai_decorator import openai_func

def generate_prompt():
    # Dynamically generate a prompt.
    # In a real-world scenario, this could depend on various factors,
    # such as the current time or the latest trending topics.
    return "Your OpenAI prompt here"

@openai_func(prompt=generate_prompt)
def example_function(arg1: str, arg2: int) -> str:
    """
    This is an example function.

    Args:
        arg1 (str): Description for arg1
        arg2 (int): Description for arg2

    Returns:
        str: Description for return value
    """
    return f"Your output here: {arg1} and {arg2}"

result = example_function()
print(result)
```

In this example, every time `example_function` is called, `generate_prompt

### Using the Decorator as a Regular Function

`openai_func` can also be used as a regular function. First, call `openai_func` with the prompt and any other arguments to get the actual decorator. Then, apply this decorator to your function.

```python
from openai_decorator import openai_func

def example_function(arg1: str, arg2: int) -> str:
    """
    This is an example function.

    Args:
        arg1 (str): Description for arg1
        arg2 (int): Description for arg2

    Returns:
        str: Description for return value
    """
    return f"Your output here: {arg1} and {arg2}"

# Use openai_func as a regular function
prompt = "Your OpenAI prompt here"

example_func_with_generated_params = openai_func(prompt=prompt)(example_function)

result = example_func_with_generated_params()
print(result)
```
This approach gives you more flexibility in determining the prompt at runtime.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

### Setup

1. Install Python `3.11` and the latest version of [poetry](https://python-poetry.org/docs/#installing-with-pipx)
    - `pyenv` can help manage multiple Python versions.
2. Clone the repository: `git clone`.
3. Set your OpenAI key as an environment variable:
```shell
export OPENAI_API_KEY=<insert your openai key>
```
4. Install dependencies: `poetry install --no-root`

## Future Enhancements

- [x] Handle optional parameters.
- [x] Handle parameters with default values.
- [ ] Add test to ensure default values are used if OpenAI doesn't return parameters.
- [ ] Publish the package to PyPI.
- [ ] Expand test coverage.
- [ ] Show tests passing & coverage as github badges.
- [ ] Fix CI/CD -- Address the issue where the pre-release deployment to PyPI fails due to the need for version update.
- [ ] Add docstrings.
- [ ] Generate docs (from docstrings).

## License

This project is under the MIT License. See the [LICENSE](LICENSE) file for more details.

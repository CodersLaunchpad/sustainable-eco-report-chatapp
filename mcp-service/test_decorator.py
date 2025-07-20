#!/usr/bin/env python3
from fastmcp import FastMCP
import inspect

# Create MCP instance
mcp = FastMCP("Test Server")

@mcp.tool()
def test_function():
    return "Hello from test function"

# Test the decorated function
print("Type of decorated function:", type(test_function))
print("Is callable:", callable(test_function))
print("Attributes:", [attr for attr in dir(test_function) if not attr.startswith('_')])

# Try to access the original function
try:
    print("Has __wrapped__:", hasattr(test_function, '__wrapped__'))
    if hasattr(test_function, '__wrapped__'):
        print("__wrapped__ type:", type(test_function.__wrapped__))
        print("__wrapped__ callable:", callable(test_function.__wrapped__))
        result = test_function.__wrapped__()
        print("Result from __wrapped__:", result)
except Exception as e:
    print("Error with __wrapped__:", e)

try:
    print("Has func:", hasattr(test_function, 'func'))
    if hasattr(test_function, 'func'):
        print("func type:", type(test_function.func))
        print("func callable:", callable(test_function.func))
        result = test_function.func()
        print("Result from func:", result)
except Exception as e:
    print("Error with func:", e)

try:
    print("Has fn:", hasattr(test_function, 'fn'))
    if hasattr(test_function, 'fn'):
        print("fn type:", type(test_function.fn))
        print("fn callable:", callable(test_function.fn))
        result = test_function.fn()
        print("Result from fn:", result)
except Exception as e:
    print("Error with fn:", e)

try:
    print("Has __call__:", hasattr(test_function, '__call__'))
    if hasattr(test_function, '__call__'):
        result = test_function.__call__()
        print("Result from __call__:", result)
except Exception as e:
    print("Error with __call__:", e)

# Try direct call
try:
    result = test_function()
    print("Direct call result:", result)
except Exception as e:
    print("Error with direct call:", e)

# Check if it's a descriptor
print("Is descriptor:", hasattr(test_function, '__get__')) 
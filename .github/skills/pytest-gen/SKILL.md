---
name: pytest-gen
description: Generate comprehensive pytest tests with fixtures and edge cases
---

# pytest Test Generation

Generate pytest tests that include:

## Test Structure
- Use pytest conventions (`test_` prefix)
- One assertion per test when possible
- Clear test names describing expected behavior
- Group tests by function under test using classes
- Follow arrange/act/assert pattern

## Coverage
- Happy path scenarios
- Edge cases: `None`, empty strings, empty lists
- Boundary values
- Error scenarios with `pytest.raises()`
- Use `@pytest.mark.parametrize` for multiple inputs

## Fixtures
- Use `@pytest.fixture` for reusable test data
- Use `tmp_path` for file operations
- Mock external dependencies with `pytest-mock`

## Template

```python
import pytest
from module_under_test import function_to_test


@pytest.fixture
def sample_data():
    """Provide shared test data."""
    return {"key": "value"}


class TestFunctionName:
    """Tests for function_name."""

    def test_happy_path(self, sample_data):
        result = function_to_test(valid_input)
        assert result == expected_output

    def test_empty_input(self):
        result = function_to_test("")
        assert result == expected_for_empty

    @pytest.mark.parametrize("input_val,expected", [
        ("valid", True),
        ("", False),
        (None, False),
    ])
    def test_various_inputs(self, input_val, expected):
        assert function_to_test(input_val) == expected
```

## Output
Provide a complete, runnable test file with proper imports.

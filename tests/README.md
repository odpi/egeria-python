# EgeriaTech Testing Framework

This document provides comprehensive guidelines for testing EgeriaTech functions using the automated testing framework.

## Overview

The EgeriaTech testing framework supports both unit testing (with mocks) and integration testing (with live Egeria instances). It provides a robust foundation for testing all synchronous methods in EgeriaTech and its sub-clients.

## Test Structure

```
tests/
├── unit/                          # Unit tests (mocked)
│   ├── test_egeria_tech_unit.py   # Core EgeriaTech tests
│   ├── test_format_sets_unit.py   # Format set execution tests
│   └── test_mcp_unit.py           # MCP functionality tests
├── integration/                   # Integration tests (live Egeria)
│   └── test_egeria_tech_live.py   # Live EgeriaTech tests
├── fixtures/                      # Test fixtures and mocks
│   ├── mock_responses.py          # Mock response factory
│   └── test_data.py               # Test data management
├── utils/                         # Test utilities
│   └── assertion_helpers.py       # Custom assertions
├── conftest.py                    # Pytest configuration
├── pytest.ini                     # Pytest settings
└── run_tests.py                   # Test runner script
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Fast, isolated tests using mocks and monkeypatching
- **Execution**: `pytest tests/unit/ -m unit`
- **Use Case**: Development, CI/CD, rapid feedback
- **Dependencies**: None (fully mocked)

### Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Tests against live Egeria instances
- **Execution**: `pytest tests/integration/ --live-egeria -m integration`
- **Use Case**: End-to-end validation, pre-deployment testing
- **Dependencies**: Live Egeria instance

### Specialized Test Markers
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.auth`: Authentication-related tests
- `@pytest.mark.format_sets`: Format set execution tests
- `@pytest.mark.mcp`: MCP-specific functionality tests

## Running Tests

### Using the Test Runner Script

```bash
# Unit tests only (fast)
python tests/run_tests.py unit

# Integration tests (requires live Egeria)
python tests/run_tests.py integration

# All tests
python tests/run_tests.py all

# All tests with live Egeria
python tests/run_tests.py live

# Specific test categories
python tests/run_tests.py format-sets
python tests/run_tests.py mcp
python tests/run_tests.py auth

# Fast tests (exclude slow)
python tests/run_tests.py fast

# Tests with coverage
python tests/run_tests.py coverage

# Setup test environment
python tests/run_tests.py setup

# Check live Egeria availability
python tests/run_tests.py check-live
```

### Using Pytest Directly

```bash
# Unit tests
pytest tests/unit/ -m unit -v

# Integration tests
pytest tests/integration/ --live-egeria -m integration -v

# All tests
pytest tests/ -v

# Specific markers
pytest tests/ -m "format_sets and not slow" -v
pytest tests/ -m "mcp" -v

# Coverage
pytest tests/ --cov=pyegeria --cov-report=html
```

## Test Configuration

### Environment Variables

For live Egeria testing, set these environment variables:

```bash
export PYEG_LIVE_EGERIA=1
export PYEG_SERVER_NAME=your-view-server
export PYEG_PLATFORM_URL=https://your-egeria.com:9443
export PYEG_USER_ID=your-username
export PYEG_USER_PWD=your-password
```

### Pytest Configuration

The `pytest.ini` file defines:
- Test markers and their descriptions
- Default command-line options
- Test discovery patterns

## Test Fixtures

### Core Fixtures

- `mock_egeria_tech_client`: Fully mocked EgeriaTech instance
- `live_egeria_tech_client`: Real EgeriaTech instance (requires live Egeria)
- `test_credentials`: Standard test credentials
- `test_params`: Standard test parameters

### Usage Example

```python
@pytest.mark.unit
def test_egeria_tech_initialization(mock_egeria_tech_client):
    """Test EgeriaTech initialization."""
    client = mock_egeria_tech_client
    assert client.view_server is not None
    assert client.platform_url is not None
```

## Mock Response Factory

The `MockResponseFactory` provides realistic mock responses:

```python
from tests.fixtures.mock_responses import MockResponseFactory

# Create mock responses
digital_products = MockResponseFactory.create_digital_products_response(count=10)
glossary_terms = MockResponseFactory.create_glossary_terms_response(count=5)
empty_response = MockResponseFactory.create_empty_response()
error_response = MockResponseFactory.create_error_response("Test error")
```

## Custom Assertions

The `EgeriaAssertions` class provides Egeria-specific validations:

```python
from tests.utils.assertion_helpers import EgeriaAssertions

# Validate format set responses
EgeriaAssertions.assert_valid_format_set_response(result)
EgeriaAssertions.assert_valid_mcp_tool_response(result)

# Validate bearer tokens
EgeriaAssertions.assert_valid_bearer_token(token)

# Validate response content
EgeriaAssertions.assert_response_contains_expected_fields(result, ["guid", "display_name"])
EgeriaAssertions.assert_response_has_guid(result)
EgeriaAssertions.assert_response_not_empty(result)
```

## Test Data Management

The `TestDataManager` provides standardized test data:

```python
from tests.fixtures.test_data import TestDataManager

# Get test data
format_sets = TestDataManager.get_test_format_sets()
params = TestDataManager.get_test_params()
credentials = TestDataManager.get_test_credentials()
```

## Writing Tests

### Unit Test Example

```python
@pytest.mark.unit
class TestEgeriaTechUnit:
    """Unit tests for EgeriaTech core functionality."""
    
    def test_create_bearer_token_success(self, mock_egeria_tech_client):
        """Test successful bearer token creation."""
        token = mock_egeria_tech_client.create_egeria_bearer_token("user", "pass")
        
        EgeriaAssertions.assert_valid_bearer_token(token)
        assert mock_egeria_tech_client.get_token() == token
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLive:
    """Integration tests for EgeriaTech with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_digital_products_report(self, live_egeria_tech_client):
        """Test Digital-Products report against live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
```

## Test Coverage

### Coverage Targets
- **Unit tests**: 90%+ line coverage for EgeriaTech and sub-clients
- **Integration tests**: Cover all major format sets and operations
- **Contract tests**: Validate all API response schemas

### Running Coverage

```bash
# Generate coverage report
pytest tests/ --cov=pyegeria --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: EgeriaTech Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python tests/run_tests.py setup
      - name: Run unit tests
        run: python tests/run_tests.py unit
      - name: Run coverage
        run: python tests/run_tests.py coverage

  integration-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python tests/run_tests.py setup
      - name: Run integration tests
        run: python tests/run_tests.py integration
        env:
          PYEG_LIVE_EGERIA: 1
          PYEG_SERVER_NAME: ${{ secrets.EGERIA_SERVER_NAME }}
          PYEG_PLATFORM_URL: ${{ secrets.EGERIA_PLATFORM_URL }}
          PYEG_USER_ID: ${{ secrets.EGERIA_USER_ID }}
          PYEG_USER_PWD: ${{ secrets.EGERIA_USER_PWD }}
```

## Best Practices

### Test Organization
1. **Group related tests** in classes
2. **Use descriptive test names** that explain what is being tested
3. **Follow the AAA pattern**: Arrange, Act, Assert
4. **Keep tests independent** - no test should depend on another

### Mock Usage
1. **Mock external dependencies** (network calls, file I/O)
2. **Use realistic mock data** from MockResponseFactory
3. **Verify mock interactions** when necessary
4. **Reset mocks** between tests

### Assertions
1. **Use specific assertions** rather than generic ones
2. **Validate response structure** with EgeriaAssertions
3. **Test both success and failure cases**
4. **Include edge cases** (empty responses, errors)

### Performance
1. **Mark slow tests** with `@pytest.mark.slow`
2. **Use appropriate timeouts** for async operations
3. **Avoid unnecessary network calls** in unit tests
4. **Run fast tests frequently**, slow tests less often

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `python tests/run_tests.py setup`
   - Check Python path and module structure

2. **Live Egeria Connection Issues**
   - Verify environment variables: `python tests/run_tests.py check-live`
   - Check network connectivity and SSL certificates
   - Ensure Egeria instance is running and accessible

3. **Test Failures**
   - Run with verbose output: `pytest tests/ -v`
   - Check test logs and error messages
   - Verify mock responses match expected format

4. **Coverage Issues**
   - Ensure all code paths are tested
   - Check for untested error conditions
   - Verify async/await patterns are properly tested

### Debug Mode

Run tests in debug mode for detailed output:

```bash
pytest tests/ -v -s --tb=long --capture=no
```

## Contributing

When adding new tests:

1. **Follow existing patterns** and naming conventions
2. **Add appropriate markers** for test categorization
3. **Update documentation** if adding new fixtures or utilities
4. **Ensure tests pass** in both unit and integration modes
5. **Maintain test coverage** above target thresholds

## Support

For questions or issues with the testing framework:

1. Check this documentation first
2. Review existing test examples
3. Run `python tests/run_tests.py check-live` for environment issues
4. Check pytest output for specific error messages
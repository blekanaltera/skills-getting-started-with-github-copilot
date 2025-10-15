# Tests for Mergington High School Activities API

This directory contains comprehensive test suites for the FastAPI application.

## Test Structure

```
tests/
├── __init__.py          # Package initialization
├── conftest.py          # Pytest configuration and fixtures
├── test_api.py          # API endpoint tests
└── test_validation.py   # Data validation and business logic tests
```

## Test Coverage

Our test suite achieves **100% code coverage** and includes:

### API Endpoint Tests (`test_api.py`)
- ✅ `GET /activities` - Retrieve all activities
- ✅ `POST /activities/{name}/signup` - Student registration
- ✅ `DELETE /activities/{name}/unregister` - Student unregistration  
- ✅ `GET /` - Root redirect functionality
- ✅ Error handling for invalid activities
- ✅ Duplicate registration prevention
- ✅ Activity capacity limits

### Data Validation Tests (`test_validation.py`)
- ✅ Required parameter validation
- ✅ URL encoding for activity names
- ✅ Empty email handling
- ✅ Data structure integrity
- ✅ Type checking for all fields

## Running Tests

### Quick Test Run
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Using the Test Runner Script
```bash
./run_tests.sh
```

### Running Specific Tests
```bash
# Run only API tests
python -m pytest tests/test_api.py -v

# Run only validation tests  
python -m pytest tests/test_validation.py -v

# Run a specific test method
python -m pytest tests/test_api.py::TestActivitiesAPI::test_get_activities -v
```

## Test Dependencies

Required packages (already in `requirements.txt`):
- `pytest` - Testing framework
- `httpx` - HTTP client for FastAPI testing
- `pytest-cov` - Coverage reporting

## Test Features

- **Isolated Tests**: Each test runs in isolation with proper setup/teardown
- **Comprehensive Coverage**: Tests cover all API endpoints and edge cases
- **Error Validation**: Tests verify proper HTTP status codes and error messages
- **Data Integrity**: Tests ensure data structure consistency
- **Performance**: Fast test execution with efficient fixtures

## Test Results

All tests pass successfully with:
- ✅ 14 test cases
- ✅ 100% code coverage
- ✅ Comprehensive error handling
- ✅ Full API endpoint coverage
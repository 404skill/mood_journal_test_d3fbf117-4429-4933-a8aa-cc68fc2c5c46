# Journal Entry System API Tests

This repository contains comprehensive API tests for the Journal Entry System as specified in `spec.md`.

## Test Coverage

The tests are organized by task and cover all 7 tasks from the specification:

### Task 1: Health Check
- Tests the `GET /health` endpoint
- Verifies correct status code and JSON response structure

### Task 2: Journal Entry Creation
- Tests `POST /entries` endpoint
- Validates request/response formats
- Tests error handling for invalid inputs
- Covers edge cases like empty text, missing fields, etc.

### Task 3: CRUD Operations
- Tests all CRUD operations: GET, PUT, DELETE
- Validates UUID format handling
- Tests error responses for invalid/non-existent IDs
- Verifies data structure and field validation

### Task 4: Mood Extraction
- Tests automatic mood extraction when creating entries
- Verifies mood field is present in responses
- Tests mood extraction for existing entries without mood

### Task 5: Mood Filtering
- Tests `GET /entries?moods=happy,sad` filtering
- Validates single and multiple mood filters
- Tests edge cases like empty filters and non-existent moods

### Task 6: Mood Summary
- Tests `GET /mood/summary` endpoint
- Verifies mood distribution counting
- Tests empty database scenarios

### Task 7: Time Range Filtering
- Tests date range filtering on both `/entries` and `/mood/summary`
- Validates ISO 8601 date format handling
- Tests start date, end date, and range filters
- Verifies error handling for invalid date formats

## Running Tests

### Option 1: Docker (Recommended)

The easiest way to run tests is using Docker, which ensures a consistent environment and automatically disables pytest caching.

```bash
# Build and run all tests
docker build -t journal-api-tests .
docker run --rm -v "$(pwd)/test-results:/app/test-results" journal-api-tests

# Or in one command
docker run --rm -v "$(pwd)/test-results:/app/test-results" $(docker build -q .)
```

### Option 2: Local Python Environment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start your API server (adjust the base URL in `test_api.py` if needed)

3. Run the tests:
```bash
# Run all tests
pytest test_api.py -v

# Run tests for a specific task
pytest test_api.py::TestTask1HealthCheck -v
pytest test_api.py::TestTask2JournalEntryCreation -v
pytest test_api.py::TestTask3CRUDOperations -v
pytest test_api.py::TestTask4MoodExtraction -v
pytest test_api.py::TestTask5MoodFiltering -v
pytest test_api.py::TestTask6MoodSummary -v
pytest test_api.py::TestTask7TimeRangeFiltering -v

# Run with HTML report
pytest test_api.py --html=report.html

# Run in parallel
pytest test_api.py -n auto

# Disable caching (recommended for CI/CD)
pytest test_api.py --cache-clear
```

## Test Results

When running tests with Docker, results are saved to:
- `test-results/test-results.xml` - JUnit XML format (for CI/CD integration)

## Test Features

- **Descriptive test names**: Each test has a clear, descriptive name explaining what it tests
- **Comprehensive assertions**: Every assertion includes descriptive failure messages
- **Task separation**: Tests are organized by task with clear class namespaces
- **Edge case coverage**: Tests cover normal cases, error cases, and edge cases
- **Independent tests**: Each test is independent and doesn't rely on database state
- **Data setup**: Tests create their own test data as needed
- **Error validation**: Tests verify both success and error responses
- **Format validation**: Tests validate JSON structure, data types, and field presence
- **No caching**: Docker setup ensures tests are re-run every time

## Configuration

The base URL for the API can be configured in the `base_url` fixture in `test_api.py`. By default, it's set to `http://host.docker.internal:8001`.

## Docker Features

- **Simple setup**: Just build and run - no extra scripts needed
- **Consistent environment**: Same Python version and dependencies every time
- **No caching**: Tests are re-run every time with `--cache-clear`
- **Isolated execution**: Tests run in a clean container environment
- **Result persistence**: Test results are saved to mounted volume
- **Direct entrypoint**: Dockerfile directly runs pytest as entrypoint

## Notes

- Tests assume the API server is running and accessible
- Tests create their own test data and don't rely on existing database state
- All tests include proper cleanup and are designed to be idempotent
- Error messages are validated to ensure proper API error handling
- Date handling assumes ISO 8601 format with timezone information
- Docker setup ensures pytest caching is disabled for consistent test execution 
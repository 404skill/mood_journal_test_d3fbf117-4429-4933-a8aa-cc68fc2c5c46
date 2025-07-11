"""
Comprehensive API tests for Journal Entry System
Organized by tasks with clear separation and descriptive test names
"""
import pytest
import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List

from test_utils import (
    create_test_entry, get_entry_by_id, delete_entry_by_id,
    validate_uuid, validate_iso_date, create_entries_with_moods,
    cleanup_test_entries, assert_valid_entry_structure, assert_valid_error_response
)


@pytest.fixture
def base_url():
    """Fixture providing the base URL for the API"""
    return "http://app:8000"  # Adjust port as needed


class TestTask1HealthCheck:
    """Task 1: Health Check Endpoint Tests"""
    
    @pytest.mark.task1
    def test_health_endpoint_returns_200_ok(self, base_url):
        """Test that GET /health returns 200 OK with correct JSON structure"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.headers.get('content-type', '').startswith('application/json'), \
            f"Expected JSON content type, but got {response.headers.get('content-type')}"
        
        data = response.json()
        assert 'status' in data, "Response JSON should contain 'status' field"
        assert data['status'] == 'OK', f"Expected status 'OK', but got '{data['status']}'"
    
    @pytest.mark.task1
    def test_health_endpoint_response_structure(self, base_url):
        """Test that health endpoint response has correct structure"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, dict), f"Response should be a dictionary, but got {type(data)}"
        assert len(data) == 1, f"Response should have exactly 1 field, but got {len(data)}"
        assert 'status' in data, "Response should contain 'status' field"


class TestTask2JournalEntryCreation:
    """Task 2: Journal Entry Model and POST Route Tests"""
    
    @pytest.mark.task2
    def test_create_entry_success_returns_201_with_id(self, base_url):
        """Test successful journal entry creation returns 201 Created with entry ID"""
        entry_data = {"text": "My first journal entry"}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"
        assert response.headers.get('content-type', '').startswith('application/json'), \
            f"Expected JSON content type, but got {response.headers.get('content-type')}"
        
        data = response.json()
        assert 'id' in data, "Response should contain 'id' field"
        assert isinstance(data['id'], str), f"ID should be a string, but got {type(data['id'])}"
        assert validate_uuid(data['id']), f"ID '{data['id']}' is not a valid UUID"
    
    @pytest.mark.task2
    def test_create_entry_empty_text_returns_400(self, base_url):
        """Test that creating entry with empty text returns 400 Bad Request"""
        entry_data = {"text": ""}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
        assert "empty" in data['error'].lower(), f"Error message should mention empty text, got: {data['error']}"
    
    @pytest.mark.task2
    def test_create_entry_missing_text_returns_400(self, base_url):
        """Test that creating entry without text field returns 400 Bad Request"""
        entry_data = {}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task2
    def test_create_entry_null_text_returns_400(self, base_url):
        """Test that creating entry with null text returns 400 Bad Request"""
        entry_data = {"text": None}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task2
    def test_create_entry_whitespace_only_text_returns_400(self, base_url):
        """Test that creating entry with only whitespace text returns 400 Bad Request"""
        entry_data = {"text": "   \n\t   "}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task2
    def test_create_entry_invalid_json_returns_400(self, base_url):
        """Test that sending invalid JSON returns 400 Bad Request"""
        response = requests.post(
            f"{base_url}/entries", 
            data="invalid json", 
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
    
    @pytest.mark.task2
    def test_create_entry_long_text_success(self, base_url):
        """Test that creating entry with long text succeeds"""
        long_text = "A" * 1000  # 1000 character text
        entry_data = {"text": long_text}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"
        
        data = response.json()
        assert 'id' in data, "Response should contain 'id' field"
        assert validate_uuid(data['id']), f"ID '{data['id']}' is not a valid UUID"
    
    @pytest.mark.task2
    def test_create_entry_special_characters_success(self, base_url):
        """Test that creating entry with special characters succeeds"""
        special_text = "Entry with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        entry_data = {"text": special_text}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"
        
        data = response.json()
        assert 'id' in data, "Response should contain 'id' field"


class TestTask3CRUDOperations:
    """Task 3: CRUD Operations Tests"""
    
    @pytest.mark.task3
    def test_get_all_entries_empty_database_returns_empty_array(self, base_url):
        """Test GET /entries returns empty array when no entries exist"""
        response = requests.get(f"{base_url}/entries")
        
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.headers.get('content-type', '').startswith('application/json'), \
            f"Expected JSON content type, but got {response.headers.get('content-type')}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list response, but got {type(data)}"
        assert len(data) == 0, f"Expected empty array, but got {len(data)} items"
    
    @pytest.mark.task3
    def test_get_all_entries_with_data_returns_correct_structure(self, base_url):
        """Test GET /entries returns correct structure when entries exist"""
        # Create test entries
        entries_to_create = [
            {"text": "First test entry"},
            {"text": "Second test entry"},
            {"text": "Third test entry"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get all entries
            response = requests.get(f"{base_url}/entries")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            assert len(data) >= 3, f"Expected at least 3 entries, but got {len(data)}"
            
            # Verify structure of each entry
            for entry in data:
                assert_valid_entry_structure(entry)
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task3
    def test_get_specific_entry_valid_id_returns_entry(self, base_url):
        """Test GET /entries/:id returns correct entry for valid ID"""
        # Create a test entry
        created_entry = create_test_entry(base_url, "Entry to retrieve")
        entry_id = created_entry['id']
        
        try:
            # Get the specific entry
            response = requests.get(f"{base_url}/entries/{entry_id}")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert data['id'] == entry_id, f"Returned entry ID should match requested ID"
            assert data['text'] == "Entry to retrieve", f"Returned text should match created text"
            assert 'createdAt' in data, "Entry should have createdAt field"
            assert_valid_entry_structure(data)
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id)
    
    @pytest.mark.task3
    def test_get_specific_entry_invalid_uuid_returns_400(self, base_url):
        """Test GET /entries/:id returns 400 for invalid UUID"""
        invalid_id = "not-a-uuid"
        response = requests.get(f"{base_url}/entries/{invalid_id}")
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task3
    def test_get_specific_entry_nonexistent_id_returns_404(self, base_url):
        """Test GET /entries/:id returns 404 for non-existent ID"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/entries/{fake_id}")
        
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task3
    def test_update_entry_valid_id_success(self, base_url):
        """Test PUT /entries/:id successfully updates entry"""
        # Create a test entry
        created_entry = create_test_entry(base_url, "Original text")
        entry_id = created_entry['id']
        
        try:
            # Update the entry
            update_data = {"text": "Updated text"}
            response = requests.put(f"{base_url}/entries/{entry_id}", json=update_data)
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert 'id' in data, "Response should contain 'id' field"
            assert data['id'] == entry_id, f"Returned ID should match updated entry ID"
            
            # Verify the update by getting the entry
            updated_entry = get_entry_by_id(base_url, entry_id)
            assert updated_entry is not None, "Updated entry should exist"
            assert updated_entry['text'] == "Updated text", "Entry text should be updated"
            assert 'updatedAt' in updated_entry, "Entry should have updatedAt field after update"
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id)
    
    @pytest.mark.task3
    def test_update_entry_invalid_uuid_returns_400(self, base_url):
        """Test PUT /entries/:id returns 400 for invalid UUID"""
        invalid_id = "not-a-uuid"
        update_data = {"text": "Updated text"}
        response = requests.put(f"{base_url}/entries/{invalid_id}", json=update_data)
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task3
    def test_update_entry_nonexistent_id_returns_404(self, base_url):
        """Test PUT /entries/:id returns 404 for non-existent ID"""
        fake_id = str(uuid.uuid4())
        update_data = {"text": "Updated text"}
        response = requests.put(f"{base_url}/entries/{fake_id}", json=update_data)
        
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task3
    def test_update_entry_empty_text_returns_400(self, base_url):
        """Test PUT /entries/:id returns 400 for empty text"""
        # Create a test entry
        created_entry = create_test_entry(base_url, "Original text")
        entry_id = created_entry['id']
        
        try:
            # Try to update with empty text
            update_data = {"text": ""}
            response = requests.put(f"{base_url}/entries/{entry_id}", json=update_data)
            
            assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
            
            data = response.json()
            assert_valid_error_response(data)
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id)
    
    @pytest.mark.task3
    def test_delete_entry_valid_id_returns_204(self, base_url):
        """Test DELETE /entries/:id returns 204 on successful deletion"""
        # Create a test entry
        created_entry = create_test_entry(base_url, "Entry to delete")
        entry_id = created_entry['id']
        
        # Delete the entry
        response = requests.delete(f"{base_url}/entries/{entry_id}")
        assert response.status_code == 204, f"Expected status code 204, but got {response.status_code}"
        
        # Verify entry is deleted
        get_response = requests.get(f"{base_url}/entries/{entry_id}")
        assert get_response.status_code == 404, "Deleted entry should not be found"
    
    @pytest.mark.task3
    def test_delete_entry_invalid_uuid_returns_400(self, base_url):
        """Test DELETE /entries/:id returns 400 for invalid UUID"""
        invalid_id = "not-a-uuid"
        response = requests.delete(f"{base_url}/entries/{invalid_id}")
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task3
    def test_delete_entry_nonexistent_id_returns_404(self, base_url):
        """Test DELETE /entries/:id returns 404 for non-existent ID"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{base_url}/entries/{fake_id}")
        
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)


class TestTask4MoodExtraction:
    """Task 4: Mood Extraction Service Tests"""
    
    @pytest.mark.task4
    def test_create_entry_with_mood_extraction(self, base_url):
        """Test that creating entry automatically extracts and saves mood"""
        entry_data = {"text": "I am so happy today!"}
        response = requests.post(f"{base_url}/entries", json=entry_data)
        
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"
        
        data = response.json()
        assert 'id' in data, "Response should contain 'id' field"
        
        # Get the created entry to verify mood was extracted
        entry_id = data['id']
        get_response = requests.get(f"{base_url}/entries/{entry_id}")
        assert get_response.status_code == 200, "Failed to retrieve created entry"
        
        entry = get_response.json()
        assert 'mood' in entry, "Entry should have mood field after creation"
        assert isinstance(entry['mood'], str), f"Mood should be string, but got {type(entry['mood'])}"
        assert len(entry['mood']) > 0, "Mood should not be empty"
        
        # Cleanup
        delete_entry_by_id(base_url, entry_id)
    
    @pytest.mark.task4
    def test_get_entries_returns_mood_field(self, base_url):
        """Test that GET /entries returns entries with mood field"""
        # Create entries with different emotional content
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get all entries
            response = requests.get(f"{base_url}/entries")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all entries have mood field
            for entry in data:
                assert 'mood' in entry, "Each entry should have mood field"
                assert isinstance(entry['mood'], str), f"Mood should be string, but got {type(entry['mood'])}"
                assert len(entry['mood']) > 0, "Mood should not be empty"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task4
    def test_existing_entry_without_mood_gets_mood_extracted(self, base_url):
        """Test that existing entries without mood get mood extracted when retrieved"""
        # Create entry
        created_entry = create_test_entry(base_url, "I am feeling great today!")
        entry_id = created_entry['id']
        
        try:
            # Get the entry - it should have mood extracted
            get_response = requests.get(f"{base_url}/entries/{entry_id}")
            assert get_response.status_code == 200, "Failed to retrieve entry"
            
            entry = get_response.json()
            assert 'mood' in entry, "Entry should have mood field after retrieval"
            assert isinstance(entry['mood'], str), f"Mood should be string, but got {type(entry['mood'])}"
            assert len(entry['mood']) > 0, "Mood should not be empty"
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id)


class TestTask5MoodFiltering:
    """Task 5: Mood Filtering Tests"""
    
    @pytest.mark.task5
    def test_get_entries_filter_by_single_mood(self, base_url):
        """Test GET /entries?moods=happy returns only happy entries"""
        # Create entries with different moods
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Filter by happy mood
            response = requests.get(f"{base_url}/entries?moods=happy")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all returned entries have happy mood
            for entry in data:
                assert entry['mood'] == 'happy', f"All entries should have 'happy' mood, but got '{entry['mood']}'"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task5
    def test_get_entries_filter_by_multiple_moods(self, base_url):
        """Test GET /entries?moods=happy,sad returns entries with either mood"""
        # Create entries with different moods
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"},
            {"text": "I am feeling great!"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Filter by happy and sad moods
            response = requests.get(f"{base_url}/entries?moods=happy,sad")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all returned entries have either happy or sad mood
            for entry in data:
                assert entry['mood'] in ['happy', 'sad'], f"Entry mood should be 'happy' or 'sad', but got '{entry['mood']}'"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task5
    def test_get_entries_no_mood_filter_returns_all_entries(self, base_url):
        """Test GET /entries without mood filter returns all entries"""
        # Create multiple entries
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get all entries without filter
            response = requests.get(f"{base_url}/entries")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            assert len(data) >= 3, f"Expected at least 3 entries, but got {len(data)}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task5
    def test_get_entries_empty_mood_filter_returns_all_entries(self, base_url):
        """Test GET /entries?moods= returns all entries (empty filter)"""
        # Create multiple entries
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get entries with empty mood filter
            response = requests.get(f"{base_url}/entries?moods=")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            assert len(data) >= 3, f"Expected at least 3 entries, but got {len(data)}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task5
    def test_get_entries_nonexistent_mood_returns_empty_array(self, base_url):
        """Test GET /entries?moods=nonexistent returns empty array"""
        # Create some entries
        created_entry = create_test_entry(base_url, "I am so happy today!")
        entry_id = created_entry['id']
        
        try:
            # Filter by nonexistent mood
            response = requests.get(f"{base_url}/entries?moods=nonexistent")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            assert len(data) == 0, f"Expected empty array for nonexistent mood, but got {len(data)} entries"
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id)


class TestTask6MoodSummary:
    """Task 6: Mood Summary Endpoint Tests"""
    
    @pytest.mark.task6
    def test_get_mood_summary_empty_database_returns_empty_object(self, base_url):
        """Test GET /mood/summary returns empty object when no entries exist"""
        response = requests.get(f"{base_url}/mood/summary")
        
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.headers.get('content-type', '').startswith('application/json'), \
            f"Expected JSON content type, but got {response.headers.get('content-type')}"
        
        data = response.json()
        assert isinstance(data, dict), f"Expected dict response, but got {type(data)}"
        assert len(data) == 0, f"Expected empty object, but got {len(data)} items"
    
    @pytest.mark.task6
    def test_get_mood_summary_with_entries_returns_correct_counts(self, base_url):
        """Test GET /mood/summary returns correct mood distribution"""
        # Create entries with different moods
        entries_to_create = [
            {"text": "I am so happy today!"},
            {"text": "I am feeling great!"},
            {"text": "I feel sad and lonely"},
            {"text": "I am angry about this situation"},
            {"text": "I am happy again!"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get mood summary
            response = requests.get(f"{base_url}/mood/summary")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, dict), f"Expected dict response, but got {type(data)}"
            
            # Verify structure - all values should be integers
            for mood, count in data.items():
                assert isinstance(mood, str), f"Mood key should be string, but got {type(mood)}"
                assert isinstance(count, int), f"Count should be integer, but got {type(count)}"
                assert count > 0, f"Count should be positive, but got {count}"
            
            # Verify total count matches expected
            total_entries = sum(data.values())
            assert total_entries >= 5, f"Expected at least 5 total entries, but got {total_entries}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)


class TestTask7TimeRangeFiltering:
    """Task 7: Time Range Filtering Tests"""
    
    @pytest.mark.task7
    def test_get_entries_with_start_date_filter(self, base_url):
        """Test GET /entries?startDate=2025-06-20 returns entries from that date onwards"""
        # Create entries
        entries_to_create = [
            {"text": "Entry from June 19"},
            {"text": "Entry from June 20"},
            {"text": "Entry from June 21"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Filter by start date
            response = requests.get(f"{base_url}/entries?startDate=2025-06-20")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all entries are from start date onwards
            start_date = datetime.fromisoformat("2025-06-20T00:00:00")
            for entry in data:
                entry_date = datetime.fromisoformat(entry['createdAt'].replace('Z', '+00:00'))
                assert entry_date >= start_date, f"Entry date {entry_date} should be >= {start_date}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task7
    def test_get_entries_with_end_date_filter(self, base_url):
        """Test GET /entries?endDate=2025-06-22 returns entries up to that date"""
        # Create entries
        entries_to_create = [
            {"text": "Entry from June 21"},
            {"text": "Entry from June 22"},
            {"text": "Entry from June 23"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Filter by end date
            response = requests.get(f"{base_url}/entries?endDate=2025-06-22")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all entries are up to end date
            end_date = datetime.fromisoformat("2025-06-22T23:59:59")
            for entry in data:
                entry_date = datetime.fromisoformat(entry['createdAt'].replace('Z', '+00:00'))
                assert entry_date <= end_date, f"Entry date {entry_date} should be <= {end_date}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task7
    def test_get_entries_with_date_range_filter(self, base_url):
        """Test GET /entries?startDate=2025-06-20&endDate=2025-06-22 returns entries in range"""
        # Create entries
        entries_to_create = [
            {"text": "Entry from June 19"},
            {"text": "Entry from June 20"},
            {"text": "Entry from June 21"},
            {"text": "Entry from June 22"},
            {"text": "Entry from June 23"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Filter by date range
            response = requests.get(f"{base_url}/entries?startDate=2025-06-20&endDate=2025-06-22")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            
            # Verify all entries are within the date range
            start_date = datetime.fromisoformat("2025-06-20T00:00:00")
            end_date = datetime.fromisoformat("2025-06-22T23:59:59")
            for entry in data:
                entry_date = datetime.fromisoformat(entry['createdAt'].replace('Z', '+00:00'))
                assert start_date <= entry_date <= end_date, f"Entry date {entry_date} should be between {start_date} and {end_date}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task7
    def test_get_entries_invalid_date_format_returns_400(self, base_url):
        """Test GET /entries with invalid date format returns 400 Bad Request"""
        response = requests.get(f"{base_url}/entries?startDate=invalid-date")
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
        assert "date format" in data['error'].lower(), f"Error message should mention date format, got: {data['error']}"
    
    @pytest.mark.task7
    def test_get_mood_summary_with_date_range_filter(self, base_url):
        """Test GET /mood/summary?startDate=2025-06-20&endDate=2025-06-22 returns filtered summary"""
        # Create entries with different moods
        entries_to_create = [
            {"text": "Happy entry from June 19"},
            {"text": "Happy entry from June 20"},
            {"text": "Sad entry from June 21"},
            {"text": "Happy entry from June 22"},
            {"text": "Angry entry from June 23"}
        ]
        
        created_ids = create_entries_with_moods(base_url, entries_to_create)
        
        try:
            # Get mood summary with date range filter
            response = requests.get(f"{base_url}/mood/summary?startDate=2025-06-20&endDate=2025-06-22")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, dict), f"Expected dict response, but got {type(data)}"
            
            # Verify all values are integers
            for mood, count in data.items():
                assert isinstance(mood, str), f"Mood key should be string, but got {type(mood)}"
                assert isinstance(count, int), f"Count should be integer, but got {type(count)}"
                assert count > 0, f"Count should be positive, but got {count}"
        finally:
            # Cleanup
            cleanup_test_entries(base_url, created_ids)
    
    @pytest.mark.task7
    def test_get_mood_summary_invalid_date_format_returns_400(self, base_url):
        """Test GET /mood/summary with invalid date format returns 400 Bad Request"""
        response = requests.get(f"{base_url}/mood/summary?startDate=invalid-date")
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
        assert "date format" in data['error'].lower(), f"Error message should mention date format, got: {data['error']}"
    
    @pytest.mark.task7
    def test_get_entries_with_malformed_date_returns_400(self, base_url):
        """Test GET /entries with malformed date returns 400 Bad Request"""
        response = requests.get(f"{base_url}/entries?startDate=2025-13-45")
        
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
        
        data = response.json()
        assert_valid_error_response(data)
    
    @pytest.mark.task7
    def test_get_entries_with_future_date_filter(self, base_url):
        """Test GET /entries with future date filter returns appropriate results"""
        # Create some entries
        created_entry = create_test_entry(base_url, "Current entry")
        entry_id = created_entry['id']
        
        try:
            # Filter with future date
            future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            response = requests.get(f"{base_url}/entries?startDate={future_date}")
            assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), f"Expected list response, but got {type(data)}"
            # Should return empty list for future date
            assert len(data) == 0, f"Expected empty list for future date, but got {len(data)} entries"
        finally:
            # Cleanup
            delete_entry_by_id(base_url, entry_id) 
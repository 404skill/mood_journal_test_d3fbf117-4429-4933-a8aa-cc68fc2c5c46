"""
Utility functions for API testing
"""
import uuid
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


def create_test_entry(base_url: str, text: str) -> Dict[str, Any]:
    """
    Helper function to create a test journal entry
    
    Args:
        base_url: Base URL of the API
        text: Text content for the journal entry
        
    Returns:
        Dictionary containing the created entry data
        
    Raises:
        AssertionError: If entry creation fails
    """
    entry_data = {"text": text}
    response = requests.post(f"{base_url}/entries", json=entry_data)
    
    assert response.status_code == 201, f"Failed to create test entry: {response.status_code}"
    
    data = response.json()
    assert 'id' in data, "Created entry should have ID"
    
    return data


def get_entry_by_id(base_url: str, entry_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to get an entry by ID
    
    Args:
        base_url: Base URL of the API
        entry_id: ID of the entry to retrieve
        
    Returns:
        Entry data if found, None if not found
    """
    response = requests.get(f"{base_url}/entries/{entry_id}")
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return None
    else:
        raise AssertionError(f"Unexpected status code when getting entry: {response.status_code}")


def delete_entry_by_id(base_url: str, entry_id: str) -> bool:
    """
    Helper function to delete an entry by ID
    
    Args:
        base_url: Base URL of the API
        entry_id: ID of the entry to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    response = requests.delete(f"{base_url}/entries/{entry_id}")
    
    if response.status_code == 204:
        return True
    elif response.status_code == 404:
        return False
    else:
        raise AssertionError(f"Unexpected status code when deleting entry: {response.status_code}")


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID
    
    Args:
        uuid_string: String to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_iso_date(date_string: str) -> bool:
    """
    Validate if a string is a valid ISO 8601 date
    
    Args:
        date_string: String to validate
        
    Returns:
        True if valid ISO date, False otherwise
    """
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def create_entries_with_moods(base_url: str, entries_data: List[Dict[str, str]]) -> List[str]:
    """
    Helper function to create multiple entries with specific text content
    
    Args:
        base_url: Base URL of the API
        entries_data: List of dictionaries with 'text' field
        
    Returns:
        List of created entry IDs
    """
    created_ids = []
    
    for entry_data in entries_data:
        response = requests.post(f"{base_url}/entries", json=entry_data)
        assert response.status_code == 201, f"Failed to create test entry: {response.status_code}"
        created_ids.append(response.json()['id'])
    
    return created_ids


def cleanup_test_entries(base_url: str, entry_ids: List[str]):
    """
    Helper function to clean up test entries
    
    Args:
        base_url: Base URL of the API
        entry_ids: List of entry IDs to delete
    """
    for entry_id in entry_ids:
        try:
            delete_entry_by_id(base_url, entry_id)
        except AssertionError:
            # Entry might already be deleted, ignore
            pass


def assert_valid_entry_structure(entry: Dict[str, Any]):
    """
    Assert that an entry has the correct structure
    
    Args:
        entry: Entry data to validate
    """
    assert isinstance(entry, dict), f"Entry should be a dictionary, but got {type(entry)}"
    assert 'id' in entry, "Entry should have 'id' field"
    assert 'text' in entry, "Entry should have 'text' field"
    assert 'createdAt' in entry, "Entry should have 'createdAt' field"
    
    assert isinstance(entry['id'], str), f"Entry ID should be string, but got {type(entry['id'])}"
    assert isinstance(entry['text'], str), f"Entry text should be string, but got {type(entry['text'])}"
    assert isinstance(entry['createdAt'], str), f"Entry createdAt should be string, but got {type(entry['createdAt'])}"
    
    # Validate UUID format
    assert validate_uuid(entry['id']), f"Entry ID '{entry['id']}' is not a valid UUID"
    
    # Validate date format
    assert validate_iso_date(entry['createdAt']), f"Entry createdAt '{entry['createdAt']}' is not a valid ISO date"


def assert_valid_error_response(response_data: Dict[str, Any]):
    """
    Assert that an error response has the correct structure
    
    Args:
        response_data: Error response data to validate
    """
    assert isinstance(response_data, dict), f"Error response should be a dictionary, but got {type(response_data)}"
    assert 'error' in response_data, "Error response should contain 'error' field"
    assert isinstance(response_data['error'], str), f"Error message should be string, but got {type(response_data['error'])}"
    assert len(response_data['error']) > 0, "Error message should not be empty" 
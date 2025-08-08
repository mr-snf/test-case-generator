"""
Jira API client tests using pytest.
"""

import os
from unittest.mock import Mock, mock_open, patch

import pytest

from src.jira import JiraAPI


class TestJiraAPI:
    """Test class for Jira API client"""

    @pytest.fixture
    def api_client(self):
        """Fixture to create Jira API client"""
        return JiraAPI(
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )

    @pytest.fixture
    def mock_jira_response(self):
        """Fixture for mock Jira API responses"""
        return {
            "id": "12345",
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue Summary",
                "description": "Test issue description",
                "attachment": [
                    {
                        "filename": "test.pdf",
                        "size": 1024,
                        "mimeType": "application/pdf",
                        "created": "2024-01-01T11:00:00.000Z",
                        "author": {"displayName": "John Doe"},
                        "content": "https://example.com/attachment/test.pdf",
                        "thumbnail": "https://example.com/thumbnail/test.pdf",
                    }
                ],
            },
        }

    @pytest.mark.unit
    def test_api_client_initialization(self, api_client):
        """Test Jira API client initialization"""
        assert api_client is not None
        assert hasattr(api_client, "base_url")
        assert hasattr(api_client, "username")
        assert hasattr(api_client, "api_token")
        assert api_client.base_url == "https://test.atlassian.net"
        assert api_client.username == "test@example.com"
        assert api_client.api_token == "test-token"

    @pytest.mark.unit
    def test_api_client_missing_configuration(self):
        """Test Jira API client initialization with missing configuration"""
        with pytest.raises(ValueError, match="Jira configuration missing"):
            JiraAPI(base_url="", username="", api_token="")

    @pytest.mark.api
    @patch("requests.get")
    def test_get_issue_success(self, mock_get, api_client, mock_jira_response):
        """Test successful get_issue call"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_jira_response
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue("TEST-123")

        # Assertions
        assert result == mock_jira_response
        mock_get.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123",
            auth=api_client.auth,
            headers=api_client.headers,
        )

    @pytest.mark.api
    @patch("requests.get")
    def test_get_issue_not_found(self, mock_get, api_client):
        """Test get_issue with 404 response"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Issue not found"
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue("TEST-999")

        # Assertions
        assert result == {}

    @pytest.mark.api
    @patch("requests.get")
    def test_get_issue_error(self, mock_get, api_client):
        """Test get_issue with API error"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue("TEST-123")

        # Assertions
        assert result == {}

    @pytest.mark.unit
    @patch("requests.get")
    def test_get_issue_description_success(self, mock_get, api_client):
        """Test get_issue_description method"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fields": {"description": "Test issue description"}
        }
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue_description("TEST-123")

        # Assertions
        assert result == "Test issue description"
        mock_get.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123",
            auth=api_client.auth,
            headers=api_client.headers,
            params={"fields": "description"},
        )

    @pytest.mark.unit
    @patch("requests.get")
    def test_get_issue_description_adf(self, mock_get, api_client):
        """Test get_issue_description method with ADF format"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fields": {
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Test ADF description"}
                            ],
                        }
                    ],
                }
            }
        }
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue_description("TEST-123")

        # Assertions
        assert result == "Test ADF description"

    @pytest.mark.unit
    @patch("requests.get")
    def test_get_issue_description_error(self, mock_get, api_client):
        """Test get_issue_description with API error"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Test
        result = api_client.get_issue_description("TEST-123")

        # Assertions
        assert result == ""

    @pytest.mark.unit
    def test_extract_text_from_adf(self, api_client):
        """Test _extract_text_from_adf method"""
        # Test ADF content
        adf_content = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "First paragraph"},
                        {"type": "text", "text": " continued"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Second paragraph"}],
                },
            ],
        }

        result = api_client._extract_text_from_adf(adf_content)
        assert result == "First paragraph  continued Second paragraph"

    @pytest.mark.unit
    def test_extract_text_from_adf_invalid(self, api_client):
        """Test _extract_text_from_adf method with invalid content"""
        # Test with non-dict content
        result = api_client._extract_text_from_adf("plain text")
        assert result == "plain text"

        # Test with None
        result = api_client._extract_text_from_adf(None)
        assert result == "None"

    @pytest.mark.api
    @patch("requests.get")
    def test_test_connection_success(self, mock_get, api_client):
        """Test test_connection success"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "serverTitle": "Test Jira Server",
            "version": "9.0.0",
        }
        mock_get.return_value = mock_response

        # Test
        result = api_client.test_connection()

        # Assertions
        assert result is True
        mock_get.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/serverInfo",
            auth=api_client.auth,
            headers=api_client.headers,
        )

    @pytest.mark.api
    @patch("requests.get")
    def test_test_connection_failure(self, mock_get, api_client):
        """Test test_connection failure"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        # Test
        result = api_client.test_connection()

        # Assertions
        assert result is False

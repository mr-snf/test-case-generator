"""
Tests for fetch_ticket_details.py script
"""

import os
import json
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Import the script's main class
from fetch_ticket_details import TicketDetailsFetcher


class TestTicketDetailsFetcher:
    """Test class for TicketDetailsFetcher"""

    @pytest.fixture
    def mock_jira_client(self):
        """Fixture for mock Jira client"""
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.get_issue.return_value = {
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
        mock_client.get_issue_description.return_value = "Test issue description"
        return mock_client

    @pytest.fixture
    def fetcher(self, mock_jira_client):
        """Fixture to create TicketDetailsFetcher with mock client"""
        with patch("fetch_ticket_details.JiraAPI") as mock_jira_class:
            mock_jira_class.return_value = mock_jira_client
            fetcher = TicketDetailsFetcher()
            return fetcher

    @pytest.mark.unit
    def test_fetcher_initialization(self, mock_jira_client):
        """Test TicketDetailsFetcher initialization"""
        with patch("fetch_ticket_details.JiraAPI") as mock_jira_class:
            mock_jira_class.return_value = mock_jira_client

            fetcher = TicketDetailsFetcher()

            assert fetcher.jira_client == mock_jira_client
            mock_jira_class.assert_called_once()

    @pytest.mark.unit
    def test_fetcher_initialization_error(self):
        """Test TicketDetailsFetcher initialization with error"""
        with patch("fetch_ticket_details.JiraAPI") as mock_jira_class:
            mock_jira_class.side_effect = ValueError("Configuration error")

            with pytest.raises(SystemExit):
                TicketDetailsFetcher()

    @pytest.mark.unit
    def test_test_connection_success(self, fetcher, mock_jira_client):
        """Test successful connection test"""
        result = fetcher.test_connection()

        assert result is True
        mock_jira_client.test_connection.assert_called_once()

    @pytest.mark.unit
    def test_test_connection_failure(self, fetcher, mock_jira_client):
        """Test failed connection test"""
        mock_jira_client.test_connection.return_value = False

        result = fetcher.test_connection()

        assert result is False

    @pytest.mark.unit
    def test_get_ticket_details_success(self, fetcher, mock_jira_client):
        """Test successful ticket details retrieval"""
        ticket_details = fetcher.get_ticket_details("TEST-123")

        assert ticket_details is not None
        assert ticket_details["ticket_id"] == "TEST-123"
        assert ticket_details["key"] == "TEST-123"
        assert ticket_details["summary"] == "Test Issue Summary"
        assert ticket_details["description"] == "Test issue description"
        assert len(ticket_details["attachments"]) == 1
        assert ticket_details["attachments"][0]["filename"] == "test.pdf"

    @pytest.mark.unit
    def test_get_ticket_details_not_found(self, fetcher, mock_jira_client):
        """Test ticket details retrieval for non-existent ticket"""
        mock_jira_client.get_issue.return_value = {}

        ticket_details = fetcher.get_ticket_details("TEST-999")

        assert ticket_details == {}

    @pytest.mark.unit
    def test_get_attachments(self, fetcher):
        """Test attachment processing"""
        attachments = [
            {
                "filename": "test1.pdf",
                "size": 1024,
                "mimeType": "application/pdf",
                "created": "2024-01-01T11:00:00.000Z",
                "author": {"displayName": "John Doe"},
                "content": "https://example.com/attachment/test1.pdf",
                "thumbnail": "https://example.com/thumbnail/test1.pdf",
            },
            {
                "filename": "test2.jpg",
                "size": 2048,
                "mimeType": "image/jpeg",
                "created": "2024-01-01T12:00:00.000Z",
                "author": {"displayName": "Jane Smith"},
                "content": "https://example.com/attachment/test2.jpg",
                "thumbnail": "https://example.com/thumbnail/test2.jpg",
            },
        ]

        processed = fetcher._get_attachments(attachments)

        assert len(processed) == 2
        assert processed[0]["filename"] == "test1.pdf"
        assert processed[0]["size"] == 1024
        assert processed[0]["mime_type"] == "application/pdf"
        assert processed[0]["author"] == "John Doe"
        assert processed[1]["filename"] == "test2.jpg"
        assert processed[1]["size"] == 2048

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_json(self, mock_file, fetcher):
        """Test saving ticket details to JSON"""
        ticket_details = {
            "ticket_id": "TEST-123",
            "summary": "Test Issue",
            "description": "Test description",
        }

        result = fetcher.save_to_json(ticket_details, "test_output.json")

        assert result == "test_output.json"
        mock_file.assert_called_once_with("test_output.json", "w", encoding="utf-8")

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_json_default_filename(self, mock_file, fetcher):
        """Test saving ticket details with default filename"""
        ticket_details = {"ticket_id": "TEST-123", "summary": "Test Issue"}

        result = fetcher.save_to_json(ticket_details)

        assert result == "ticket_details_TEST-123.json"
        mock_file.assert_called_once_with(
            "ticket_details_TEST-123.json", "w", encoding="utf-8"
        )

    @pytest.mark.unit
    @patch("builtins.print")
    def test_print_summary(self, mock_print, fetcher):
        """Test printing ticket summary"""
        ticket_details = {
            "ticket_id": "TEST-123",
            "summary": "Test Issue Summary",
            "description": "This is a test issue description that should be truncated for preview.",
            "attachments": [{"filename": "test.pdf", "size": 1024}],
        }

        fetcher.print_summary(ticket_details)

        # Verify that print was called multiple times (summary output)
        assert mock_print.call_count > 0

    @pytest.mark.unit
    @patch("builtins.print")
    def test_print_summary_empty(self, mock_print, fetcher):
        """Test printing summary for empty ticket details"""
        fetcher.print_summary({})

        mock_print.assert_called_with("❌ No ticket details to display")

    @pytest.mark.unit
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_download_attachments_no_attachments(self, mock_print, mock_mkdir, fetcher):
        """Test downloading attachments when there are none"""
        ticket_details = {"attachments": []}

        result = fetcher.download_attachments(ticket_details)

        assert result == []
        mock_print.assert_called_with("📎 No attachments to download")

    @pytest.mark.unit
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_download_attachments_success(self, mock_print, mock_mkdir, fetcher):
        """Test successful attachment download"""
        ticket_details = {
            "attachments": [
                {
                    "filename": "test.pdf",
                    "url": "https://example.com/attachment/test.pdf",
                }
            ]
        }

        # Mock the session and response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"PDF content"
        fetcher.jira_client._session.get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            result = fetcher.download_attachments(ticket_details, "test_dir")

        assert len(result) == 1
        assert result[0] == os.path.join("test_dir", "test.pdf")
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @pytest.mark.unit
    @patch("pathlib.Path.mkdir")
    @patch("builtins.print")
    def test_download_attachments_no_url(self, mock_print, mock_mkdir, fetcher):
        """Test downloading attachments with missing URL"""
        ticket_details = {"attachments": [{"filename": "test.pdf", "url": ""}]}

        result = fetcher.download_attachments(ticket_details)

        assert result == []
        # Check that the skip message was called (among other print calls)
        mock_print.assert_any_call("  ⚠️  Skipping test.pdf: No download URL")


class TestFetchTicketDetailsIntegration:
    """Integration tests for fetch_ticket_details.py"""

    @pytest.mark.integration
    @patch("fetch_ticket_details.TicketDetailsFetcher")
    def test_main_function_success(self, mock_fetcher_class):
        """Test main function with successful execution"""
        # Mock the fetcher
        mock_fetcher = Mock()
        mock_fetcher.test_connection.return_value = True
        mock_fetcher.get_ticket_details.return_value = {
            "ticket_id": "TEST-123",
            "summary": "Test Issue",
        }
        mock_fetcher_class.return_value = mock_fetcher

        # Import and run main
        from fetch_ticket_details import main

        main()

        # Verify calls
        mock_fetcher.test_connection.assert_called_once()
        mock_fetcher.get_ticket_details.assert_called_once()
        mock_fetcher.print_summary.assert_called_once()
        mock_fetcher.save_to_json.assert_called_once()
        mock_fetcher.download_attachments.assert_called_once()

    @pytest.mark.integration
    @patch("fetch_ticket_details.TicketDetailsFetcher")
    def test_main_function_connection_failure(self, mock_fetcher_class):
        """Test main function with connection failure"""
        # Mock the fetcher
        mock_fetcher = Mock()
        mock_fetcher.test_connection.return_value = False
        mock_fetcher_class.return_value = mock_fetcher

        # Import and run main
        from fetch_ticket_details import main

        with pytest.raises(SystemExit):
            main()

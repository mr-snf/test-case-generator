"""
Tests for the extract_test_cases.py functionality.
"""

from unittest.mock import Mock, mock_open, patch

import pytest

from extract_test_cases import create_extraction_summary, extract_test_cases


class TestExtractTestCases:
    """Test class for extract_test_cases functionality"""

    @pytest.fixture
    def sample_test_cases(self):
        """Fixture for sample test cases"""
        return [
            {
                "id": 1,
                "title": "User Login with Valid Credentials",
                "type_id": 1,  # Functional
                "priority_id": 3,  # High (not 4)
                "section_id": 1,
                "custom_preconds": "User has a registered account",
                "custom_steps_separated": [
                    {
                        "content": "Navigate to login page",
                        "expected": "Login form is displayed",
                    }
                ],
                "custom_test_data": "test@example.com / password123",
            },
            {
                "id": 2,
                "title": "User Login with Invalid Email",
                "type_id": 1,  # Functional
                "priority_id": 2,  # Medium (not 3)
                "section_id": 1,
                "custom_preconds": "User is on login page",
                "custom_steps_separated": [
                    {
                        "content": "Enter invalid email format",
                        "expected": "Email validation error is displayed",
                    }
                ],
                "custom_test_data": "invalid-email / password123",
            },
        ]

    @pytest.mark.unit
    def test_create_extraction_summary(self, sample_test_cases):
        """Test extraction summary creation"""
        summary = create_extraction_summary(sample_test_cases)

        assert "Test Case Extraction Summary" in summary
        assert "Total Test Cases: 2" in summary
        assert "Breakdown by Priority:" in summary
        assert "Breakdown by Type:" in summary
        assert "Breakdown by Section:" in summary
        assert "High: 1" in summary
        assert "Medium: 1" in summary
        assert "Functional: 2" in summary
        assert "Section 1: 2" in summary

    @pytest.mark.unit
    def test_create_extraction_summary_empty(self):
        """Test extraction summary with empty test cases"""
        summary = create_extraction_summary([])
        assert "No test cases extracted." in summary

    @pytest.mark.unit
    @patch("extract_test_cases.TestRailAPI")
    @patch("extract_test_cases.PROJECT_ID", 9)  # Mock the project ID
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_extract_test_cases_success(
        self, mock_makedirs, mock_file, mock_api_class, sample_test_cases
    ):
        """Test successful test case extraction"""
        # Setup mock API
        mock_api = Mock()
        mock_api.get_projects.return_value = [{"id": 9, "name": "Test Project"}]
        mock_api.export_test_cases_to_json.return_value = sample_test_cases
        mock_api_class.return_value = mock_api

        # Run extraction
        extract_test_cases()

        # Verify API calls
        mock_api.get_projects.assert_called_once()
        mock_api.export_test_cases_to_json.assert_called_once()

        # Verify file operations
        mock_makedirs.assert_called_once_with("knowledgebase", exist_ok=True)
        mock_file.assert_called_once()

    @pytest.mark.unit
    @patch("extract_test_cases.TestRailAPI")
    @patch("extract_test_cases.PROJECT_ID", 9)  # Mock the project ID
    @patch("os.makedirs")
    def test_extract_test_cases_project_not_found(self, mock_makedirs, mock_api_class):
        """Test extraction when project is not found"""
        # Setup mock API
        mock_api = Mock()
        mock_api.get_projects.return_value = [{"id": 2, "name": "Other Project"}]
        mock_api_class.return_value = mock_api

        # Run extraction
        extract_test_cases()

        # Verify API calls
        mock_api.get_projects.assert_called_once()
        # Should not call export_test_cases_to_json when project not found

    @pytest.mark.unit
    @patch("extract_test_cases.TestRailAPI")
    @patch("extract_test_cases.PROJECT_ID", 9)  # Mock the project ID
    @patch("os.makedirs")
    def test_extract_test_cases_api_error(self, mock_makedirs, mock_api_class):
        """Test extraction with API error"""
        # Setup mock API to raise exception
        mock_api = Mock()
        mock_api.get_projects.side_effect = Exception("API Error")
        mock_api_class.return_value = mock_api

        # Run extraction (should handle error gracefully and exit)
        with pytest.raises(SystemExit, match="1"):
            extract_test_cases()

        # Verify API was called
        mock_api.get_projects.assert_called_once()

    @pytest.mark.unit
    @patch("extract_test_cases.TestRailAPI")
    @patch("extract_test_cases.PROJECT_ID", 9)  # Mock the project ID
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_extract_test_cases_no_test_cases(
        self, mock_makedirs, mock_file, mock_api_class
    ):
        """Test test case extraction when no test cases exist"""
        # Setup mock API
        mock_api = Mock()
        mock_api.get_projects.return_value = [{"id": 9, "name": "Test Project"}]
        mock_api.export_test_cases_to_json.return_value = []
        mock_api_class.return_value = mock_api

        # Run extraction
        extract_test_cases()

        # Verify API calls
        mock_api.get_projects.assert_called_once()
        mock_api.export_test_cases_to_json.assert_called_once()

        # Verify directory creation (should still happen)
        mock_makedirs.assert_called_once_with("knowledgebase", exist_ok=True)

        # Note: When no test cases are found, no file is written
        # So we don't expect mock_file to be called

    @pytest.mark.unit
    def test_create_extraction_summary_with_unknown_fields(self):
        """Test extraction summary with unknown priority/type values"""
        test_cases = [
            {
                "id": 1,
                "title": "Test Case 1",
                "priority_id": 999,  # Unknown priority
                "type_id": 999,  # Unknown type
                "section_id": 999,  # Unknown section
            }
        ]

        summary = create_extraction_summary(test_cases)

        assert "Unknown (999)" in summary
        assert "Total Test Cases: 1" in summary

    @pytest.mark.unit
    def test_create_extraction_summary_priority_mapping(self):
        """Test priority mapping in summary creation"""
        test_cases = [
            {"id": 1, "priority_id": 1, "type_id": 1, "section_id": 1},  # Low
            {"id": 2, "priority_id": 2, "type_id": 1, "section_id": 1},  # Medium
            {"id": 3, "priority_id": 3, "type_id": 1, "section_id": 1},  # High
            {"id": 4, "priority_id": 4, "type_id": 1, "section_id": 1},  # Critical
        ]

        summary = create_extraction_summary(test_cases)

        assert "Low: 1" in summary
        assert "Medium: 1" in summary
        assert "High: 1" in summary
        assert "Critical: 1" in summary

    @pytest.mark.unit
    def test_create_extraction_summary_type_mapping(self):
        """Test type mapping in summary creation"""
        test_cases = [
            {"id": 1, "priority_id": 1, "type_id": 1, "section_id": 1},  # Functional
            {"id": 2, "priority_id": 1, "type_id": 2, "section_id": 1},  # Accessibility
            {"id": 3, "priority_id": 1, "type_id": 3, "section_id": 1},  # Performance
            {"id": 4, "priority_id": 1, "type_id": 4, "section_id": 1},  # Usability
        ]

        summary = create_extraction_summary(test_cases)

        assert "Functional: 1" in summary
        assert "Accessibility: 1" in summary
        assert "Performance: 1" in summary
        assert "Usability: 1" in summary

    @pytest.mark.unit
    def test_create_extraction_summary_section_grouping(self):
        """Test section grouping in summary creation"""
        test_cases = [
            {"id": 1, "priority_id": 1, "type_id": 1, "section_id": 1},
            {"id": 2, "priority_id": 1, "type_id": 1, "section_id": 1},
            {"id": 3, "priority_id": 1, "type_id": 1, "section_id": 2},
            {"id": 4, "priority_id": 1, "type_id": 1, "section_id": 3},
        ]

        summary = create_extraction_summary(test_cases)

        assert "Section 1: 2" in summary
        assert "Section 2: 1" in summary
        assert "Section 3: 1" in summary

"""
TestRail API client tests using pytest.
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open

from src.testrail import TestRailAPI


class TestTestRailAPI:
    """Test class for TestRail API client"""

    @pytest.fixture
    def api_client(self):
        """Fixture to create TestRail API client"""
        return TestRailAPI()

    @pytest.fixture
    def mock_api_response(self):
        """Fixture for mock API responses"""
        return {
            "projects": [
                {"id": 1, "name": "Test Project 1"},
                {"id": 2, "name": "Test Project 2"},
            ],
            "suites": [
                {"id": 1, "name": "Test Suite 1"},
                {"id": 2, "name": "Test Suite 2"},
            ],
            "sections": [
                {"id": 1, "name": "Test Section 1"},
                {"id": 2, "name": "Test Section 2"},
            ],
            "cases": [
                {"id": 1, "title": "Test Case 1"},
                {"id": 2, "title": "Test Case 2"},
            ],
            "fields": [
                {"id": 1, "name": "custom_field_1"},
                {"id": 2, "name": "custom_field_2"},
            ],
            "priorities": [
                {"id": 1, "name": "Low"},
                {"id": 2, "name": "Medium"},
                {"id": 3, "name": "High"},
            ],
            "types": [
                {"id": 1, "name": "Functional"},
                {"id": 2, "name": "Accessibility"},
            ],
        }

    @pytest.mark.unit
    def test_api_client_initialization(self, api_client):
        """Test TestRail API client initialization"""
        assert api_client is not None
        assert hasattr(api_client, "base_url")
        assert hasattr(api_client, "username")
        assert hasattr(api_client, "password")
        assert hasattr(api_client, "project_id")
        assert hasattr(api_client, "suite_id")

    @pytest.mark.unit
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_URL": "https://your-domain.testrail.io",
            "TESTRAIL_USERNAME": "your-email@domain.com",
            "TESTRAIL_PASSWORD": "your-api-key-or-password",
            "TESTRAIL_PROJECT_ID": "1",
            "TESTRAIL_SUITE_ID": "1",
        },
        clear=True,
    )
    def test_api_client_default_values(self):
        """Test default configuration values"""
        import importlib
        import configs.config
        import src.testrail.api

        # Reload the modules to pick up the new environment variables
        importlib.reload(configs.config)
        importlib.reload(src.testrail.api)

        from src.testrail import TestRailAPI

        api_client = TestRailAPI()
        assert api_client.base_url == "https://your-domain.testrail.io"
        assert api_client.username == "your-email@domain.com"
        assert api_client.password == "your-api-key-or-password"
        assert api_client.project_id == 1
        assert api_client.suite_id == 1

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_projects_success(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_projects call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["projects"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_projects()

        # Assertions
        assert result == mock_api_response["projects"]
        mock_client.send_get.assert_called_once_with("get_projects")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_projects_error(self, mock_client_class, api_client):
        """Test get_projects with API error"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_projects()

        # Assertions
        assert result == []

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_suites_success(self, mock_client_class, api_client, mock_api_response):
        """Test successful get_suites call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["suites"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_suites(1)

        # Assertions
        assert result == mock_api_response["suites"]
        mock_client.send_get.assert_called_once_with("get_suites/1")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_sections_success(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_sections call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["sections"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_sections(1, 1)

        # Assertions
        assert result == mock_api_response["sections"]
        mock_client.send_get.assert_called_once_with("get_sections/1&suite_id=1")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_success(
        self, mock_print, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_cases call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["cases"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1, 1, 1)

        # Assertions
        assert result == mock_api_response["cases"]
        mock_client.send_get.assert_called_once_with(
            "get_cases/1&limit=250&offset=0&suite_id=1&section_id=1"
        )

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_pagination(self, mock_print, mock_client_class, api_client):
        """Test get_cases with pagination (multiple pages)"""
        # Setup mock to return different responses for each call
        mock_client = Mock()

        # First call: return 250 cases (full page)
        first_page = [{"id": i, "title": f"Test Case {i}"} for i in range(1, 251)]
        # Second call: return 100 cases (partial page - end of results)
        second_page = [{"id": i, "title": f"Test Case {i}"} for i in range(251, 351)]

        mock_client.send_get.side_effect = [first_page, second_page]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert len(result) == 350  # 250 + 100
        assert mock_client.send_get.call_count == 2

        # Check the calls were made with correct parameters
        expected_calls = [
            "get_cases/1&limit=250&offset=0",
            "get_cases/1&limit=250&offset=250",
        ]
        actual_calls = [call[0][0] for call in mock_client.send_get.call_args_list]
        assert actual_calls == expected_calls

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_pagination_with_filters(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases pagination with suite_id and section_id filters"""
        # Setup mock
        mock_client = Mock()
        first_page = [{"id": i, "title": f"Test Case {i}"} for i in range(1, 251)]
        second_page = [{"id": i, "title": f"Test Case {i}"} for i in range(251, 351)]

        mock_client.send_get.side_effect = [first_page, second_page]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test with filters
        result = api_client.get_cases(1, suite_id=5, section_id=10)

        # Assertions
        assert len(result) == 350
        assert mock_client.send_get.call_count == 2

        # Check the calls were made with correct parameters including filters
        expected_calls = [
            "get_cases/1&limit=250&offset=0&suite_id=5&section_id=10",
            "get_cases/1&limit=250&offset=250&suite_id=5&section_id=10",
        ]
        actual_calls = [call[0][0] for call in mock_client.send_get.call_args_list]
        assert actual_calls == expected_calls

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_dict_response_format(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with dict response format containing 'cases' key"""
        # Setup mock
        mock_client = Mock()
        cases_data = [
            {"id": 1, "title": "Test Case 1"},
            {"id": 2, "title": "Test Case 2"},
        ]
        dict_response = {"cases": cases_data}

        mock_client.send_get.return_value = dict_response
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == cases_data
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_dict_response_with_data_key(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with dict response format containing 'data' key"""
        # Setup mock
        mock_client = Mock()
        cases_data = [
            {"id": 1, "title": "Test Case 1"},
            {"id": 2, "title": "Test Case 2"},
        ]
        dict_response = {"data": cases_data}

        mock_client.send_get.return_value = dict_response
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == cases_data
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_single_case_dict_response(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with single case returned as dict"""
        # Setup mock
        mock_client = Mock()
        single_case = {"id": 1, "title": "Single Test Case"}

        mock_client.send_get.return_value = single_case
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == [single_case]  # Should be wrapped in a list
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_empty_response(self, mock_print, mock_client_class, api_client):
        """Test get_cases with empty response"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = []
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == []
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_unexpected_response_type(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with unexpected response type"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = "unexpected_string_response"
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == []
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_safety_limit(self, mock_print, mock_client_class, api_client):
        """Test get_cases with safety limit to prevent infinite loops"""
        # Setup mock to return full pages indefinitely
        mock_client = Mock()
        full_page = [{"id": i, "title": f"Test Case {i}"} for i in range(1, 251)]
        mock_client.send_get.return_value = full_page
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions - should stop at safety limit (10000 offset)
        # With limit=250, this means 41 calls (10000/250 + 1 for the final check)
        # The last call adds 250 more cases before the safety limit is hit
        assert mock_client.send_get.call_count == 41
        assert len(result) == 10250  # 41 * 250 (the last call adds 250 more cases)

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_error_handling(self, mock_print, mock_client_class, api_client):
        """Test get_cases error handling"""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == []
        mock_client.send_get.assert_called_once_with("get_cases/1&limit=250&offset=0")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_case_fields_success(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_case_fields call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["fields"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_case_fields()

        # Assertions
        assert result == mock_api_response["fields"]
        mock_client.send_get.assert_called_once_with("get_case_fields")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_priorities_success(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_priorities call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["priorities"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_priorities()

        # Assertions
        assert result == mock_api_response["priorities"]
        mock_client.send_get.assert_called_once_with("get_priorities")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_case_types_success(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test successful get_case_types call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["types"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_case_types()

        # Assertions
        assert result == mock_api_response["types"]
        mock_client.send_get.assert_called_once_with("get_case_types")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_add_case_success(self, mock_client_class, api_client):
        """Test successful add_case call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_post.return_value = {"id": 1, "title": "New Test Case"}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test data
        case_data = {"title": "New Test Case", "type_id": 1, "priority_id": 3}

        # Test
        result = api_client.add_case(1, case_data)

        # Assertions
        assert result == {"id": 1, "title": "New Test Case"}
        mock_client.send_post.assert_called_once_with("add_case/1", case_data)

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_add_case_error(self, mock_client_class, api_client):
        """Test add_case with API error"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test data
        case_data = {"title": "Test Case"}

        # Test - should return empty dict on error, not raise exception
        result = api_client.add_case(1, case_data)
        assert result == {}

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("builtins.print")
    def test_export_test_cases_to_json_success(
        self,
        mock_print,
        mock_makedirs,
        mock_file,
        mock_client_class,
        api_client,
        mock_api_response,
    ):
        """Test successful export_test_cases_to_json call"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["cases"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.export_test_cases_to_json(1, "test.json")

        # Assertions
        assert result == mock_api_response["cases"]
        mock_client.send_get.assert_called()
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_export_test_cases_to_json_error(
        self, mock_print, mock_client_class, api_client
    ):
        """Test export_test_cases_to_json with API error"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.export_test_cases_to_json(1, "test.json")

        # Assertions
        assert result == []

    @pytest.mark.unit
    def test_format_test_case_for_testrail(self, api_client):
        """Test test case formatting for TestRail"""
        # Test data
        test_case = {
            "title": "Test User Login",
            "type": "positive",
            "priority": "High",
            "preconditions": "User has valid credentials",
            "steps": [
                {
                    "step": "Navigate to login page",
                    "expected": "Login form is displayed",
                },
                {
                    "step": "Enter valid credentials",
                    "expected": "User is logged in successfully",
                },
            ],
            "test_data": "test@example.com / password123",
        }

        # Test
        formatted = api_client.format_test_case_for_testrail(test_case)

        # Assertions
        assert formatted["title"] == "Test User Login"
        assert formatted["type_id"] == 1  # Functional
        assert formatted["priority_id"] == 4  # High
        assert formatted["custom_preconds"] == "User has valid credentials"
        assert len(formatted["custom_steps_separated"]) == 2
        assert (
            formatted["custom_steps_separated"][0]["content"]
            == "Navigate to login page"
        )
        assert (
            formatted["custom_steps_separated"][0]["expected"]
            == "Login form is displayed"
        )

    @pytest.mark.unit
    def test_format_test_case_edge_cases(self, api_client):
        """Test test case formatting with edge cases"""
        # Test with missing fields
        test_case = {
            "title": "Minimal Test Case",
        }

        # Test
        formatted = api_client.format_test_case_for_testrail(test_case)

        # Assertions
        assert formatted["title"] == "Minimal Test Case"
        assert formatted["type_id"] == 1  # Default to Functional
        assert formatted["priority_id"] == 3  # Default to Medium
        assert formatted["custom_preconds"] == ""
        assert len(formatted["custom_steps_separated"]) == 0

    @pytest.mark.unit
    def test_format_test_case_priority_mapping(self, api_client):
        """Test priority mapping in test case formatting"""
        # Test all priority levels
        priorities = ["Low", "Medium", "High", "Critical"]
        expected_ids = [2, 3, 4, 5]

        for priority, expected_id in zip(priorities, expected_ids):
            test_case = {
                "title": f"Test with {priority} priority",
                "priority": priority,
            }

            formatted = api_client.format_test_case_for_testrail(test_case)
            assert formatted["priority_id"] == expected_id

    @pytest.mark.unit
    def test_format_test_case_type_mapping(self, api_client):
        """Test type mapping in test case formatting"""
        # Test all type mappings
        types = ["positive", "negative", "edge", "accessibility"]
        expected_ids = [
            1,
            1,
            1,
            2,
        ]  # positive/negative/edge -> Functional, accessibility -> Accessibility

        for test_type, expected_id in zip(types, expected_ids):
            test_case = {
                "title": f"Test with {test_type} type",
                "type": test_type,
            }

            formatted = api_client.format_test_case_for_testrail(test_case)
            assert formatted["type_id"] == expected_id

    @pytest.mark.unit
    def test_format_test_case_complex_steps(self, api_client):
        """Test formatting test cases with complex step structures"""
        test_case = {
            "title": "Complex Test Case",
            "type": "negative",
            "priority": "Critical",
            "preconditions": "System is running",
            "steps": [
                {"step": "Step 1: Do something", "expected": "Expected result 1"},
                {"step": "Step 2: Do something else", "expected": "Expected result 2"},
                {"step": "Step 3: Final step", "expected": "Final expected result"},
            ],
            "test_data": "Complex test data",
        }

        formatted = api_client.format_test_case_for_testrail(test_case)

        # Assertions
        assert formatted["title"] == "Complex Test Case"
        assert formatted["type_id"] == 1  # Functional (negative)
        assert formatted["priority_id"] == 5  # Critical
        assert formatted["custom_preconds"] == "System is running"
        assert len(formatted["custom_steps_separated"]) == 3
        assert formatted["custom_steps_separated"][2]["content"] == "Step 3: Final step"
        assert (
            formatted["custom_steps_separated"][2]["expected"]
            == "Final expected result"
        )

    @pytest.mark.unit
    def test_format_test_case_empty_steps(self, api_client):
        """Test formatting test cases with empty steps"""
        test_case = {
            "title": "Test with Empty Steps",
            "type": "positive",
            "priority": "Medium",
            "preconditions": "No preconditions",
            "steps": [],
            "test_data": "",
        }

        formatted = api_client.format_test_case_for_testrail(test_case)

        # Assertions
        assert formatted["title"] == "Test with Empty Steps"
        assert formatted["type_id"] == 1  # Functional
        assert formatted["priority_id"] == 3  # Medium
        assert formatted["custom_preconds"] == "No preconditions"
        assert len(formatted["custom_steps_separated"]) == 0

    @pytest.mark.unit
    def test_format_test_case_malformed_steps(self, api_client):
        """Test formatting test cases with malformed step data"""
        test_case = {
            "title": "Test with Malformed Steps",
            "type": "positive",
            "priority": "Low",
            "steps": [
                {"step": "Valid step", "expected": "Valid expected"},
                {"step": "Step without expected"},
                {"expected": "Expected without step"},
                {"invalid_field": "Invalid data"},
            ],
        }

        formatted = api_client.format_test_case_for_testrail(test_case)

        # Assertions
        assert formatted["title"] == "Test with Malformed Steps"
        assert len(formatted["custom_steps_separated"]) == 4
        # Should handle malformed steps gracefully
        assert formatted["custom_steps_separated"][0]["content"] == "Valid step"
        assert formatted["custom_steps_separated"][0]["expected"] == "Valid expected"
        assert (
            formatted["custom_steps_separated"][1]["content"] == "Step without expected"
        )
        assert formatted["custom_steps_separated"][1]["expected"] == ""

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    def test_get_sections_with_suite_id(
        self, mock_client_class, api_client, mock_api_response
    ):
        """Test get_sections with specific suite ID"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["sections"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_sections(1, 2)  # Different suite ID

        # Assertions
        assert result == mock_api_response["sections"]
        mock_client.send_get.assert_called_once_with("get_sections/1&suite_id=2")

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_without_section_id(
        self, mock_print, mock_client_class, api_client, mock_api_response
    ):
        """Test get_cases without section ID"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["cases"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1, 1)  # No section ID

        # Assertions
        assert result == mock_api_response["cases"]
        mock_client.send_get.assert_called_once_with(
            "get_cases/1&limit=250&offset=0&suite_id=1"
        )

    @pytest.mark.api
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_with_section_id(
        self, mock_print, mock_client_class, api_client, mock_api_response
    ):
        """Test get_cases with section ID"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = mock_api_response["cases"]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1, 1, 5)  # With section ID

        # Assertions
        assert result == mock_api_response["cases"]
        mock_client.send_get.assert_called_once_with(
            "get_cases/1&limit=250&offset=0&suite_id=1&section_id=5"
        )


@pytest.mark.integration
class TestTestRailIntegration:
    """Integration tests for TestRail API (requires real connection)"""

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_URL": "https://test.testrail.io",
            "TESTRAIL_USERNAME": "test@example.com",
            "TESTRAIL_PASSWORD": "test-password",
            "TESTRAIL_PROJECT_ID": "1",
        },
    )
    def test_real_connection(self):
        """Test real TestRail connection (with mock credentials)"""
        # This test will use mock credentials but test the connection logic
        api_client = TestRailAPI()

        # Test connection method exists
        assert hasattr(api_client, "test_connection")
        assert callable(api_client.test_connection)

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_URL": "https://test.testrail.io",
            "TESTRAIL_USERNAME": "test@example.com",
            "TESTRAIL_PASSWORD": "test-password",
            "TESTRAIL_PROJECT_ID": "1",
        },
    )
    def test_real_api_endpoints(self):
        """Test real API endpoints (with mock credentials)"""
        api_client = TestRailAPI()

        # Test that all required methods exist
        required_methods = [
            "get_projects",
            "get_suites",
            "get_sections",
            "get_cases",
            "add_case",
            "update_case",
            "delete_case",
            "export_test_cases_to_json",
        ]

        for method in required_methods:
            assert hasattr(api_client, method), f"Method {method} not found"
            assert callable(
                getattr(api_client, method)
            ), f"Method {method} is not callable"

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_URL": "https://test.testrail.io",
            "TESTRAIL_USERNAME": "test@example.com",
            "TESTRAIL_PASSWORD": "test-password",
            "TESTRAIL_PROJECT_ID": "1",
        },
    )
    def test_real_test_case_operations(self):
        """Test real test case operations (with mock credentials)"""
        api_client = TestRailAPI()

        # Test test case formatting
        test_case = {
            "title": "Test Case",
            "type": "positive",
            "priority": "High",
            "preconditions": "User is logged in",
            "steps": [{"step": "Click button", "expected": "Button is clicked"}],
        }

        formatted = api_client.format_test_case_for_testrail(test_case)
        assert "title" in formatted
        assert "type_id" in formatted
        assert "priority_id" in formatted
        assert "custom_preconds" in formatted
        assert "custom_steps_separated" in formatted

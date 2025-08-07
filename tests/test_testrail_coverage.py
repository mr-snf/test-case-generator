"""
Additional tests to improve coverage for TestRail API and client modules.
"""

import pytest
from unittest.mock import Mock, patch, mock_open

from src.testrail.client import APIClient, APIError
from src.testrail.api import TestRailAPI


class TestTestRailAPICoverage:
    """Additional tests to improve TestRail API coverage"""

    @pytest.fixture
    def api_client(self):
        """Fixture to create TestRail API client"""
        return TestRailAPI()

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_suites_error(self, mock_client_class, api_client):
        """Test get_suites with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_suites(1)
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_sections_error(self, mock_client_class, api_client):
        """Test get_sections with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_sections(1)
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_cases_error(self, mock_client_class, api_client):
        """Test get_cases with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_cases(1)
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_pagination_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases pagination for coverage"""
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

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_dict_response_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with dict response format for coverage"""
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

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_data_key_response_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with 'data' key response format for coverage"""
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

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_single_dict_response_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with single dict response for coverage"""
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

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_empty_response_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with empty response for coverage"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = []
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_unexpected_response_type_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases with unexpected response type for coverage"""
        # Setup mock
        mock_client = Mock()
        mock_client.send_get.return_value = "unexpected_string_response"
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        # Test
        result = api_client.get_cases(1)

        # Assertions
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_get_cases_safety_limit_coverage(
        self, mock_print, mock_client_class, api_client
    ):
        """Test get_cases safety limit for coverage"""
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

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_case_success(self, mock_client_class, api_client):
        """Test get_case success"""
        mock_client = Mock()
        mock_client.send_get.return_value = {"id": 1, "title": "Test Case"}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_case(1)
        assert result == {"id": 1, "title": "Test Case"}
        mock_client.send_get.assert_called_once_with("get_case/1")

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_case_error(self, mock_client_class, api_client):
        """Test get_case with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_case(1)
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_update_case_success(self, mock_client_class, api_client):
        """Test update_case success"""
        mock_client = Mock()
        mock_client.send_post.return_value = {"id": 1, "title": "Updated Case"}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        case_data = {"title": "Updated Case"}
        result = api_client.update_case(1, case_data)
        assert result == {"id": 1, "title": "Updated Case"}
        mock_client.send_post.assert_called_once_with("update_case/1", case_data)

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_update_case_error(self, mock_client_class, api_client):
        """Test update_case with API error"""
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.update_case(1, {"title": "Test"})
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_delete_case_success(self, mock_client_class, api_client):
        """Test delete_case success"""
        mock_client = Mock()
        mock_client.send_post.return_value = {"success": True}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.delete_case(1)
        assert result == {"success": True}
        mock_client.send_post.assert_called_once_with("delete_case/1", {})

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_delete_case_error(self, mock_client_class, api_client):
        """Test delete_case with API error"""
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.delete_case(1)
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_add_section_success(self, mock_client_class, api_client):
        """Test add_section success"""
        mock_client = Mock()
        mock_client.send_post.return_value = {"id": 1, "name": "New Section"}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        section_data = {"name": "New Section"}
        result = api_client.add_section(1, section_data)
        assert result == {"id": 1, "name": "New Section"}
        mock_client.send_post.assert_called_once_with("add_section/1", section_data)

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_add_section_error(self, mock_client_class, api_client):
        """Test add_section with API error"""
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.add_section(1, {"name": "Test"})
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_update_section_success(self, mock_client_class, api_client):
        """Test update_section success"""
        mock_client = Mock()
        mock_client.send_post.return_value = {"id": 1, "name": "Updated Section"}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        section_data = {"name": "Updated Section"}
        result = api_client.update_section(1, section_data)
        assert result == {"id": 1, "name": "Updated Section"}
        mock_client.send_post.assert_called_once_with("update_section/1", section_data)

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_update_section_error(self, mock_client_class, api_client):
        """Test update_section with API error"""
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.update_section(1, {"name": "Test"})
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_delete_section_success(self, mock_client_class, api_client):
        """Test delete_section success"""
        mock_client = Mock()
        mock_client.send_post.return_value = {"success": True}
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.delete_section(1)
        assert result == {"success": True}
        mock_client.send_post.assert_called_once_with("delete_section/1", {})

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_delete_section_error(self, mock_client_class, api_client):
        """Test delete_section with API error"""
        mock_client = Mock()
        mock_client.send_post.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.delete_section(1)
        assert result == {}

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_case_fields_error(self, mock_client_class, api_client):
        """Test get_case_fields with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_case_fields()
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_priorities_error(self, mock_client_class, api_client):
        """Test get_priorities with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_priorities()
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_get_case_types_error(self, mock_client_class, api_client):
        """Test get_case_types with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.get_case_types()
        assert result == []

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_test_connection_success(self, mock_client_class, api_client):
        """Test test_connection success"""
        mock_client = Mock()
        mock_client.send_get.return_value = [{"id": 1, "name": "Project 1"}]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.test_connection()
        assert result is True

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_test_connection_no_projects(self, mock_client_class, api_client):
        """Test test_connection with no projects"""
        mock_client = Mock()
        mock_client.send_get.return_value = []
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.test_connection()
        assert result is False

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    def test_test_connection_error(self, mock_client_class, api_client):
        """Test test_connection with API error"""
        mock_client = Mock()
        mock_client.send_get.side_effect = Exception("Connection Error")
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.test_connection()
        assert result is False

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_test_connection_success_with_print(
        self, mock_print, mock_client_class, api_client
    ):
        """Test test_connection success with print statement coverage"""
        mock_client = Mock()
        mock_client.send_get.return_value = [{"id": 1, "name": "Project 1"}]
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.test_connection()
        assert result is True
        mock_print.assert_called_with(
            "Successfully connected to TestRail. Found 1 projects."
        )

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_test_connection_no_projects_with_print(
        self, mock_print, mock_client_class, api_client
    ):
        """Test test_connection with no projects and print statement coverage"""
        mock_client = Mock()
        mock_client.send_get.return_value = []
        mock_client_class.return_value = mock_client
        api_client.client = mock_client

        result = api_client.test_connection()
        assert result is False
        mock_print.assert_called_with("Connected to TestRail but no projects found.")

    @pytest.mark.unit
    @patch("src.testrail.api.APIClient")
    @patch("builtins.print")
    def test_test_connection_error_with_print(
        self, mock_print, mock_client_class, api_client
    ):
        """Test test_connection with API error and print statement coverage"""
        # Mock the get_projects method directly to raise an exception
        with patch.object(
            api_client, "get_projects", side_effect=Exception("Connection Error")
        ):
            result = api_client.test_connection()
            assert result is False
            mock_print.assert_called_with(
                "Failed to connect to TestRail: Connection Error"
            )


class TestTestRailClientCoverage:
    """Additional tests to improve TestRail client coverage"""

    @pytest.fixture
    def client(self):
        """Fixture to create APIClient"""
        return APIClient("https://test.testrail.io")

    @pytest.mark.unit
    def test_client_initialization_with_trailing_slash(self):
        """Test APIClient initialization with trailing slash"""
        client = APIClient("https://test.testrail.io/")
        # Access private attribute using name mangling
        assert client._APIClient__url == "https://test.testrail.io/index.php?/api/v2/"

    @pytest.mark.unit
    def test_client_initialization_without_trailing_slash(self):
        """Test APIClient initialization without trailing slash"""
        client = APIClient("https://test.testrail.io")
        # Access private attribute using name mangling
        assert client._APIClient__url == "https://test.testrail.io/index.php?/api/v2/"

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_success(self, mock_get, client):
        """Test send_get success"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        result = client.send_get("get_projects")
        assert result == {"success": True}

    @pytest.mark.unit
    @patch("requests.post")
    def test_send_post_success(self, mock_post, client):
        """Test send_post success"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        result = client.send_post("add_case/1", {"title": "Test"})
        assert result == {"success": True}

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_error_status(self, mock_get, client):
        """Test send_get with error status code"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_get.return_value = mock_response

        with pytest.raises(APIError):
            client.send_get("get_projects")

    @pytest.mark.unit
    @patch("requests.post")
    def test_send_post_error_status(self, mock_post, client):
        """Test send_post with error status code"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_post.return_value = mock_response

        with pytest.raises(APIError):
            client.send_post("add_case/1", {"title": "Test"})

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_error_non_json(self, mock_get, client):
        """Test send_get with non-JSON error response"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.content = b"Error message"
        mock_get.return_value = mock_response

        with pytest.raises(APIError):
            client.send_get("get_projects")

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_attachment(self, mock_get, client):
        """Test send_get for attachment download"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"attachment content"
        mock_get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            result = client.send_get("get_attachment/1", "test.txt")
            assert result == "test.txt"

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_attachment_error(self, mock_get, client):
        """Test send_get for attachment download with error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"attachment content"
        mock_get.return_value = mock_response

        with patch("builtins.open", side_effect=Exception("File error")):
            result = client.send_get("get_attachment/1", "test.txt")
            assert result == "Error saving attachment."

    @pytest.mark.unit
    @patch("requests.post")
    def test_send_post_attachment(self, mock_post, client):
        """Test send_post for attachment upload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        with patch("builtins.open", mock_open(read_data=b"file content")):
            result = client.send_post("add_attachment/1", "test.txt")
            assert result == {"success": True}

    @pytest.mark.unit
    @patch("requests.post")
    def test_send_post_json_error(self, mock_post, client):
        """Test send_post with JSON parsing error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("JSON Error")
        mock_post.return_value = mock_response

        result = client.send_post("add_case/1", {"title": "Test"})
        assert result == {}

    @pytest.mark.unit
    @patch("requests.get")
    def test_send_get_json_error(self, mock_get, client):
        """Test send_get with JSON parsing error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("JSON Error")
        mock_get.return_value = mock_response

        result = client.send_get("get_projects")
        assert result == {}

    @pytest.mark.unit
    def test_api_error_exception(self):
        """Test APIError exception"""
        error = APIError("Test error")
        assert str(error) == "Test error"

"""
Tests for the save_test_cases.py functionality.
"""

import pytest
from unittest.mock import Mock, patch, mock_open


from save_test_cases import TestCaseSaver, OutputFormatter


class TestOutputFormatter:
    """Test class for OutputFormatter"""

    @pytest.fixture
    def formatter(self):
        """Fixture to create OutputFormatter"""
        return OutputFormatter()

    @pytest.fixture
    def sample_test_cases(self):
        """Fixture for sample test cases"""
        return [
            {
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
        ]

    @pytest.mark.unit
    def test_formatter_initialization(self, formatter):
        """Test OutputFormatter initialization"""
        assert formatter is not None

    @pytest.mark.unit
    @patch("os.makedirs")
    def test_ensure_target_directory(self, mock_makedirs, formatter):
        """Test target directory creation"""
        formatter._ensure_target_directory()
        mock_makedirs.assert_called_once_with("target", exist_ok=True)

    @pytest.mark.unit
    def test_format_for_testrail(self, formatter, sample_test_cases):
        """Test test case formatting for TestRail"""
        formatted = formatter.format_for_testrail(sample_test_cases)

        assert len(formatted) == 1
        formatted_case = formatted[0]

        assert formatted_case["title"] == "Test User Login"
        assert formatted_case["type_id"] == 1  # Functional
        assert formatted_case["priority_id"] == 4  # High
        assert formatted_case["custom_preconds"] == "User has valid credentials"
        assert len(formatted_case["custom_steps_separated"]) == 2
        assert (
            formatted_case["custom_steps_separated"][0]["content"]
            == "Navigate to login page"
        )
        assert (
            formatted_case["custom_steps_separated"][0]["expected"]
            == "Login form is displayed"
        )

    @pytest.mark.unit
    def test_format_for_testrail_empty(self, formatter):
        """Test formatting empty test cases"""
        formatted = formatter.format_for_testrail([])
        assert formatted == []

    @pytest.mark.unit
    def test_get_testrail_type_id(self, formatter):
        """Test TestRail type ID mapping"""
        assert formatter._get_testrail_type_id("positive") == 1
        assert formatter._get_testrail_type_id("negative") == 1
        assert formatter._get_testrail_type_id("edge") == 1
        assert formatter._get_testrail_type_id("accessibility") == 2
        assert formatter._get_testrail_type_id("unknown") == 1  # Default

    @pytest.mark.unit
    def test_get_testrail_priority_id(self, formatter):
        """Test TestRail priority ID mapping"""
        assert formatter._get_testrail_priority_id("High") == 4
        assert formatter._get_testrail_priority_id("Medium") == 3
        assert formatter._get_testrail_priority_id("Low") == 2
        assert formatter._get_testrail_priority_id("Critical") == 5
        assert formatter._get_testrail_priority_id("Unknown") == 3  # Default

    @pytest.mark.unit
    def test_format_for_testrail_missing_fields(self, formatter):
        """Test formatting test cases with missing fields"""
        test_case = {
            "title": "Minimal Test Case",
            # Missing type, priority, preconditions, steps
        }

        formatted = formatter.format_for_testrail([test_case])

        assert len(formatted) == 1
        formatted_case = formatted[0]
        assert formatted_case["title"] == "Minimal Test Case"
        assert formatted_case["type_id"] == 1  # Default
        assert formatted_case["priority_id"] == 3  # Default
        assert formatted_case["custom_preconds"] == ""
        assert len(formatted_case["custom_steps_separated"]) == 0

    @pytest.mark.unit
    def test_format_for_testrail_complex_steps(self, formatter):
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
        }

        formatted = formatter.format_for_testrail([test_case])

        assert len(formatted) == 1
        formatted_case = formatted[0]
        assert formatted_case["type_id"] == 1  # Functional (negative)
        assert formatted_case["priority_id"] == 5  # Critical
        assert len(formatted_case["custom_steps_separated"]) == 3
        assert (
            formatted_case["custom_steps_separated"][2]["content"]
            == "Step 3: Final step"
        )
        assert (
            formatted_case["custom_steps_separated"][2]["expected"]
            == "Final expected result"
        )

    @pytest.mark.unit
    def test_format_for_testrail_already_formatted(self, formatter):
        """Test formatting test cases that are already in TestRail format"""
        already_formatted_cases = [
            {
                "id": 11,
                "title": "Already Formatted Test",
                "type": "positive",
                "priority": "High",
                "custom_preconds": "Setup required",
                "custom_steps_separated": [
                    {"content": "Step 1", "expected": "Result 1"},
                    {"content": "Step 2", "expected": "Result 2"},
                ],
                "similarity_score": 0.85,
                "similarity_reasons": ["Test reason"],
                "similar_to_existing_id": 1,
            }
        ]

        result = formatter.format_for_testrail(already_formatted_cases)

        assert len(result) == 1
        assert result[0]["title"] == "Already Formatted Test"
        assert result[0]["type_id"] == 1  # Should be added
        assert result[0]["priority_id"] == 4  # Should be added
        assert result[0]["custom_preconds"] == "Setup required"
        assert len(result[0]["custom_steps_separated"]) == 2
        # Duplicate detection fields should be removed
        assert "similarity_score" not in result[0]
        assert "similarity_reasons" not in result[0]
        assert "similar_to_existing_id" not in result[0]

    @pytest.mark.unit
    def test_format_for_testrail_mixed_formats(self, formatter):
        """Test formatting test cases with mixed formats"""
        mixed_test_cases = [
            {
                "title": "Standard Format Test",
                "type": "positive",
                "priority": "Medium",
                "preconditions": "Setup required",
                "steps": [
                    {"step": "Step 1", "expected": "Result 1"},
                ],
            },
            {
                "id": 12,
                "title": "TestRail Format Test",
                "type": "negative",
                "priority": "Low",
                "custom_preconds": "Setup required",
                "custom_steps_separated": [
                    {"content": "Step 1", "expected": "Result 1"},
                ],
                "similarity_score": 0.75,
            }
        ]

        result = formatter.format_for_testrail(mixed_test_cases)

        assert len(result) == 2
        
        # First case should be formatted from standard to TestRail
        assert result[0]["title"] == "Standard Format Test"
        assert result[0]["type_id"] == 1
        assert result[0]["priority_id"] == 3
        assert result[0]["custom_preconds"] == "Setup required"
        
        # Second case should remain in TestRail format with fields added/removed
        assert result[1]["title"] == "TestRail Format Test"
        assert result[1]["type_id"] == 1
        assert result[1]["priority_id"] == 2
        assert "similarity_score" not in result[1]


class TestTestCaseSaver:
    """Test class for TestCaseSaver"""

    @pytest.fixture
    def saver(self):
        """Fixture to create TestCaseSaver"""
        return TestCaseSaver()

    @pytest.fixture
    def sample_test_cases(self):
        """Fixture for sample test cases"""
        return [
            {
                "title": "Test User Login",
                "type": "positive",
                "priority": "High",
                "preconditions": "User has valid credentials",
                "steps": [
                    {
                        "step": "Navigate to login page",
                        "expected": "Login form is displayed",
                    },
                ],
                "test_data": "test@example.com / password123",
            }
        ]

    @pytest.mark.unit
    def test_saver_initialization(self, saver):
        """Test TestCaseSaver initialization"""
        assert saver is not None
        assert hasattr(saver, "testrail_api")
        assert hasattr(saver, "output_formatter")
        assert hasattr(saver, "project_id")
        assert hasattr(saver, "suite_id")
        assert hasattr(saver, "default_section_id")

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open, read_data='[{"title": "Test"}]')
    @patch("os.path.exists", return_value=True)
    def test_load_test_cases_from_json_success(self, mock_exists, mock_file, saver):
        """Test successful JSON test case loading"""
        result = saver.load_test_cases_from_json("test.json")
        assert len(result) == 1
        assert result[0]["title"] == "Test"

    @pytest.mark.unit
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"test_cases": [{"title": "Test"}]}',
    )
    @patch("os.path.exists", return_value=True)
    def test_load_test_cases_from_json_with_test_cases_field(
        self, mock_exists, mock_file, saver
    ):
        """Test JSON loading with test_cases field"""
        result = saver.load_test_cases_from_json("test.json")
        assert len(result) == 1
        assert result[0]["title"] == "Test"

    @pytest.mark.unit
    @patch("builtins.open", side_effect=Exception("File error"))
    @patch("os.path.exists", return_value=True)
    def test_load_test_cases_from_json_error(self, mock_exists, mock_file, saver):
        """Test JSON loading with error"""
        result = saver.load_test_cases_from_json("test.json")
        assert result == []

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    @patch("os.path.exists", return_value=True)
    def test_load_test_cases_from_json_invalid_json(
        self, mock_exists, mock_file, saver
    ):
        """Test JSON loading with invalid JSON"""
        result = saver.load_test_cases_from_json("test.json")
        assert result == []

    @pytest.mark.unit
    def test_save_to_testrail_success(self, saver, sample_test_cases):
        """Test successful TestRail saving"""
        # Mock the API methods
        saver.testrail_api.get_sections = Mock(
            return_value=[{"id": 1, "name": "Test Section"}]
        )
        saver.testrail_api.add_case = Mock(
            return_value={"id": 1, "title": "Test User Login"}
        )

        result = saver.save_to_testrail(sample_test_cases)

        assert len(result) == 1
        assert result[0]["title"] == "Test User Login"
        saver.testrail_api.add_case.assert_called_once()

    @pytest.mark.unit
    def test_save_to_testrail_empty(self, saver):
        """Test saving empty test cases"""
        result = saver.save_to_testrail([])
        assert result == []

    @pytest.mark.unit
    def test_save_to_testrail_with_section_id(self, saver, sample_test_cases):
        """Test saving with specific section ID"""
        # Mock the API
        saver.testrail_api.add_case = Mock(
            return_value={"id": 1, "title": "Test User Login"}
        )

        result = saver.save_to_testrail(sample_test_cases, section_id=5)

        assert len(result) == 1
        # Should use the provided section_id
        saver.testrail_api.add_case.assert_called_once()

    @pytest.mark.unit
    def test_save_to_testrail_api_error(self, saver, sample_test_cases):
        """Test saving with API error"""
        # Mock the API to raise exception
        saver.testrail_api.get_sections = Mock(
            return_value=[{"id": 1, "name": "Test Section"}]
        )
        saver.testrail_api.add_case = Mock(side_effect=Exception("API Error"))

        result = saver.save_to_testrail(sample_test_cases)

        assert len(result) == 0  # Should return empty list on error

    @pytest.mark.unit
    def test_save_to_testrail_no_sections_found(self, saver, sample_test_cases):
        """Test saving when no sections are found"""
        # Mock the API to return no sections
        saver.testrail_api.get_sections = Mock(return_value=[])
        saver.default_section_id = 1  # Default value

        with pytest.raises(Exception, match="No sections found in TestRail project"):
            saver.save_to_testrail(sample_test_cases)

    @pytest.mark.unit
    @patch("os.listdir")
    @patch("os.path.exists", return_value=True)
    def test_save_all_from_target_success(
        self, mock_exists, mock_listdir, saver, sample_test_cases
    ):
        """Test saving all test cases from target directory"""
        # Mock directory listing with the exact filename the implementation expects
        mock_listdir.return_value = ["generated_test_cases.json"]

        # Mock file loading
        saver.load_test_cases_from_json = Mock(return_value=sample_test_cases)

        # Mock TestRail saving
        saver.save_to_testrail = Mock(return_value=[{"id": 1, "title": "Test"}])

        # Run the method
        saver.save_all_from_target()

        # Verify calls
        saver.load_test_cases_from_json.assert_called_once()
        saver.save_to_testrail.assert_called_once()

    @pytest.mark.unit
    @patch("os.path.exists", return_value=False)
    def test_save_all_from_target_directory_not_found(self, mock_exists, saver):
        """Test saving when target directory doesn't exist"""
        saver.save_all_from_target()
        # Should handle gracefully without error

    @pytest.mark.unit
    @patch("os.listdir", return_value=[])
    @patch("os.path.exists", return_value=True)
    def test_save_all_from_target_no_files(self, mock_exists, mock_listdir, saver):
        """Test saving when no files in target directory"""
        saver.save_all_from_target()
        # Should handle gracefully without error

    @pytest.mark.unit
    @patch("os.listdir", return_value=["test.txt", "test.csv"])  # Non-JSON files
    @patch("os.path.exists", return_value=True)
    def test_save_all_from_target_no_json_files(self, mock_exists, mock_listdir, saver):
        """Test saving when no JSON files in target directory"""
        saver.save_all_from_target()
        # Should handle gracefully without error

    @pytest.mark.unit
    @patch("os.listdir", return_value=["generated_test_cases.json", "other_file.json"])
    @patch("os.path.exists", return_value=True)
    def test_save_all_from_target_multiple_files(
        self, mock_exists, mock_listdir, saver
    ):
        """Test saving from multiple JSON files"""
        # Mock file loading for the file that matches the expected name
        saver.load_test_cases_from_json = Mock(return_value=[{"title": "Test 1"}])

        # Mock TestRail saving
        saver.save_to_testrail = Mock(return_value=[{"id": 1, "title": "Test"}])

        # Run the method
        saver.save_all_from_target()

        # Verify calls - only the matching file should be processed
        saver.load_test_cases_from_json.assert_called_once()
        saver.save_to_testrail.assert_called_once()

    @pytest.mark.unit
    def test_save_to_testrail_partial_failure(self, saver, sample_test_cases):
        """Test saving when some test cases fail to save"""
        # Mock the API to fail on second case
        saver.testrail_api.get_sections = Mock(
            return_value=[{"id": 1, "name": "Test Section"}]
        )
        saver.testrail_api.add_case = Mock(
            side_effect=[
                {"id": 1, "title": "Test User Login"},  # First case succeeds
                Exception("API Error"),  # Second case fails
            ]
        )

        # Create two test cases
        two_test_cases = sample_test_cases + [{"title": "Test Case 2"}]

        result = saver.save_to_testrail(two_test_cases)

        # Should return only the successful case
        assert len(result) == 1
        assert result[0]["title"] == "Test User Login"

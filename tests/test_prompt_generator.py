"""
Tests for the prompt generator functionality.
"""

import pytest
from unittest.mock import Mock, patch, mock_open


from generate_prompt import PromptGeneratorOrchestrator


class TestPromptGeneratorOrchestrator:
    """Test class for PromptGeneratorOrchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Fixture to create PromptGeneratorOrchestrator"""
        return PromptGeneratorOrchestrator()

    @pytest.fixture
    def sample_test_cases(self):
        """Fixture for sample test cases"""
        return [
            {
                "id": 1,
                "title": "User Login with Valid Credentials",
                "type": "positive",
                "priority": "High",
                "section_id": 1,
                "custom_preconds": "User has a registered account",
                "custom_steps_separated": [
                    {
                        "content": "Navigate to login page",
                        "expected": "Login form is displayed",
                    },
                    {
                        "content": "Enter valid email address",
                        "expected": "Email field accepts input",
                    },
                ],
                "custom_test_data": "test@example.com / password123",
            },
            {
                "id": 2,
                "title": "User Login with Invalid Email",
                "type": "negative",
                "priority": "Medium",
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

    @pytest.fixture
    def sample_features(self):
        """Fixture for sample feature files"""
        return [
            {
                "filename": "example_feature.md",
                "content": """
# User Login Feature

## Functional Requirements
- Users can log in using email and password
- System validates credentials

## Security Requirements
- Passwords are encrypted
- Account lockout after failed attempts

## Accessibility Requirements
- Screen reader compatibility
- Keyboard navigation support
                """,
                "path": "feature/example_feature.md",
            }
        ]

    @pytest.mark.unit
    def test_orchestrator_initialization(self, orchestrator):
        """Test PromptGeneratorOrchestrator initialization"""
        assert orchestrator is not None
        assert hasattr(orchestrator, "knowledge_base_file")
        assert hasattr(orchestrator, "feature_dir")
        assert hasattr(orchestrator, "target_dir")
        assert hasattr(orchestrator, "config_file")

    @pytest.mark.unit
    def test_orchestrator_default_paths(self, orchestrator):
        """Test default file paths"""
        assert (
            orchestrator.knowledge_base_file == "knowledgebase/existing_test_cases.json"
        )
        assert orchestrator.feature_dir == "feature"
        assert orchestrator.target_dir == "target"
        assert orchestrator.config_file == "configs/output_test_case_config.py"

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    @patch("os.path.exists", return_value=True)
    def test_read_knowledge_base_success(self, mock_exists, mock_file, orchestrator):
        """Test successful knowledge base reading"""
        result = orchestrator.read_knowledge_base()
        assert result == []
        mock_file.assert_called_once()

    @pytest.mark.unit
    @patch("os.path.exists", return_value=False)
    def test_read_knowledge_base_file_not_found(self, mock_exists, orchestrator):
        """Test knowledge base reading when file doesn't exist"""
        result = orchestrator.read_knowledge_base()
        assert result == []

    @pytest.mark.unit
    @patch("builtins.open", side_effect=Exception("File error"))
    @patch("os.path.exists", return_value=True)
    def test_read_knowledge_base_error(self, mock_exists, mock_file, orchestrator):
        """Test knowledge base reading with error"""
        result = orchestrator.read_knowledge_base()
        assert result == []

    @pytest.mark.unit
    def test_analyze_test_case_patterns(self, orchestrator, sample_test_cases):
        """Test test case pattern analysis"""
        patterns = orchestrator.analyze_test_case_patterns(sample_test_cases)

        assert "types" in patterns
        assert "priorities" in patterns
        assert "naming_conventions" in patterns
        assert "step_patterns" in patterns
        assert "common_preconditions" in patterns
        assert "custom_fields" in patterns
        assert "field_variations" in patterns
        assert "step_formats" in patterns

        # Check specific patterns
        assert patterns["types"]["positive"] == 1
        assert patterns["types"]["negative"] == 1
        assert patterns["priorities"]["High"] == 1
        assert patterns["priorities"]["Medium"] == 1
        assert len(patterns["naming_conventions"]) == 2
        assert len(patterns["step_patterns"]) == 3

    @pytest.mark.unit
    def test_analyze_test_case_patterns_empty(self, orchestrator):
        """Test pattern analysis with empty test cases"""
        patterns = orchestrator.analyze_test_case_patterns([])
        assert patterns == {}

    @pytest.mark.unit
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open, read_data="# Test Feature")
    @patch("os.path.exists", return_value=True)
    def test_read_feature_files_success(
        self, mock_exists, mock_file, mock_glob, orchestrator
    ):
        """Test successful feature file reading"""
        # Mock glob to return a file path
        mock_file_path = Mock()
        mock_file_path.name = "test_feature.md"
        mock_glob.return_value = [mock_file_path]

        result = orchestrator.read_feature_files()

        assert len(result) == 1
        assert result[0]["filename"] == "test_feature.md"
        assert result[0]["content"] == "# Test Feature"

    @pytest.mark.unit
    @patch("os.path.exists", return_value=False)
    def test_read_feature_files_directory_not_found(self, mock_exists, orchestrator):
        """Test feature file reading when directory doesn't exist"""
        result = orchestrator.read_feature_files()
        assert result == []

    @pytest.mark.unit
    def test_extract_feature_requirements(self, orchestrator, sample_features):
        """Test feature requirements extraction"""
        requirements = orchestrator.extract_feature_requirements(sample_features)

        assert "functional" in requirements
        assert "security" in requirements
        assert "accessibility" in requirements
        assert "technical" in requirements
        assert "performance" in requirements
        assert "api_endpoints" in requirements
        assert "database" in requirements
        assert "browser_support" in requirements

        # Check that requirements were found
        assert len(requirements["functional"]) == 1
        assert len(requirements["security"]) == 1
        assert len(requirements["accessibility"]) == 1

    @pytest.mark.unit
    def test_extract_feature_requirements_empty(self, orchestrator):
        """Test requirements extraction with empty features"""
        requirements = orchestrator.extract_feature_requirements([])

        # All requirement types should be empty lists
        for req_type in requirements.values():
            assert req_type == []

    @pytest.mark.unit
    @patch("generate_prompt.DEFAULT_TEST_CASES_COUNT", 15)
    @patch("generate_prompt.DEFAULT_TEST_TYPES", ["positive", "negative", "edge"])
    @patch(
        "generate_prompt.DEFAULT_PRIORITY_DISTRIBUTION",
        {"High": 40, "Medium": 40, "Low": 20},
    )
    @patch("generate_prompt.SIMILARITY_THRESHOLD", 0.85)
    def test_read_configuration_success(self, orchestrator):
        """Test successful configuration reading"""
        config = orchestrator.read_configuration()

        assert config["test_case_count"] > 0
        assert config["test_types"] == ["positive", "negative", "edge"]
        assert config["priority_distribution"]["High"] == 40
        assert config["priority_distribution"]["Medium"] == 40
        assert config["priority_distribution"]["Low"] == 20
        # Test that wcag_guideline is not included when accessibility is not in test_types
        assert "wcag_guideline" not in config

    @pytest.mark.unit
    @patch("generate_prompt.DEFAULT_TEST_CASES_COUNT", 15)
    @patch(
        "generate_prompt.DEFAULT_TEST_TYPES",
        ["positive", "negative", "edge", "accessibility"],
    )
    @patch(
        "generate_prompt.DEFAULT_PRIORITY_DISTRIBUTION",
        {"High": 40, "Medium": 40, "Low": 20},
    )
    @patch("generate_prompt.SIMILARITY_THRESHOLD", 0.85)
    @patch("generate_prompt.WCAG_GUIDLINE", "WCAG 2.2 AA")
    def test_read_configuration_with_accessibility(self, orchestrator):
        """Test configuration reading when accessibility is included"""
        config = orchestrator.read_configuration()

        assert config["test_case_count"] > 0
        assert "accessibility" in config["test_types"]
        assert config["priority_distribution"]["High"] == 40
        # Test that wcag_guideline is included when accessibility is in test_types
        assert "wcag_guideline" in config
        assert config["wcag_guideline"] == "WCAG 2.2 AA"

    @pytest.mark.unit
    @patch("os.path.exists", return_value=False)
    def test_read_configuration_file_not_found(self, mock_exists, orchestrator):
        """Test configuration reading with default values"""
        config = orchestrator.read_configuration()

        assert config["test_case_count"] > 10
        assert set(config["test_types"]).issubset(
            {"positive", "negative", "edge", "accessibility"}
        )
        assert (
            config["priority_distribution"]["High"]
            + config["priority_distribution"]["Medium"]
            + config["priority_distribution"]["Low"]
            == 100
        )

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open)
    def test_save_test_cases(self, mock_file, orchestrator, sample_test_cases):
        """Test saving test cases"""
        orchestrator.save_test_cases(sample_test_cases, "test_feature")

        # Check that file was opened for writing
        mock_file.assert_called()
        # Check that json.dump was called (indirectly through file write)

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open)
    def test_create_summary(self, mock_file, orchestrator, sample_test_cases):
        """Test summary creation"""
        filepath = "target/test_feature_test_cases.json"
        orchestrator.create_summary(sample_test_cases, filepath)

        # Check that summary file was created
        mock_file.assert_called()

    @pytest.mark.unit
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="# Test Case Generator\n## 🎯 Objective",
    )
    @patch("os.path.exists", return_value=True)
    def test_save_prompt_data(self, mock_exists, mock_file, orchestrator):
        """Test saving prompt data to file"""
        prompt_data = {
            "existing_test_cases": [],
            "patterns": {"types": {}, "priorities": {}},
            "features": [],
            "requirements": {
                "functional": [],
                "security": [],
                "accessibility": [],
                "performance": [],
                "api_endpoints": [],
                "database": [],
                "browser_support": [],
                "technical": [],
            },
            "config": {
                "test_case_count": 10,
                "test_types": ["positive", "negative"],
                "priority_distribution": {"High": 30, "Medium": 50, "Low": 20},
                "wcag_guideline": "WCAG 2.2 AA",
            },
        }

        orchestrator.save_prompt_data(prompt_data)

        # Verify file was opened for writing (the new implementation only writes once)
        assert mock_file.call_count >= 1

    @pytest.mark.unit
    @patch.object(PromptGeneratorOrchestrator, "read_knowledge_base")
    @patch.object(PromptGeneratorOrchestrator, "analyze_test_case_patterns")
    @patch.object(PromptGeneratorOrchestrator, "read_feature_files")
    @patch.object(PromptGeneratorOrchestrator, "extract_feature_requirements")
    @patch.object(PromptGeneratorOrchestrator, "read_configuration")
    @patch.object(PromptGeneratorOrchestrator, "save_prompt_data")
    def test_run_workflow(
        self,
        mock_save_prompt,
        mock_config,
        mock_req,
        mock_features,
        mock_patterns,
        mock_kb,
        orchestrator,
    ):
        """Test complete workflow execution"""
        # Setup mocks
        mock_kb.return_value = []
        mock_patterns.return_value = {}
        mock_features.return_value = []
        mock_req.return_value = {}
        mock_config.return_value = {
            "test_case_count": 10,
            "test_types": ["positive", "negative"],
            "priority_distribution": {"High": 30, "Medium": 50, "Low": 20},
        }

        # Run workflow
        result = orchestrator.run_workflow()

        # Verify all methods were called
        mock_kb.assert_called_once()
        mock_patterns.assert_called_once()
        mock_features.assert_called_once()
        mock_req.assert_called_once()
        mock_config.assert_called_once()
        mock_save_prompt.assert_called_once()

        # Verify result structure
        assert "existing_test_cases" in result
        assert "patterns" in result
        assert "features" in result
        assert "requirements" in result
        assert "config" in result

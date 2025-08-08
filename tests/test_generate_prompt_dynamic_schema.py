import json
import pytest
from unittest.mock import patch

from generate_prompt import PromptGeneratorOrchestrator


class TestDynamicSchemaDerivation:
    @pytest.fixture
    def orchestrator(self):
        return PromptGeneratorOrchestrator()

    def test_numeric_and_boolean_placeholders(self, orchestrator):
        samples = [
            {
                "title": "Sample",
                "type_id": 16,
                "priority_id": 2,
                "custom_preconds": "{}",
                "custom_steps_separated": [{"content": "Do X", "expected": "See Y"}],
                "custom_automation_type": 1,
                "custom_flag": True,
            }
        ]
        patterns = {
            "field_variations": {"custom_automation_type": 10, "custom_flag": 8}
        }
        result = orchestrator.derive_format_from_samples(
            samples=samples,
            patterns=patterns,
            existing_cases_count=10,
            existing_cases=samples,
        )

        schema = result["schema"]
        assert isinstance(schema.get("custom_automation_type"), int)
        assert schema.get("custom_automation_type") == 0
        assert isinstance(schema.get("custom_flag"), bool)

    def test_steps_always_nonempty_and_normalized(self, orchestrator):
        samples = [
            {
                "title": "Sample",
                "custom_steps_separated": [],
            }
        ]
        result = orchestrator.derive_format_from_samples(
            samples=samples,
            patterns={"field_variations": {}},
            existing_cases_count=0,
            existing_cases=[],
        )
        schema = result["schema"]
        assert "custom_steps_separated" in schema
        assert isinstance(schema["custom_steps_separated"], list)
        assert len(schema["custom_steps_separated"]) == 1
        first = schema["custom_steps_separated"][0]
        assert first["content"]
        assert first["expected"]


class TestSampleEmbeddingFormatting:
    @pytest.fixture
    def orchestrator(self):
        return PromptGeneratorOrchestrator()

    @patch("generate_prompt.PromptGeneratorOrchestrator.read_knowledge_base")
    @patch("generate_prompt.PromptGeneratorOrchestrator.read_feature_files")
    @patch("generate_prompt.PromptGeneratorOrchestrator.read_configuration")
    def test_embedded_sample_has_nonempty_step_fields(
        self, mock_config, mock_features, mock_kb, orchestrator
    ):
        mock_kb.return_value = [
            {
                "id": 1,
                "title": "Case 1",
                "type_id": 16,
                "priority_id": 2,
                "custom_preconds": "{}",
                "custom_steps_separated": [{"content": "", "expected": ""}],
            },
            {
                "id": 2,
                "title": "Case 2",
                "type_id": 16,
                "priority_id": 2,
                "custom_preconds": "{}",
                "custom_steps_separated": [{"content": "Step", "expected": "Result"}],
            },
        ]
        mock_features.return_value = []
        mock_config.return_value = {
            "test_case_count": 5,
            "test_types": ["positive", "negative"],
            "priority_distribution": {"High": 40, "Medium": 40, "Low": 20},
        }

        # Run to generate prompt and ensure no exceptions
        orchestrator.run_workflow()

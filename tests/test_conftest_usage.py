import pytest


def test_sample_test_cases_fixture(sample_test_cases):
    assert isinstance(sample_test_cases, list)
    assert len(sample_test_cases) >= 2
    first = sample_test_cases[0]
    assert "title" in first
    assert "custom_steps_separated" in first
    assert isinstance(first["custom_steps_separated"], list)


def test_sample_feature_content_fixture(sample_feature_content):
    assert isinstance(sample_feature_content, str)
    assert "User Login Feature" in sample_feature_content


def test_mock_api_responses_fixture(mock_api_responses):
    assert "projects" in mock_api_responses
    assert "fields" in mock_api_responses
    assert any(f["name"].startswith("custom_") for f in mock_api_responses["fields"])


def test_sample_test_cases_varied_templates(sample_test_cases_varied_templates):
    cases = sample_test_cases_varied_templates
    assert any(c.get("template_id") == 2 for c in cases)
    assert any(c.get("template_id") == 3 for c in cases)
    assert any(c.get("template_id") == 7 for c in cases)
    # Ensure at least one has step-based, one exploratory, one BDD fields
    assert any("custom_steps_separated" in c for c in cases)
    assert any("custom_steps" in c and "custom_expected" in c for c in cases)
    assert any("custom_testrail_bdd_scenario" in c for c in cases)

"""
Tests for the output test case configuration module.
"""

import os
from unittest.mock import patch

import pytest

from configs.output_test_case_config import (
    DEFAULT_PRIORITY_DISTRIBUTION,
    DEFAULT_TEST_CASES_COUNT,
    DEFAULT_TEST_TYPES,
    WCAG_GUIDLINE,
)


class TestOutputTestCaseConfig:
    """Test class for output test case configuration settings"""

    @pytest.mark.unit
    def test_config_variables_exist(self):
        """Test that all required config variables are defined"""
        assert DEFAULT_TEST_CASES_COUNT is not None
        assert DEFAULT_TEST_TYPES is not None
        assert DEFAULT_PRIORITY_DISTRIBUTION is not None

    @pytest.mark.unit
    def test_config_types(self):
        """Test that configuration values have correct types"""
        assert isinstance(DEFAULT_TEST_CASES_COUNT, int)
        assert isinstance(DEFAULT_TEST_TYPES, list)
        assert isinstance(DEFAULT_PRIORITY_DISTRIBUTION, dict)

    @pytest.mark.unit
    def test_test_types_content(self):
        """Test that test types contain expected values"""
        for test_type in DEFAULT_TEST_TYPES:
            assert test_type in ["positive", "negative", "edge", "accessibility"]

    @pytest.mark.unit
    def test_priority_distribution_content(self):
        """Test that priority distribution contains expected keys"""
        expected_priorities = ["High", "Medium", "Low"]
        for priority in expected_priorities:
            assert priority in DEFAULT_PRIORITY_DISTRIBUTION

    @pytest.mark.unit
    def test_priority_distribution_percentages(self):
        """Test that priority distribution percentages sum to 100"""
        total_percentage = sum(DEFAULT_PRIORITY_DISTRIBUTION.values())
        assert total_percentage == 100

    @pytest.mark.unit
    def test_wcag_guideline_format(self):
        """Test that WCAG guideline has correct format"""
        if WCAG_GUIDLINE:
            assert "WCAG" in WCAG_GUIDLINE

    @pytest.mark.unit
    def test_config_consistency(self):
        """Test configuration consistency"""
        # Test case count should be positive
        assert DEFAULT_TEST_CASES_COUNT > 0

        # Test types should not be empty
        assert len(DEFAULT_TEST_TYPES) > 0

        # Priority distribution should not be empty
        assert len(DEFAULT_PRIORITY_DISTRIBUTION) > 0

        # All priority percentages should be positive
        for percentage in DEFAULT_PRIORITY_DISTRIBUTION.values():
            assert percentage > 0

    @pytest.mark.unit
    def test_config_importability(self):
        """Test that config can be imported without errors"""
        try:
            from configs.output_test_case_config import (
                DEFAULT_PRIORITY_DISTRIBUTION,
                DEFAULT_TEST_CASES_COUNT,
                DEFAULT_TEST_TYPES,
                WCAG_GUIDLINE,
            )

            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import config variables: {e}")

    @pytest.mark.unit
    def test_config_attributes_accessible(self):
        """Test that config attributes are accessible"""
        # Test that we can access all attributes
        assert hasattr(DEFAULT_TEST_CASES_COUNT, "__class__")
        assert hasattr(DEFAULT_TEST_TYPES, "__class__")
        assert hasattr(DEFAULT_PRIORITY_DISTRIBUTION, "__class__")
        assert hasattr(WCAG_GUIDLINE, "__class__")

    @pytest.mark.unit
    def test_accessibility_in_test_types(self):
        """Test that accessibility is included in test types when WCAG guideline is set"""
        if WCAG_GUIDLINE:
            assert "accessibility" in DEFAULT_TEST_TYPES

    @pytest.mark.unit
    def test_priority_distribution_keys_are_strings(self):
        """Test that priority distribution keys are strings"""
        for key in DEFAULT_PRIORITY_DISTRIBUTION.keys():
            assert isinstance(key, str)

    @pytest.mark.unit
    def test_priority_distribution_values_are_integers(self):
        """Test that priority distribution values are integers"""
        for value in DEFAULT_PRIORITY_DISTRIBUTION.values():
            assert isinstance(value, int)

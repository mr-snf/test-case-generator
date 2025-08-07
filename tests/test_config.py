"""
Tests for the configuration module.
"""

import os
import pytest
from unittest.mock import patch

from configs.config import (
    TESTRAIL_URL,
    TESTRAIL_USERNAME,
    TESTRAIL_PASSWORD,
    PROJECT_ID,
    SUITE_ID,
    TARGET_SECTION_ID,
    API_BASE_URL,
)


class TestConfig:
    """Test class for configuration settings"""

    @pytest.mark.unit
    def test_config_variables_exist(self):
        """Test that all required config variables are defined"""
        assert TESTRAIL_URL is not None
        assert TESTRAIL_USERNAME is not None
        assert TESTRAIL_PASSWORD is not None
        assert PROJECT_ID is not None
        assert SUITE_ID is not None
        assert TARGET_SECTION_ID is not None
        assert API_BASE_URL is not None

    @pytest.mark.unit
    def test_api_base_url_format(self):
        """Test API base URL format"""
        assert API_BASE_URL.startswith("https://")
        assert API_BASE_URL.endswith("/api/v2")
        assert TESTRAIL_URL in API_BASE_URL

    @pytest.mark.unit
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_URL": "https://custom.testrail.io",
            "TESTRAIL_USERNAME": "custom@example.com",
            "TESTRAIL_PASSWORD": "custom-password",
            "TESTRAIL_PROJECT_ID": "5",
            "TESTRAIL_SUITE_ID": "3",
            "TARGET_SECTION_ID": "10",
        },
    )
    def test_config_with_environment_variables(self):
        """Test configuration with environment variables"""
        # Reload the config module to pick up new environment variables
        import importlib
        import configs.config

        importlib.reload(configs.config)

        # Test that environment variables are used
        assert configs.config.TESTRAIL_URL == "https://custom.testrail.io"
        assert configs.config.TESTRAIL_USERNAME == "custom@example.com"
        assert configs.config.TESTRAIL_PASSWORD == "custom-password"
        assert configs.config.PROJECT_ID == 5
        assert configs.config.SUITE_ID == 3
        assert configs.config.TARGET_SECTION_ID == 10

    @pytest.mark.unit
    @patch.dict(
        os.environ,
        {
            "TESTRAIL_PROJECT_ID": "invalid",
            "TESTRAIL_SUITE_ID": "invalid",
            "TARGET_SECTION_ID": "invalid",
        },
    )
    def test_config_with_invalid_integer_values(self):
        """Test configuration with invalid integer values"""
        # This test should verify that invalid values are handled gracefully
        # The actual config module will raise ValueError, which is expected behavior
        with pytest.raises(ValueError, match="invalid literal for int"):
            # Reload the config module to pick up new environment variables
            import importlib
            import configs.config

            importlib.reload(configs.config)

    @pytest.mark.unit
    def test_config_types(self):
        """Test that configuration values have correct types"""
        assert isinstance(TESTRAIL_URL, str)
        assert isinstance(TESTRAIL_USERNAME, str)
        assert isinstance(TESTRAIL_PASSWORD, str)
        assert isinstance(PROJECT_ID, int)
        assert isinstance(SUITE_ID, int)
        assert isinstance(TARGET_SECTION_ID, int)
        assert isinstance(API_BASE_URL, str)

    @pytest.mark.unit
    def test_config_url_format(self):
        """Test that TestRail URL has correct format"""
        assert TESTRAIL_URL.startswith("https://")
        assert "testrail" in TESTRAIL_URL or "your-domain" in TESTRAIL_URL

    @pytest.mark.unit
    def test_config_email_format(self):
        """Test that username looks like an email"""
        assert "@" in TESTRAIL_USERNAME
        assert "." in TESTRAIL_USERNAME

    @pytest.mark.unit
    def test_config_positive_integers(self):
        """Test that integer config values are positive"""
        assert PROJECT_ID > 0
        assert SUITE_ID > 0
        assert TARGET_SECTION_ID > 0

    @pytest.mark.unit
    def test_config_consistency(self):
        """Test configuration consistency"""
        # API_BASE_URL should be derived from TESTRAIL_URL
        expected_api_url = f"{TESTRAIL_URL}/api/v2"
        assert API_BASE_URL == expected_api_url

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_config_without_environment_variables(self):
        """Test configuration without environment variables"""
        import os
        import shutil
        import tempfile

        # Temporarily move the .env file
        env_file_path = os.path.join(os.getcwd(), ".env")
        temp_env_path = None

        if os.path.exists(env_file_path):
            temp_env_path = tempfile.mktemp()
            shutil.move(env_file_path, temp_env_path)

        try:
            # Clear dotenv cache and reload the config module
            import importlib
            import configs.config

            # Reload the config module
            importlib.reload(configs.config)

            # Should use default values
            assert (
                configs.config.TESTRAIL_URL
                == "https://you-forgot-to-set-this.testrail.io"
            )
            assert (
                configs.config.TESTRAIL_USERNAME
                == "i-do-not-know@your-testrail-account.com"
            )
            assert (
                configs.config.TESTRAIL_PASSWORD
                == "what-is-your-testrail-api-key-or-password?"
            )
            assert configs.config.PROJECT_ID == 1
            assert configs.config.SUITE_ID == 1
            assert configs.config.TARGET_SECTION_ID == 1
            assert (
                configs.config.JIRA_URL
                == "https://you-forgot-to-set-this.atlassian.net"
            )
            assert configs.config.JIRA_USERNAME == "i-do-not-know@your-jira-account.com"
            assert (
                configs.config.JIRA_API_TOKEN
                == "what-is-your-jira-api-key-or-password?"
            )
            assert configs.config.JIRA_TICKET_ID == "what-is-the-jira-ticket-id-001"
        finally:
            # Restore the .env file
            if temp_env_path and os.path.exists(temp_env_path):
                shutil.move(temp_env_path, env_file_path)

    @pytest.mark.unit
    def test_config_importability(self):
        """Test that config module can be imported without errors"""
        try:
            import configs.config

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import config module: {e}")

    @pytest.mark.unit
    def test_config_attributes_accessible(self):
        """Test that all config attributes are accessible"""
        config_vars = [
            "TESTRAIL_URL",
            "TESTRAIL_USERNAME",
            "TESTRAIL_PASSWORD",
            "PROJECT_ID",
            "SUITE_ID",
            "TARGET_SECTION_ID",
            "API_BASE_URL",
        ]

        import configs.config

        for var in config_vars:
            assert hasattr(configs.config, var), f"Config variable {var} not found"
            assert (
                getattr(configs.config, var) is not None
            ), f"Config variable {var} is None"

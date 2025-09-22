"""
Jira API client for fetching ticket details.
Uses the official Jira REST API.
"""

from typing import Dict

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException


class JiraAPI:
    """Jira API client for fetching ticket details"""

    __test__ = False  # Prevent pytest from collecting this as a test

    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize Jira API client

        Args:
            base_url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            username: Jira username/email
            api_token: Jira API token (not password)
        """
        self.base_url = base_url
        self.username = username
        self.api_token = api_token

        if not self.base_url or not self.username or not self.api_token:
            raise ValueError(
                "Jira configuration missing. Please provide base_url, username, and api_token "
                "or set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables."
            )

        # Set up authentication
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Create a session for reuse
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)

    def get_issue(self, issue_key: str) -> Dict:
        """
        Get a specific issue by its key (e.g., 'PROJ-123')

        Args:
            issue_key: The issue key (e.g., 'PROJ-123', 'BUG-456')

        Returns:
            Dict containing the issue details
        """
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            response = requests.get(
                url, auth=self.auth, headers=self.headers, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Issue {issue_key} not found")
                return {}
            else:
                print(
                    f"Error fetching issue {issue_key}: {response.status_code} - {response.text}"
                )
                return {}

        except RequestException as e:
            print(f"Error fetching issue {issue_key}: {str(e)}")
            return {}

    def get_issue_description(self, issue_key: str) -> str:
        """
        Get the description of an issue

        Args:
            issue_key: The issue key (e.g., 'PROJ-123')

        Returns:
            Issue description as string, or empty string if not found
        """
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            params = {"fields": "description"}

            response = requests.get(
                url, auth=self.auth, headers=self.headers, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                description = data.get("fields", {}).get("description", "")
                # Handle Atlassian Document Format (ADF) or plain text
                if isinstance(description, dict):
                    # Extract text from ADF format
                    return self._extract_text_from_adf(description)
                return description or ""
            else:
                print(
                    f"Error fetching description for {issue_key}: {response.status_code}"
                )
                return ""

        except RequestException as e:
            print(f"Error fetching description for {issue_key}: {str(e)}")
            return ""

    def _extract_text_from_adf(self, adf_content: Dict) -> str:
        """
        Extract plain text from Atlassian Document Format (ADF)

        Args:
            adf_content: ADF content as dictionary

        Returns:
            Plain text extracted from ADF
        """
        if not isinstance(adf_content, dict):
            return str(adf_content)

        text_parts = []

        def extract_text_recursive(content):
            if isinstance(content, dict):
                if content.get("type") == "text":
                    text_parts.append(content.get("text", ""))
                elif content.get("type") == "paragraph":
                    if "content" in content:
                        for item in content["content"]:
                            extract_text_recursive(item)
                elif "content" in content:
                    for item in content["content"]:
                        extract_text_recursive(item)
            elif isinstance(content, list):
                for item in content:
                    extract_text_recursive(item)

        extract_text_recursive(adf_content)
        return " ".join(text_parts)

    def test_connection(self) -> bool:
        """
        Test the connection to Jira

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch server info
            url = f"{self.base_url}/rest/api/3/serverInfo"
            response = requests.get(
                url, auth=self.auth, headers=self.headers, timeout=10
            )

            if response.status_code == 200:
                server_info = response.json()
                print(
                    f"Successfully connected to Jira. Server: {server_info.get('serverTitle', 'Unknown')}"
                )
                return True
            else:
                print(
                    f"Failed to connect to Jira: {response.status_code} - {response.text}"
                )
                return False

        except RequestException as e:
            print(f"Failed to connect to Jira: {str(e)}")
            return False

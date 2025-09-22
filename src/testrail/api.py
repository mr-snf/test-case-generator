"""
TestRail API client for fetching and creating test cases and sections.
Uses the official TestRail API client.
"""

import json
import os
from typing import Dict, List, Optional

from configs.config import (
    PROJECT_ID,
    SUITE_ID,
    TESTRAIL_PASSWORD,
    TESTRAIL_URL,
    TESTRAIL_USERNAME,
)

from .client import APIClient


class TestRailAPI:
    """TestRail API client for managing test cases"""

    __test__ = False  # Prevent pytest from collecting this as a test

    def __init__(self):
        # Load configuration from environment variables
        self.base_url = TESTRAIL_URL
        self.username = TESTRAIL_USERNAME
        self.password = TESTRAIL_PASSWORD
        self.project_id = PROJECT_ID
        self.suite_id = SUITE_ID

        # Initialize the official TestRail API client
        self.client = APIClient(self.base_url)
        self.client.user = self.username
        self.client.password = self.password

    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        try:
            return self.client.send_get("get_projects")
        except (ConnectionError, TimeoutError) as e:
            print(f"Network error getting projects: {str(e)}")
            return []
        except ValueError as e:
            print(f"Value error getting projects: {str(e)}")
            return []
        except OSError as e:
            print(f"OS error getting projects: {str(e)}")
            return []
        except RuntimeError as e:
            print(f"Runtime error getting projects: {str(e)}")
            return []

    def get_suites(self, project_id: int) -> List[Dict]:
        """Get all test suites for a project"""
        try:
            return self.client.send_get(f"get_suites/{project_id}")
        except ValueError as e:
            print(f"Value error getting suites: {str(e)}")
            return []
        except ConnectionError as e:
            print(f"Connection error getting suites: {str(e)}")
            return []
        except TimeoutError as e:
            print(f"Timeout error getting suites: {str(e)}")
            return []
        except OSError as e:
            print(f"OS error getting suites: {str(e)}")
            return []
        except RuntimeError as e:
            print(f"Runtime error getting suites: {str(e)}")
            return []

    def get_sections(
        self, project_id: int, suite_id: Optional[int] = None
    ) -> List[Dict]:
        """Get all sections for a project and suite"""
        try:
            endpoint = f"get_sections/{project_id}"
            if suite_id:
                endpoint += f"&suite_id={suite_id}"
            return self.client.send_get(endpoint)
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting sections: {str(e)}")
            return []

    def get_cases(
        self,
        project_id: int,
        suite_id: Optional[int] = None,
        section_id: Optional[int] = None,
    ) -> List[Dict]:
        """Get all test cases for a project, suite, and/or section with pagination"""
        try:
            all_cases = []
            offset = 0
            limit = 250
            total_cases = 0

            while True:
                # Build endpoint with proper URL parameter construction
                endpoint = f"get_cases/{project_id}"
                params = [f"limit={limit}", f"offset={offset}"]

                if suite_id:
                    params.append(f"suite_id={suite_id}")
                if section_id:
                    params.append(f"section_id={section_id}")

                # Construct URL with parameters
                if params:
                    endpoint += "&" + "&".join(params)

                print(f"Fetching cases: offset={offset}, limit={limit}")
                response = self.client.send_get(endpoint)

                # Handle different response formats more robustly
                if isinstance(response, dict):
                    if "cases" in response:
                        cases = response["cases"]
                    elif "data" in response:
                        cases = response["data"]
                    else:
                        # If it's a dict but no obvious key, treat it as a single test case
                        cases = [response]
                elif isinstance(response, list):
                    cases = response
                else:
                    print(f"Unexpected response type: {type(response)}")
                    print(f"Response content: {response}")
                    break

                if not cases:
                    print(f"No cases returned at offset {offset}")
                    break

                all_cases.extend(cases)
                total_cases += len(cases)
                print(f"Retrieved {len(cases)} cases, total so far: {total_cases}")

                # Check if we've reached the end (less than limit returned)
                if len(cases) < limit:
                    print(
                        f"Reached end of results. Total cases retrieved: {total_cases}"
                    )
                    break

                offset += limit

                # Safety check to prevent infinite loops
                if offset > 10000:  # Arbitrary large number
                    print(
                        f"Safety limit reached at offset {offset}. Stopping pagination."
                    )
                    break

            return all_cases
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting cases: {str(e)}")
            return []

    def get_case(self, case_id: int) -> Dict:
        """Get a specific test case by ID"""
        try:
            return self.client.send_get(f"get_case/{case_id}")
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting case {case_id}: {str(e)}")
            return {}

    def add_case(self, section_id: int, case_data: Dict) -> Dict:
        """Add a new test case to a section"""
        try:
            return self.client.send_post(f"add_case/{section_id}", case_data)
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error adding case: {str(e)}")
            return {}

    def update_case(self, case_id: int, case_data: Dict) -> Dict:
        """Update an existing test case"""
        try:
            return self.client.send_post(f"update_case/{case_id}", case_data)
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error updating case {case_id}: {str(e)}")
            return {}

    def delete_case(self, case_id: int) -> Dict:
        """Delete a test case"""
        try:
            return self.client.send_post(f"delete_case/{case_id}", {})
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error deleting case {case_id}: {str(e)}")
            return {}

    def add_section(self, project_id: int, section_data: Dict) -> Dict:
        """Add a new section to a project"""
        try:
            return self.client.send_post(f"add_section/{project_id}", section_data)
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error adding section: {str(e)}")
            return {}

    def update_section(self, section_id: int, section_data: Dict) -> Dict:
        """Update an existing section"""
        try:
            return self.client.send_post(f"update_section/{section_id}", section_data)
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error updating section {section_id}: {str(e)}")
            return {}

    def delete_section(self, section_id: int) -> Dict:
        """Delete a section"""
        try:
            return self.client.send_post(f"delete_section/{section_id}", {})
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error deleting section {section_id}: {str(e)}")
            return {}

    def get_case_fields(self) -> List[Dict]:
        """Get all available custom fields for test cases"""
        try:
            return self.client.send_get("get_case_fields")
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting case fields: {str(e)}")
            return []

    def get_priorities(self) -> List[Dict]:
        """Get all available priorities"""
        try:
            return self.client.send_get("get_priorities")
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting priorities: {str(e)}")
            return []

    def get_case_types(self) -> List[Dict]:
        """Get all available case types"""
        try:
            return self.client.send_get("get_case_types")
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Error getting case types: {str(e)}")
            return []

    def format_test_case_for_testrail(self, test_case: Dict) -> Dict:
        """Format a test case dictionary for TestRail API"""
        # Convert priority string to TestRail priority ID
        priority_map = {"High": 4, "Medium": 3, "Low": 2, "Critical": 5}

        # Convert type string to TestRail case type ID
        type_map = {
            "positive": 1,  # Functional
            "negative": 1,  # Functional
            "edge": 1,  # Functional
            "accessibility": 2,  # Accessibility
        }

        formatted_case = {
            "title": test_case.get("title", ""),
            "type_id": type_map.get(test_case.get("type", "positive"), 1),
            "priority_id": priority_map.get(test_case.get("priority", "Medium"), 3),
            "custom_preconds": test_case.get("preconditions", ""),
            "custom_steps_separated": [],
        }

        # Format steps
        for step in test_case.get("steps", []):
            formatted_case["custom_steps_separated"].append(
                {"content": step.get("step", ""), "expected": step.get("expected", "")}
            )

        return formatted_case

    def export_test_cases_to_json(
        self,
        project_id: int,
        output_file: str = "knowledgebase/existing_test_cases.json",
    ):
        """Export all test cases from a project to JSON file"""
        try:
            # Get all test cases for the project
            response = self.get_cases(project_id)

            # Handle different response formats
            if isinstance(response, dict):
                # If it's a dictionary, check if it contains cases in a specific key
                cases_value = response.get("cases")
                data_value = response.get("data")
                if isinstance(cases_value, list):
                    test_cases = cases_value
                elif isinstance(data_value, list):
                    test_cases = data_value
                else:
                    # If it's a dict but no obvious key, treat it as a single test case
                    test_cases = [response]
            elif isinstance(response, list):
                test_cases = response
            else:
                print(f"Unexpected response type: {type(response)}")
                print(f"Response content: {response}")
                return []

            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save to JSON file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(test_cases, f, indent=2, ensure_ascii=False)

            print(f"Exported {len(test_cases)} test cases to {output_file}")
            return test_cases

        except (OSError, IOError, ValueError, TypeError) as e:
            print(f"Error exporting test cases: {str(e)}")
            return []

    def test_connection(self) -> bool:
        """Test the connection to TestRail"""
        try:
            projects = self.get_projects()
            if projects:
                print(
                    f"Successfully connected to TestRail. Found {len(projects)} projects."
                )
                return True
            else:
                print("Connected to TestRail but no projects found.")
                return False
        except (ConnectionError, TimeoutError, ValueError, OSError, RuntimeError) as e:
            print(f"Failed to connect to TestRail: {str(e)}")
            return False

"""
Script to save test cases from target folder to TestRail.
"""

import json
import os
import sys
from typing import Dict, List, Optional

from configs.config import PROJECT_ID, SUITE_ID, TARGET_SECTION_ID
from src.testrail import TestRailAPI


class OutputFormatter:
    """Formatter for saving test cases in different formats"""

    def __init__(self):
        self._ensure_target_directory()

    def _ensure_target_directory(self):
        """Ensure target directory exists"""
        os.makedirs("target", exist_ok=True)

    def format_for_testrail(self, test_cases: List[Dict]) -> List[Dict]:
        """Format test cases for TestRail import"""
        formatted_cases = []

        for case in test_cases:
            # Check if already in TestRail format
            if "custom_steps_separated" in case and "custom_preconds" in case:
                # Already formatted, just ensure type_id and priority_id
                formatted_case = case.copy()
                if "type" in case and "type_id" not in case:
                    formatted_case["type_id"] = self._get_testrail_type_id(
                        case.get("type", "positive")
                    )
                if "priority" in case and "priority_id" not in case:
                    formatted_case["priority_id"] = self._get_testrail_priority_id(
                        case.get("priority", "Medium")
                    )
            else:
                # Need to format from standard format
                formatted_case = {
                    "title": case.get("title", ""),
                    "type_id": self._get_testrail_type_id(case.get("type", "positive")),
                    "priority_id": self._get_testrail_priority_id(
                        case.get("priority", "Medium")
                    ),
                    "custom_preconds": case.get(
                        "preconditions", case.get("custom_preconds", "")
                    ),
                    "custom_steps_separated": [],
                }

                # Format steps for TestRail
                steps = case.get("steps", case.get("custom_steps_separated", []))
                for step in steps:
                    if isinstance(step, dict):
                        formatted_case["custom_steps_separated"].append(
                            {
                                "content": step.get("step", step.get("content", "")),
                                "expected": step.get("expected", ""),
                            }
                        )

            # Remove duplicate detection fields if present
            for field in [
                "similarity_score",
                "similarity_reasons",
                "similar_to_existing_id",
            ]:
                formatted_case.pop(field, None)

            formatted_cases.append(formatted_case)

        return formatted_cases

    def _get_testrail_type_id(self, test_type: str) -> int:
        """Get TestRail type ID for test type"""
        type_mapping = {
            "positive": 1,  # Functional
            "negative": 1,  # Functional
            "edge": 1,  # Functional
            "accessibility": 2,  # Accessibility
        }
        return type_mapping.get(test_type, 1)

    def _get_testrail_priority_id(self, priority: str) -> int:
        """Get TestRail priority ID for priority"""
        priority_mapping = {"High": 4, "Medium": 3, "Low": 2, "Critical": 5}
        return priority_mapping.get(priority, 3)


class TestCaseSaver:
    """Saves test cases to TestRail"""

    __test__ = False  # Prevent pytest from collecting this as a test

    def __init__(self):

        self.testrail_api = TestRailAPI()
        self.output_formatter = OutputFormatter()

        # Get configuration from configs/config.py
        self.project_id = PROJECT_ID
        self.suite_id = SUITE_ID
        self.default_section_id = TARGET_SECTION_ID

    def load_test_cases_from_json(self, json_file: str) -> List[Dict]:
        """Load test cases from JSON file"""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "test_cases" in data:
                    return data["test_cases"]
                else:
                    print(f"Unexpected JSON structure in {json_file}")
                    return []

        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            print(f"Error loading test cases from {json_file}: {str(e)}")
            return []

    def save_to_testrail(
        self, test_cases: List[Dict], section_id: Optional[int] = None
    ) -> List[Dict]:
        """Save test cases to TestRail"""
        if not test_cases:
            print("No test cases to save to TestRail")
            return []

        # Format test cases for TestRail
        formatted_cases = self.output_formatter.format_for_testrail(test_cases)

        # Use default section if not specified
        if section_id is None:
            section_id = self.default_section_id

            # If default section is not available, get the first available section
            if section_id == 1:  # Default value, try to get actual sections
                sections = self.testrail_api.get_sections(
                    self.project_id, self.suite_id
                )
                if not sections:
                    print("Error: No sections found in TestRail project")
                    return []
                section_id = sections[0]["id"]

        saved_cases = []
        for case_data in formatted_cases:
            try:
                result = self.testrail_api.add_case(section_id, case_data)
                saved_cases.append(result)
                print(f"Saved test case: {result.get('title', 'Untitled')}")
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Error saving test case: {str(e)}")

        print(f"Successfully saved {len(saved_cases)} test cases to TestRail")
        return saved_cases

    def save_all_from_target(self):
        """Save all test cases from target folder to TestRail"""
        print("=== Test Case Saver ===")
        print("Loading test cases from target folder...")

        target_dir = "target"
        if not os.path.exists(target_dir):
            print(f"Target directory '{target_dir}' not found")
            return

        all_test_cases = []

        # Find all JSON files in target directory
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)

            if filename == "generated_test_cases.json":
                print(f"Loading test cases from {filename}...")
                test_cases = self.load_test_cases_from_json(file_path)
                all_test_cases.extend(test_cases)
                print(f"Loaded {len(test_cases)} test cases from {filename}")

        if not all_test_cases:
            print("No test cases found in target folder")
            return

        print(f"\nTotal test cases to save: {len(all_test_cases)}")

        # Save to TestRail
        print("\nSaving test cases to TestRail...")
        saved_cases = self.save_to_testrail(all_test_cases)

        print("\n=== Summary ===")
        print(f"Total test cases processed: {len(all_test_cases)}")
        print(f"Successfully saved to TestRail: {len(saved_cases)}")


def main():
    """Main entry point"""
    try:
        saver = TestCaseSaver()
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

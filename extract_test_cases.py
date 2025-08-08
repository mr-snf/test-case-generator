"""
Script to extract all test cases from TestRail and save them to knowledgebase folder.
"""

import os
import sys
from typing import Dict, List

from configs.config import (
    PROJECT_ID,
    TESTRAIL_URL,
)
from src.testrail import TestRailAPI


def extract_test_cases():
    """Extract all test cases from TestRail and save to JSON file"""

    # Use configuration from configs/config.py
    project_id = PROJECT_ID
    output_file = "knowledgebase/existing_test_cases.json"

    # Ensure knowledgebase directory exists
    os.makedirs("knowledgebase", exist_ok=True)

    print(f"=== TestRail Test Case Extractor ===")
    print(f"TestRail URL: {TESTRAIL_URL}")
    print(f"Project ID: {project_id}")
    print(f"Output file: {output_file}")

    try:
        # Initialize TestRail API
        testrail_api = TestRailAPI()

        # Test connection
        print("Testing TestRail connection...")
        projects_response = testrail_api.get_projects()
        print(f"Connected successfully. Found {len(projects_response)} projects.")

        # Handle different response formats
        if isinstance(projects_response, dict):
            # If it's a dictionary, it might contain projects in a specific key
            if "projects" in projects_response:
                projects = projects_response["projects"]
            elif "data" in projects_response:
                projects = projects_response["data"]
            else:
                # If it's a dict but no obvious key, treat it as a single project
                projects = [projects_response]
        elif isinstance(projects_response, list):
            projects = projects_response
        else:
            print(f"Unexpected response type: {type(projects_response)}")
            print(f"Response content: {projects_response}")
            return

        # Get project info
        project_info = None
        for project in projects:
            if isinstance(project, dict) and project.get("id") == project_id:
                project_info = project
                break
            elif isinstance(project, str):
                print(f"Warning: Project is a string: {project}")
                continue

        if not project_info:
            print(f"Project with ID {project_id} not found.")
            print("Available projects:")
            for project in projects:
                if isinstance(project, dict):
                    print(f"  - ID: {project.get('id')}, Name: {project.get('name')}")
                else:
                    print(f"  - Invalid project format: {project}")
            return

        print(f"Extracting test cases from project: {project_info['name']}")

        # Extract test cases
        test_cases = testrail_api.export_test_cases_to_json(project_id, output_file)

        if test_cases:
            print(f"Successfully extracted {len(test_cases)} test cases")

            # Create summary
            summary = create_extraction_summary(test_cases)
            print("\n" + summary)

            # Save summary to file
            summary_file = os.path.join("knowledgebase", "extraction_summary.txt")
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"Summary saved to: {summary_file}")

        else:
            print("No test cases found in the project")

    except Exception as e:
        print(f"Error extracting test cases: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def create_extraction_summary(test_cases: List[Dict]) -> str:
    """Create a summary of extracted test cases"""
    if not test_cases:
        return "No test cases extracted."

    # Count by priority
    priority_counts: Dict[int, int] = {}
    type_counts: Dict[int, int] = {}
    section_counts: Dict[int, int] = {}

    for case in test_cases:
        # Handle different case formats
        if isinstance(case, str):
            print(f"Warning: Test case is a string: {case}")
            continue
        elif not isinstance(case, dict):
            print(f"Warning: Test case is not a dict: {type(case)} - {case}")
            continue

        # Priority
        priority = case.get("priority_id", "Unknown")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Type
        case_type = case.get("type_id", "Unknown")
        type_counts[case_type] = type_counts.get(case_type, 0) + 1

        # Section
        section_id = case.get("section_id", "Unknown")
        section_counts[section_id] = section_counts.get(section_id, 0) + 1

    summary = f"""
Test Case Extraction Summary
============================

Total Test Cases: {len(test_cases)}

Breakdown by Priority:
"""

    priority_names = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
    for priority_id, count in priority_counts.items():
        priority_name = priority_names.get(priority_id, f"Unknown ({priority_id})")
        summary += f"  - {priority_name}: {count}\n"

    summary += "\nBreakdown by Type:\n"
    type_names = {1: "Functional", 2: "Accessibility", 3: "Performance", 4: "Usability"}
    for type_id, count in type_counts.items():
        type_name = type_names.get(type_id, f"Unknown ({type_id})")
        summary += f"  - {type_name}: {count}\n"

    summary += f"\nBreakdown by Section:\n"
    for section_id, count in section_counts.items():
        summary += f"  - Section {section_id}: {count}\n"

    return summary


def main():
    """Main entry point"""
    extract_test_cases()


if __name__ == "__main__":
    main()

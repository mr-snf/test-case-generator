"""
Shared pytest fixtures and configuration for test suite.
"""

import os

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture for test data directory"""
    return os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture(scope="session")
def sample_test_cases():
    """Shared fixture for sample test cases"""
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
                {
                    "content": "Enter valid password",
                    "expected": "Password field accepts input",
                },
                {
                    "content": "Click Login button",
                    "expected": "User is redirected to dashboard",
                },
            ],
            "custom_test_data": "test@example.com / password123",
        },
        {
            "id": 2,
            "title": "User Login with Invalid Email Format",
            "type": "negative",
            "priority": "Medium",
            "section_id": 1,
            "custom_preconds": "User is on login page",
            "custom_steps_separated": [
                {
                    "content": "Enter invalid email format (e.g., 'invalid-email')",
                    "expected": "Email validation error is displayed",
                },
                {
                    "content": "Enter valid password",
                    "expected": "Password field accepts input",
                },
                {
                    "content": "Click Login button",
                    "expected": "Form submission is prevented",
                },
            ],
            "custom_test_data": "invalid-email / password123",
        },
    ]


@pytest.fixture(scope="session")
def sample_feature_content():
    """Shared fixture for sample feature content"""
    return """
# User Login Feature

## Overview
The user login feature allows registered users to authenticate and access their account dashboard.

## Functional Requirements

### Core Functionality
- Users can log in using their email address and password
- The system validates credentials against the user database
- Successful login redirects users to their dashboard
- Failed login attempts show appropriate error messages

### Input Validation
- Email field must be a valid email format
- Password field must not be empty
- Both fields are required for submission

### Security Requirements
- Passwords are encrypted and never stored in plain text
- Failed login attempts are logged for security monitoring
- Account lockout after 5 consecutive failed attempts
- Session timeout after 30 minutes of inactivity

### User Experience
- Clear error messages for invalid inputs
- Loading indicator during authentication
- Remember me functionality for convenience
- Password reset option for forgotten passwords

## Technical Specifications

### API Endpoints
- POST /api/auth/login - Main login endpoint
- GET /api/auth/logout - Logout endpoint
- POST /api/auth/forgot-password - Password reset request

### Database Tables
- users (id, email, password_hash, created_at, last_login)
- login_attempts (id, user_id, ip_address, timestamp, success)
- sessions (id, user_id, token, expires_at)

### Response Codes
- 200: Successful login
- 400: Invalid input data
- 401: Invalid credentials
- 429: Too many failed attempts
- 500: Server error

## Accessibility Requirements
- All form elements must have proper labels
- Error messages must be announced to screen readers
- Keyboard navigation must be fully functional
- Color contrast must meet WCAG AA standards
- Focus indicators must be clearly visible

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Requirements
- Login response time must be under 2 seconds
- Page load time must be under 3 seconds
- Must handle concurrent login attempts efficiently
"""


@pytest.fixture(scope="session")
def mock_api_responses():
    """Shared fixture for mock API responses"""
    return {
        "projects": [
            {"id": 1, "name": "Test Project 1"},
            {"id": 2, "name": "Test Project 2"},
        ],
        "suites": [
            {"id": 1, "name": "Test Suite 1"},
            {"id": 2, "name": "Test Suite 2"},
        ],
        "sections": [
            {"id": 1, "name": "Test Section 1"},
            {"id": 2, "name": "Test Section 2"},
        ],
        "cases": [{"id": 1, "title": "Test Case 1"}, {"id": 2, "title": "Test Case 2"}],
        "fields": [
            {"id": 1, "name": "custom_field_1"},
            {"id": 2, "name": "custom_field_2"},
        ],
        "priorities": [
            {"id": 1, "name": "Low"},
            {"id": 2, "name": "Medium"},
            {"id": 3, "name": "High"},
        ],
        "types": [{"id": 1, "name": "Functional"}, {"id": 2, "name": "Accessibility"}],
    }


@pytest.fixture(scope="session")
def sample_test_cases_varied_templates():
    """Sample cases covering multiple TestRail templates and field styles."""
    return [
        # Step-based template (template_id 2)
        {
            "id": 101,
            "template_id": 2,
            "title": "Checkout: Successful purchase",
            "type_id": 16,
            "priority_id": 3,
            "refs": "ECOM-1001",
            "estimate": "10min",
            "custom_preconds": '{"cart": {"items": 3}}',
            "custom_steps_separated": [
                {"content": "Go to cart", "expected": "Cart page visible"},
                {"content": "Click checkout", "expected": "Checkout page visible"},
            ],
            "labels": ["checkout", "e2e"],
            "custom_automation_type": 1,
            "custom_platforms": 2,
        },
        # Text-based (exploratory) template using custom_steps/custom_expected
        {
            "id": 102,
            "template_id": 3,
            "title": "Exploratory: Profile settings",
            "type_id": 25,
            "priority_id": 2,
            "refs": "USR-2002",
            "estimate": "15min",
            "custom_preconds": "User logged in",
            "custom_steps": "Explore profile tabs and toggles",
            "custom_expected": "No errors, settings are persisted",
            "custom_mission": "Discover usability issues",
            "custom_goals": "Coverage of core profile actions",
            "custom_levels": 1,
        },
        # BDD/Scenario template with scenario text field
        {
            "id": 103,
            "template_id": 7,
            "title": "BDD: Password reset",
            "type_id": 9,
            "priority_id": 1,
            "refs": "AUTH-3003",
            "estimate": "5min",
            "custom_testrail_bdd_scenario": "Given a user, When password reset requested, Then email sent",
            "labels": ["bdd"],
            "custom_operatingsystem": 4,
            "custom_testtype": ["smoke", "regression"],
        },
    ]

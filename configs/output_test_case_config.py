# Test Case Generation Settings
# =======================================================

# Default number of test cases to generate
DEFAULT_TEST_CASES_COUNT = 20

# Default test types to generate (comma-separated)
# Options: positive, negative, edge, accessibility
DEFAULT_TEST_TYPES = ["positive", "negative", "edge"]

# WCAG Accessibility Guideline
WCAG_GUIDLINE = None

# Default priority distribution (percentage)
# Format: High:30, Medium:50, Low:20
DEFAULT_PRIORITY_DISTRIBUTION = {"High": 40, "Medium": 40, "Low": 20}

# Similarity threshold for duplicate test cases
SIMILARITY_THRESHOLD = 0.85

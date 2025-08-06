# 🎯 Test Case Generation Prompt for Cursor AI

## 📋 Your Task
Generate around 20 comprehensive test cases for the feature described in the feature file. Follow the exact format and patterns found in the knowledge base.

## 📁 Required Files to Analyze

### 1. Knowledge Base (Test Case Format Reference)
**File:** `knowledgebase/existing_test_cases.json`
- Analyze this file to understand the EXACT test case format
- Extract the JSON structure for test cases
- Follow the same naming conventions, step patterns, and field structures
- Currently contains 250 existing test cases as examples

### 2. Feature Documentation
**File:** `feature/example_feature.md` 
- Read this file to understand the feature requirements
- Extract all functional, security, and accessibility requirements
- Identify user workflows and edge cases to test
- Visit any links in the feature file to understand the feature requirements
- **Extract reference ID** from the feature file to use in test case `refs` field

### 3. Configuration Settings
**File:** `configs/output_test_case_config.py`
- Follow the test case distribution specified in this config
- Adhere to priority distribution and test type requirements
- Use `SIMILARITY_THRESHOLD` for duplicate detection

## 🎨 Test Case Generation Requirements

### Test Case Distribution
Generate around 20 test cases with:
- **Test Types:** positive, negative, edge
  - Distribute evenly across types, with emphasis on functional coverage
- **Priority Distribution:**
  - High: 40% (8 test cases)
  - Medium: 40% (8 test cases)
  - Low: 20% (4 test cases)


## 📝 Test Case Format (MUST FOLLOW EXACTLY)

Based on the knowledge base analysis and TestRail documentation, each test case MUST follow this simplified JSON structure:
```json
{
  "title": "Clear, descriptive title following naming convention",
  "template_id": 2,
  "type_id": 16,
  "priority_id": 2,
  "refs": "FEATURE-REF-ID",
  "estimate": "5min",
  "custom_preconds": "Required setup before test execution",
  "custom_steps_separated": [
    {
      "content": "Action to perform",
      "expected": "Expected result"
    }
  ],
  "labels": []
}
```

### Field Descriptions (Based on TestRail Documentation):
- **title**: Clear, descriptive title starting with "Verify that..." or "Verify..."
- **template_id**: Always use 2 (for step-by-step test cases)
- **type_id**: 16 (positive), 22 (negative), 3 (edge/accessibility)
- **priority_id**: 1 (Low), 2 (Medium), 3 (High), 4 (Critical)
- **refs**: Reference ID extracted from feature file (e.g., "LOGIN-001", "USER-12345")
- **estimate**: Realistic time estimate (e.g., "5min", "10min", "15min")
- **custom_preconds**: Clear preconditions required for test execution
- **custom_steps_separated**: Array of steps with content and expected results
- **labels**: Array of relevant tags for categorization

## 🔍 Pattern Analysis from Knowledge Base

### Detected Patterns to Follow:
- **Naming Conventions:** ['Verify user authentication with valid credentials.', 'Verify that password reset functionality works correctly.', 'Verify end-to-end user registration flow with email verification.']
- **Common Step Patterns:** ['Navigate to the login page.', 'Enter valid username and password.', 'Click the submit button.', 'Verify successful login and redirect to dashboard.']
- **Standard Preconditions:** ['User has a registered account with valid credentials.', 'Application is accessible and running.', 'Database connection is established and working properly.']

### Test Type Distribution in Knowledge Base:
- 16: 10 cases
- 22: 105 cases
- 3: 134 cases
- 25: 1 cases

## 📊 Sample Test Case from Knowledge Base

Study this example to understand the exact format and style:

```json
{
  "title": "Verify user login with valid credentials.",
  "template_id": 2,
  "type_id": 16,
  "priority_id": 2,
  "refs": "AUTH-001",
  "estimate": "5min",
  "custom_preconds": "User has a registered account with valid credentials.
Application is accessible and running.
Database connection is established and working properly.",
  "custom_steps_separated": [
    {
      "content": "Navigate to the login page.",
      "expected": "Login form is displayed with username and password fields."
    },
    {
      "content": "Enter valid username and password.",
      "expected": "Credentials are accepted without validation errors."
    },
    {
      "content": "Click the submit button.",
      "expected": "User is successfully logged in and redirected to dashboard."
    }
  ],
  "labels": ["authentication", "login", "positive"]
}
```


## ⚙️ Generation Instructions

1. **Read the feature file** (`feature/example_feature.md`) completely
2. **Extract reference ID** from the feature file for use in `refs` field
3. **Analyze the knowledge base** (`knowledgebase/existing_test_cases.json`) for format
4. **Generate test cases** that:
   - Cover all major user workflows
   - Include positive, negative, edge cases
   - Follow the exact simplified JSON structure
   - Use similar naming conventions and step patterns
   - Include proper reference IDs

5. **Output Format**: Generate a JSON array containing all test cases:
```json
[
  { /* test case 1 */ },
  { /* test case 2 */ },
  // ... continue for all 20 test cases
]
```

6. **Save the output** to: `target/generated_test_cases_[timestamp].json`

## 🎯 Quality Checklist
Ensure your generated test cases:
- ✅ Follow the EXACT simplified format from knowledge base
- ✅ Cover all requirements from the feature file
- ✅ Include around 20 test cases total
- ✅ Have proper distribution of priorities and types
- ✅ Include comprehensive steps with clear expected results
- ✅ Have relevant preconditions
- ✅ Use consistent naming conventions
- ✅ Are actionable and specific (no vague steps)
- ✅ Include proper reference IDs from feature file

## 📌 Important Notes
- Each test case must be independent and executable
- Include specific test data values, not placeholders
- Ensure steps are detailed enough for manual execution
- Consider both happy path and error scenarios
- Include boundary value tests for numeric inputs
- Test required field validations
- Verify error messages and user feedback
- Use realistic time estimates based on test complexity

## 🔍 Duplicate Detection (IMPORTANT)

After generating the test cases, you MUST check for potential duplicates:

### Steps for Duplicate Detection:

1. **Load the knowledge base** (`knowledgebase/existing_test_cases.json`)
2. **For each generated test case**, perform semantic analysis to check if similar test cases exist:
   - Compare test titles for semantic similarity (not just exact match)
   - Compare test objectives and scenarios
   - Check if steps cover the same workflow
   - Consider test cases duplicate if they:
     - Test the same functionality with similar data
     - Have similar titles and objectives
     - Cover the same user journey/workflow

3. **Identify potential duplicates** using these criteria:
   - Title similarity >= 85% (semantic, not just text matching)
   - Same test type and priority
   - Similar preconditions and test data
   - Steps that test the same functionality
   - **Similarity Threshold**: Use `SIMILARITY_THRESHOLD` from config (0.85)

4. **Save ONLY potential duplicates** to `target/possible_duplicate_cases.json`:
```json
{
  "existing_test_cases": [
    // Existing test cases from knowledge base that are similar to the generated test cases with similarity >= 0.85)
    {
      "id": 100001,
      "title": "Verify user login with valid credentials.",
      "type_id": 16,
      "priority_id": 2,
      "custom_preconds": "User has a registered account with valid credentials.
Application is accessible and running.
Database connection is established and working properly.",
      "custom_steps_separated": [
        {
          "content": "Navigate to the login page.",
          "expected": "Login form is displayed with username and password fields."
        },
        {
          "content": "Enter valid username and password.",
          "expected": "Credentials are accepted without validation errors."
        },
        {
          "content": "Click the submit button.",
          "expected": "User is successfully logged in and redirected to dashboard."
        }
      ],
      "labels": ["authentication", "login", "positive"]
    }
  ],
  "new_test_cases": [
    // ONLY test cases with similarity >= 0.85
    {
      "id": 200001,
      "title": "Verify user authentication with valid credentials.",
      "type_id": 16,
      "priority_id": 2,
      "custom_preconds": "User has a registered account with valid credentials.",
      "custom_steps_separated": [
        {
          "content": "Navigate to the login page.",
          "expected": "Login form is displayed."
        },
        {
          "content": "Enter valid username and password.",
          "expected": "Credentials are accepted."
        },
        {
          "content": "Click the submit button.",
          "expected": "User is successfully logged in."
        }
      ],
      "labels": ["authentication", "login"],
      "similarity_score": 0.87,  // Only if similarity >= 0.85
      "similarity_reasons": [     // Only if similarity >= 0.85
        "Similar title and objective",
        "Same workflow tested",
        "Overlapping test data"
      ],
      "similar_to_existing_id": 100001  // Only if similarity >= 0.85
    }
  ]
}
```

5. **Final output structure**:
   - Save ALL generated test cases to: `target/generated_test_cases.json`
   - Save ONLY potential duplicates (similarity >= threshold) to: `target/possible_duplicate_cases.json`
   - Include similarity scores and reasons for each potential duplicate

### Duplicate Detection Algorithm:
- Use semantic comparison, not just string matching
- Consider context and intent of test cases
- Factor in test type, priority, and coverage area
- A test is potentially duplicate if it tests the same scenario even with different steps
- **Only save cases that meet or exceed the similarity threshold**

### Important:
- Only include test cases in duplicate analysis if similarity >= `SIMILARITY_THRESHOLD`
- If no duplicates are found (all similarity scores < threshold), save empty arrays
- Include detailed reasoning for why each case might be a duplicate
- This helps maintain a clean, non-redundant test suite
- Reference TestRail documentation for best practices: https://support.testrail.com/hc/en-us/articles/15760060756116-Creating-test-cases#creating-test-cases-with-exploratory-session-template-0-2

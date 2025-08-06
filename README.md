# Test Case Generator

A comprehensive test case generation system that creates high-quality test cases for software features in TestRail-compatible format. This tool analyzes existing test cases, extracts feature requirements, and generates comprehensive test coverage including positive, negative, edge cases, and accessibility scenarios.

## 🚀 Features

- 🤖 **AI-Powered Generation**: Uses advanced prompt engineering for intelligent test case generation
- 📊 **TestRail Integration**: Direct integration with TestRail API for seamless test case management
- 🔍 **Duplicate Detection**: Prevents duplicate test cases using semantic similarity analysis
- 📁 **Multiple Output Formats**: Export test cases in JSON format compatible with TestRail
- ⚙️ **Configurable**: Customize test case types, counts, and priorities
- 🎯 **Comprehensive Coverage**: Generates positive, negative, edge, and accessibility test cases
- 📋 **Pattern Analysis**: Analyzes existing test cases to maintain consistency
- 🔗 **Reference ID Extraction**: Automatically extracts reference IDs from feature files

## 📁 Project Structure

```
Test-case-generator/
├── configs/
│   ├── config.py                    # TestRail API configuration
│   └── output_test_case_config.py  # Test case generation settings
├── feature/
│   └── example_feature.md          # Example feature description
├── knowledgebase/
│   └── existing_test_cases.json    # Existing test cases from TestRail
├── prompts/
│   ├── test_case_generator.md      # Generated prompt for test case creation
│   └── README.md                   # Prompt system documentation
├── src/
│   ├── testrail_api.py             # TestRail API client
│   └── testrail_client.py          # TestRail HTTP client
├── target/                         # Generated test case outputs
├── tests/                          # Comprehensive test suite
├── extract_test_cases.py           # TestRail extraction script
├── generate_prompt.py              # Prompt generation orchestrator
├── save_test_cases.py              # TestRail saving utilities
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
├── env.example                     # Environment variables template
├── LICENSE                         # MIT License file
└── README.md                       # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Test-case-generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your TestRail configuration:
   ```env
   # TestRail API Configuration
   TESTRAIL_URL=https://your-domain.testrail.io
   TESTRAIL_USERNAME=your-email@domain.com
   TESTRAIL_PASSWORD=your-api-key-or-password
   
   # TestRail Project Configuration
   TESTRAIL_PROJECT_ID=1
   TESTRAIL_SUITE_ID=1
   TARGET_SECTION_ID=101
   ```

## 🚀 Usage

### 1. Extract Existing Test Cases

First, extract existing test cases from TestRail to build your knowledge base:

```bash
python extract_test_cases.py
```

This will:
- Connect to your TestRail instance
- Extract all test cases from the configured project
- Save them to `knowledgebase/existing_test_cases.json`
- Generate a summary report

### 2. Prepare Feature Description

Create a feature description file in the `feature/` directory. See `feature/example_feature.md` for an example.

### 3. Generate Prompt for Test Case Creation

Run the prompt generation orchestrator:

```bash
python generate_prompt.py
```

This will:
- Load existing test cases from `knowledgebase/`
- Analyze patterns and structure
- Read feature files from `feature/`
- Extract requirements and reference IDs
- Read configuration from `configs/output_test_case_config.py`
- Generate a comprehensive prompt in `prompts/test_case_generator.md`

### 4. Use the Generated Prompt

The generated prompt in `prompts/test_case_generator.md` contains:
- **Pattern Analysis**: Understanding of existing test case structure
- **Feature Requirements**: Extracted requirements from feature files
- **Configuration**: Test case count, types, and priority distribution
- **Instructions**: Step-by-step guidance for generating test cases
- **Quality Checks**: Validation criteria for generated test cases

### 5. Save Test Cases to TestRail (Optional)

Use the save utility to upload generated test cases to TestRail:

```bash
python save_test_cases.py
```

This will:
- Load test cases from `target/generated_test_cases.json`
- Format them for TestRail
- Upload to your TestRail project

## ⚙️ Configuration

### Test Case Generation Settings

Edit `configs/output_test_case_config.py` to customize:

```python
# Number of test cases to generate
DEFAULT_TEST_CASES_COUNT = 20

# Test types to generate
DEFAULT_TEST_TYPES = ["positive", "negative", "edge"]

# Priority distribution
DEFAULT_PRIORITY_DISTRIBUTION = {
    "High": 40,
    "Medium": 40, 
    "Low": 20
}

# Similarity threshold for duplicate detection
SIMILARITY_THRESHOLD = 0.85
```

### TestRail Configuration

Edit `configs/config.py` to configure TestRail connection:

```python
# TestRail API settings
API_BASE_URL = "https://your-domain.testrail.io"
USERNAME = "your-email@domain.com"
PASSWORD = "your-api-key"
PROJECT_ID = 1
SUITE_ID = 1
```

## 📊 Output Formats

### JSON Format (TestRail Compatible)

Generated test cases follow the TestRail API format:

```json
{
  "title": "User Login with Valid Credentials",
  "template_id": 2,
  "type_id": 16,
  "priority_id": 2,
  "refs": "LOGIN-001",
  "estimate": "5min",
  "custom_preconds": "User has a registered account",
  "custom_steps_separated": [
    {
      "content": "Navigate to login page",
      "expected": "Login form is displayed"
    },
    {
      "content": "Enter valid email and password",
      "expected": "Credentials are accepted"
    }
  ],
  "labels": ["login", "authentication"]
}
```

## 🎯 Test Case Types

The system generates comprehensive test coverage:

### Positive Tests
- Valid user inputs and workflows
- Successful system responses
- Happy path scenarios
- Expected functionality verification

### Negative Tests
- Invalid inputs and error conditions
- Exception handling verification
- Security vulnerability testing
- Graceful failure mode validation

### Edge Tests
- Boundary condition testing
- Performance limit validation
- Data limit verification
- Concurrent operation testing

### Accessibility Tests (Optional)
- WCAG compliance verification
- Screen reader compatibility
- Keyboard navigation testing
- Color contrast validation
- Focus management testing

## 🔍 Duplicate Detection

The system includes intelligent duplicate detection:

- **Semantic Analysis**: Compares test case content and intent
- **Similarity Scoring**: Uses configurable threshold (default: 0.85)
- **Reference ID Tracking**: Extracts and uses reference IDs from feature files
- **Quality Filtering**: Only saves potential duplicates that meet similarity criteria

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_extract_test_cases.py -v
python -m pytest tests/test_generate_prompt_integration.py -v
python -m pytest tests/test_test_case_generator.py -v
```

The test suite includes:
- **174 tests** covering all functionality
- **Unit tests** for individual components
- **Integration tests** for workflow validation
- **Error handling** and edge case coverage

## 🔧 Troubleshooting

### Common Issues

1. **TestRail Connection Failed**
   - Verify your TestRail URL, username, and password in `.env`
   - Check if your TestRail instance allows API access
   - Ensure your account has appropriate permissions

2. **No Test Cases Generated**
   - Ensure `knowledgebase/existing_test_cases.json` exists
   - Check that feature files are in the `feature/` directory
   - Verify configuration in `configs/output_test_case_config.py`

3. **Prompt Generation Errors**
   - Check that all required directories exist
   - Verify file permissions and access
   - Review console output for specific error messages

4. **Duplicate Detection Issues**
   - Adjust `SIMILARITY_THRESHOLD` in configuration
   - Review similarity analysis results
   - Check reference ID extraction from feature files

### Debug Mode

Enable debug output by setting the `DEBUG` environment variable:

```bash
export DEBUG=1
python generate_prompt.py
```

## 📈 Quality Assurance

The system includes comprehensive quality checks:

- ✅ **Format Validation**: Ensures TestRail compatibility
- ✅ **Coverage Analysis**: Validates requirement coverage
- ✅ **Pattern Consistency**: Maintains established test case patterns
- ✅ **Duplicate Prevention**: Identifies and filters similar test cases
- ✅ **Reference Tracking**: Extracts and uses reference IDs
- ✅ **Configuration Validation**: Ensures proper settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### License Summary
The MIT License is a permissive open-source license that allows you to:
- ✅ Use the software for any purpose
- ✅ Modify the software
- ✅ Distribute the software
- ✅ Use it commercially
- ✅ Use it privately
- ✅ Sublicense it

The only requirement is that the original license and copyright notice must be included in all copies or substantial portions of the software.

### Copyright
Copyright (c) 2024 Test Case Generator

For more information about the MIT License, visit: https://opensource.org/licenses/MIT

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration documentation
- Run the test suite to verify functionality


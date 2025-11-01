# Test Development Script Guide

This guide explains how to use `scripts/test-development.py`, a development workflow automation script for running different types of tests and validations during development.

## Overview

The test development script provides automated workflows for:
- Fast development testing cycles
- Comprehensive test suite execution
- Enhanced fixture validation
- Performance analysis
- Fixture usage reporting

## Installation and Setup

The script is ready to use with no additional dependencies beyond the project's existing test environment.

```bash
# Make the script executable (if needed)
chmod +x scripts/test-development.py

# Or run with Python
python scripts/test-development.py
```

## Available Workflows

### 1. Development Cycle (`dev`)

**Purpose**: Fast feedback loop during active development

```bash
python scripts/test-development.py dev
```

**What it runs**:
- Fast tests (unit + integration, excluding slow/container tests)
- Enhanced fixture validation tests
- Code quality checks (linting)

**Use when**:
- Making code changes during development
- Need quick feedback on changes
- Before committing code

**Example output**:
```
🚀 Starting Development Test Cycle
==================================================
🔄 Running fast tests (unit + integration)
   Command: pytest -m not slow and not container -v --tb=short
✅ Running fast tests (unit + integration) - Success
🔄 Validating enhanced fixture usage
   Command: pytest -m enhanced_fixtures and fast -v
✅ Validating enhanced fixture usage - Success
🔄 Running code quality checks
   Command: make lint
✅ Running code quality checks - Success
🎉 Development cycle completed successfully!
```

### 2. Comprehensive Suite (`comprehensive`)

**Purpose**: Full test coverage including slow and container tests

```bash
python scripts/test-development.py comprehensive
```

**What it runs**:
- Unit tests with coverage
- Integration tests with coverage
- Container tests with coverage
- Linting
- Type checking

**Use when**:
- Before pushing to main branch
- Preparing for release
- Validating major changes
- CI/CD pipeline validation

### 3. Enhanced Fixture Validation (`enhanced`)

**Purpose**: Validate enhanced fixture infrastructure

```bash
python scripts/test-development.py enhanced
```

**What it runs**:
- Enhanced fixture usage tests
- Data builder pattern validation
- Error simulation fixture tests
- Workflow service fixture validation

**Use when**:
- Working on test fixtures
- Validating test infrastructure changes
- Debugging fixture-related issues

### 4. Performance Analysis (`performance`)

**Purpose**: Analyze test and fixture performance

```bash
python scripts/test-development.py performance
```

**What it runs**:
- Performance benchmarks
- Fast test performance validation
- Enhanced fixture performance analysis

**Use when**:
- Optimizing test performance
- Investigating slow tests
- Validating fixture efficiency

### 5. Usage Report (`usage-report`)

**Purpose**: Generate fixture usage metrics

```bash
python scripts/test-development.py usage-report
```

**What it provides**:
- Fixture usage statistics
- Test metrics and insights
- Recommendations for verbose test runs

**Use when**:
- Analyzing test coverage
- Understanding fixture utilization
- Planning test improvements

## Test Markers and Categories

The script uses pytest markers to categorize tests:

### Core Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `container`: Container-based tests
- `slow`: Long-running tests
- `fast`: Quick tests for development

### Enhanced Fixture Markers
- `enhanced_fixtures`: Tests using enhanced fixture infrastructure
- `data_builders`: Tests validating data builder patterns
- `error_simulation`: Tests for error simulation fixtures
- `workflow_services`: Tests for workflow service fixtures
- `performance`: Performance benchmark tests

## Command Options and Flags

### Pytest Options Used
- `-v`: Verbose output
- `-vv`: Very verbose output
- `--tb=short`: Short traceback format
- `--tb=no`: No traceback (for performance tests)
- `--cov=src`: Coverage for source code
- `--cov-append`: Append coverage results
- `-q`/`--quiet`: Quiet output
- `--benchmark-only`: Run only benchmark tests

### Make Targets Used
- `make lint`: Code linting with flake8
- `make type-check`: Type checking with mypy

## Integration with Development Workflow

### Recommended Usage Patterns

**During Active Development**:
```bash
# Quick feedback loop
python scripts/test-development.py dev

# If tests pass, make changes and repeat
# If tests fail, fix issues and rerun
```

**Before Commits**:
```bash
# Run development cycle first
python scripts/test-development.py dev

# If working on fixtures, also run:
python scripts/test-development.py enhanced
```

**Before Push/PR**:
```bash
# Full validation
python scripts/test-development.py comprehensive
```

**Performance Optimization**:
```bash
# Analyze performance
python scripts/test-development.py performance

# Generate usage report
python scripts/test-development.py usage-report
```

### IDE Integration

The script can be integrated with IDEs:

**VS Code Tasks** (`.vscode/tasks.json`):
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Test Development Cycle",
            "type": "shell",
            "command": "python",
            "args": ["scripts/test-development.py", "dev"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

## Error Handling and Troubleshooting

### Common Issues

**Tests Fail to Run**:
- Ensure PDM environment is activated
- Check that all dependencies are installed: `make install-dev`
- Verify pytest configuration in `pyproject.toml`

**Performance Tests Timeout**:
- Container tests may take longer on slower systems
- Consider running `dev` workflow instead of `comprehensive` during development

**Coverage Issues**:
- Ensure source code is in `src/` directory
- Check `.coveragerc` configuration
- Verify test files are properly marked

### Exit Codes

- `0`: Success - all tests passed
- `1`: Failure - one or more tests failed or commands errored

### Debug Mode

For debugging test issues:
```bash
# Run with maximum verbosity
pytest -vv --tb=long -s

# Run specific marker with debug output
pytest -m enhanced_fixtures -vv --tb=long -s
```

## Customization

### Adding New Workflows

To add a new workflow, modify `scripts/test-development.py`:

1. Add new function following the pattern:
```python
def my_custom_workflow():
    """Description of custom workflow."""
    print("🔧 Starting Custom Workflow")
    print("="*50)
    
    commands = [
        (["pytest", "-m", "my_marker", "-v"], "Running custom tests"),
        # Add more commands as needed
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success
```

2. Add to workflows dictionary in `main()`:
```python
workflows = {
    # ... existing workflows
    "custom": my_custom_workflow,
}
```

3. Update argument parser choices:
```python
parser.add_argument("workflow", choices=[
    "dev", "comprehensive", "enhanced", "performance", "usage-report", "custom"
], help="Choose testing workflow")
```

### Environment Variables

The script respects environment variables that affect pytest:
- `PYTEST_ARGS`: Additional pytest arguments
- `COVERAGE_FILE`: Coverage data file location
- `PYTHONPATH`: Python module search path

## Best Practices

1. **Use `dev` workflow for active development** - provides fastest feedback
2. **Run `comprehensive` before important commits** - ensures full validation
3. **Use `enhanced` when working on test infrastructure** - validates fixture changes
4. **Monitor performance regularly** - catch performance regressions early
5. **Review usage reports periodically** - optimize test organization

## Related Documentation

- [Testing Guide](../testing/README.md): Complete testing documentation
- [CONTRIBUTING.md](../../CONTRIBUTING.md): Development workflow and standards
- [Makefile](../../Makefile): Available make targets for testing
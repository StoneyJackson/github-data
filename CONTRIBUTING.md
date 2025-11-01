# Contributing

Thank you for your interest in contributing to this project! We welcome contributions from everyone.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message
6. Create a pull request

## Developer Certificate of Origin (DCO)

This project requires all contributors to sign off on their commits using the [Developer Certificate of Origin (DCO)](https://developercertificate.org/). This certifies that you have the right to submit your contribution under the project's license.

### How to Sign Off

Add the `-s` flag when making commits:

```bash
git commit -s -m "feat: add new feature"
```

This adds a `Signed-off-by:` line to your commit message:

```
feat: add new feature

Signed-off-by: Your Name <your.email@example.com>
```

### What DCO Means

By signing off, you certify that:

1. The contribution was created in whole or in part by you and you have the right to submit it under the open source license indicated in the file
2. The contribution is based upon previous work that, to the best of your knowledge, is covered under an appropriate open source license and you have the right under that license to submit that work with modifications
3. The contribution was provided directly to you by some other person who certified (1), (2) or (3) and you have not modified it
4. You understand and agree that this project and the contribution are public and that a record of the contribution is maintained indefinitely

### Important Notes

- **All commits** in your pull request must be signed off
- You can sign off previous commits using: `git commit --amend -s`
- For multiple commits, you can rebase: `git rebase HEAD~n --signoff`
- Pull requests with unsigned commits will not be merged

## Development Process

### Setup

1. Fork and clone the repository
2. Follow setup instructions in the [README](README.md)
3. Create a new branch for your changes

### Making Changes

- Write clear, self-documenting code
- Add tests for new functionality
- Update documentation as needed
- Follow existing code style and conventions

### Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. All commit messages must be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Breaking Changes:**
Breaking changes should be indicated by adding `!` after the type/scope or by including `BREAKING CHANGE:` in the footer:

```
feat!: remove deprecated login method

BREAKING CHANGE: The legacy login() method has been removed. Use authenticateUser() instead.
```

**Examples:**
- `feat: add user authentication`
- `fix: resolve memory leak in data processing`
- `docs: update API documentation`
- `feat(auth): implement OAuth2 integration`
- `feat!: change API response format`
- `fix(api)!: remove support for legacy endpoints`

### Testing

This project uses comprehensive multi-layered testing with pytest. Run tests to ensure your changes don't break existing functionality:

```bash
make test-fast   # Fast feedback (recommended during development)
make test        # All tests including slower container tests
make check       # All quality checks (fast)
make check-all   # All quality checks including container tests
```

**For complete testing documentation, test categories, best practices, and detailed guidelines, see [docs/testing/README.md](docs/testing/README.md).**

For detailed information about GitHub API rate limiting implementation, see **[docs/rate-limiting.md](docs/rate-limiting.md)**.

## Development Setup and Workflow

This project uses PDM for package management and a comprehensive Makefile for development tasks.

### Quick Start

```bash
make install-dev  # Install all dependencies (including development tools)
make check        # Run all quality checks (recommended before committing)
```

### Essential Commands

```bash
make install-dev  # Setup development environment
make check        # Fast quality checks (format, lint, type-check, test-fast)
make check-all    # All quality checks including container integration tests
make test-fast    # Quick test feedback (excludes slow container tests)
make clean        # Remove build artifacts and caches
```

### Development Workflow

1. **Setup**: `make install-dev`
2. **Development**: Make your code changes
3. **Quality Check**: `make check` (fast feedback)
4. **Full Validation**: `make check-all` (before final commit)
5. **Commit**: Use signed-off commits with conventional format

All commands use PDM's virtual environment automatically - no manual activation needed.

### AI Development Tools

This project supports AI-assisted development. For Claude Code usage, session documentation, and AI development best practices, see **[docs/claude.md](docs/claude.md)**.

## Coding Standards

This project follows **Clean Code** principles as outlined in Robert C. Martin's "Clean Code: A Handbook of Agile Software Craftsmanship". All contributions are expected to adhere to these standards.

### Clean Code Principles

**Function Design:**
- **Single Responsibility**: Each function should do one thing and do it well
- **Step-Down Rule**: Functions should be organized from high-level abstractions to low-level details within each file
- **Small Functions**: Functions should be small (typically 10-20 lines)
- **Descriptive Names**: Use intention-revealing names that explain what the function does
- **Minimal Arguments**: Prefer functions with 0-3 parameters

**Naming Conventions:**
- Use clear, searchable, pronounceable names
- Avoid abbreviations and mental mapping
- Use verbs for functions (`get_user()`, `save_data()`)
- Use nouns for classes and variables (`Configuration`, `github_token`)
- Avoid misleading names and noise words

**Code Organization:**
- Follow the **Step-Down Rule**: Higher-level functions come before lower-level ones
- Dependencies should point downward in files
- Group related functionality together
- Keep files focused on a single concept

**Error Handling:**
- Use exceptions rather than return codes
- Don't return or pass `None` when possible
- Write error messages that help users understand what went wrong

**Testing:**
- Follow Test-Driven Development (TDD) when possible
- Write clean, readable tests that serve as documentation
- One assertion per test method
- Fast, Independent, Repeatable, Self-Validating, and Timely (FIRST) principles

### Python-Specific Guidelines

- Follow PEP 8 for code formatting (enforced by `black`)
- Use type hints for all function parameters and return values
- Prefer composition over inheritance
- Use `dataclasses` or `pydantic` models for data structures
- Private functions should be prefixed with `_`

### Code Quality Tools

All code must pass the following quality checks:

```bash
make format      # Format code with black
make lint        # Check with flake8
make type-check  # Verify types with mypy
make test        # Run test suite
make check       # Run all quality checks
```

### Examples

**Good:**
```python
def save_repository_issues(github_client: Github, repo_name: str, output_path: str) -> None:
    """Save all issues from a repository to a JSON file."""
    issues = _fetch_all_issues(github_client, repo_name)
    issue_data = _serialize_issues(issues)
    _write_json_file(output_path, issue_data)

def _fetch_all_issues(github_client: Github, repo_name: str) -> List[Issue]:
    """Fetch all issues from the specified repository."""
    # Implementation details...
```

**Bad:**
```python
def do_stuff(gc, rn, op):  # Unclear names, abbreviations
    """Do repository stuff."""  # Vague description
    # Mixed levels of abstraction
    issues = gc.get_repo(rn).get_issues()
    data = []
    for issue in issues:
        data.append({"title": issue.title, "body": issue.body})
    with open(op, 'w') as f:
        json.dump(data, f)  # Low-level details mixed with high-level logic
```

### Style Guide

- Follow the existing code style in the project
- Use meaningful variable and function names following Clean Code principles
- Follow the Conventional Commits standard for commit messages
- Keep changes focused and atomic
- Organize code following the Step-Down Rule

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
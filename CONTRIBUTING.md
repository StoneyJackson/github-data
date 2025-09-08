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

Run the test suite to ensure your changes don't break existing functionality:

```bash
# Add test commands here
```

## Style Guide

- Follow the existing code style in the project
- Use meaningful variable and function names
- Follow the Conventional Commits standard for commit messages
- Keep changes focused and atomic

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
# GitHub Data Project TODO

*Generated from Claude session summaries on 2025-09-08, updated 2025-09-14*

## Current Sprint (Immediate Priorities)

### Core Development Tasks
- [ ] Implement issue subissue relationship handling
- [ ] Implement data validation and sanitization for restore operations
- [ ] Add progress reporting for backup/restore operations

### Content Enhancement Features
- [ ] Add option to prevent user notifications by replacing @username with [AT]username in restored content
- [ ] Update internal issue links to use new issue numbers after restore (handle URL and shortcut syntax)
- [ ] Update internal links to wiki, releases, and other repository resources after restore
- [ ] Add option to break external issue links to prevent unwanted backlinks to restored repository

### Repository Management
- [ ] Add repository handling options: create if missing/fail if exists, create if missing/use if exists, or fail if missing

## Future Roadmap

### Extended Backup/Restore Features
- [ ] Save/restore project metadata and configuration
- [ ] Save/restore git repository
- [ ] Save/restore PRs
- [ ] Save/restore milestones
- [ ] Save/restore releases and tags
- [ ] Save/restore wiki pages
- [ ] Save/restore repository settings (description, homepage, topics, visibility)
- [ ] Save/restore branch protection rules

## Performance & Scalability

### API Performance Optimization
- [X] Consider GraphQL API for complex queries to reduce request count
- [X] Implement batch operations where possible to minimize API calls

## Documentation & Configuration
- [x] Create configuration documentation for GitHub token setup
- [ ] Document backup/restore file format specifications
- [ ] Add troubleshooting guide for common issues
- [ ] Create user guide with example workflows

## Quality Assurance
- [ ] Test DCO sign-off requirements in practice
- [ ] Eliminate DRY violations for error messages (main.py:86,95) and file operations

## Infrastructure & CI/CD
- [ ] Set up automated DCO enforcement (GitHub App installation)
- [ ] Configure branch protection rules requiring DCO checks
- [ ] Set up CI/CD pipeline for automated testing
- [ ] Create and push container images in CI/CD
- [ ] Automate release process in CI/CD
- [ ] Implement commit message linting (commitlint) for Conventional Commits

## Platform Integration
- [ ] Validate PR template functionality on GitHub
- [ ] Test GitLab MR template functionality
- [ ] Verify cross-platform compatibility

## Future Enhancements
- [ ] Consider automated versioning based on conventional commits
- [ ] Evaluate need for multiple GitLab MR templates
- [ ] Plan team onboarding documentation
- [ ] Design template iteration process based on user feedback

## Completed Features ✅

### Core GitHub API Implementation (2025-09-12)
✅ **Complete GitHub API client** - labels, issues, comments with full CRUD operations
✅ **Comment-to-issue relationship mapping** - proper restore with issue number mapping
✅ **Chronological comment ordering** - maintains conversation flow during restore
✅ **Pull request filtering** - excludes PRs from issue backup/restore operations
✅ **Original metadata preservation** - includes author, timestamps in restored content
✅ **Closed issue restoration** - captures and restores closure state and metadata

### Performance & Quality (2025-09-11/12)
✅ **GitHub API rate limiting** - exponential backoff, monitoring, configurable delays
✅ **Response caching system** - ETag-based conditional requests, SQLite backend
✅ **Cache architecture simplification** - streamlined from session-based to global approach
✅ **Clean Code refactoring** - Step-Down Rule, Single Responsibility Principle
✅ **Full type safety** - MyPy compliance across all 16 source files
✅ **Comprehensive testing** - 98 tests with 92% coverage including container integration

### Infrastructure & Tooling (2025-09-08/11)
✅ **Project foundation** - Python/PDM, Docker, DevContainer environment
✅ **Development tooling** - pytest, black, flake8, mypy, comprehensive Makefile
✅ **Testing framework** - multi-layered with unit/integration/container test markers
✅ **Quality compliance** - Conventional Commits, DCO, REUSE licensing
✅ **Documentation system** - comprehensive guides, session documentation workflow

## Development Notes
- **Environment**: DevContainer ready with all tools pre-configured
- **Workflow**: Use `make test-fast` for development, `make check-all` for full validation
- **Compliance**: All commits require `git commit -s` for DCO, follow Conventional Commits
- **Scope**: GitHub repository labels, issues, subissues, and comments only
- **Next milestone**: Issue subissue relationships and enhanced validation

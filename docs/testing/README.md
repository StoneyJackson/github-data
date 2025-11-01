# Testing Guide

## Quick Navigation

**New to the project?** Start here:
1. Read [Getting Started](getting-started.md) (15 min) - Commands and first test
2. Read [Writing Tests](writing-tests.md) (20 min) - Required patterns
3. Reference others as needed

**Daily Development?** → [Getting Started - Essential Commands](getting-started.md#essential-commands)

**Writing a test?** → [Writing Tests - Modern Pattern](writing-tests.md#required-test-pattern)

**Debugging?** → [Reference: Debugging](reference/debugging.md)

## Documentation Map

| File | Purpose | When to Read |
|------|---------|--------------|
| [Getting Started](getting-started.md) | Commands, quick reference, test categories | First day, daily use |
| [Writing Tests](writing-tests.md) | REQUIRED patterns, standards, examples | Before writing any test |
| [Test Infrastructure](test-infrastructure.md) | Fixtures, markers, configuration deep-dive | Understanding test architecture |
| [Specialized Testing](specialized-testing.md) | Container, error, performance testing | Working on advanced scenarios |
| [Debugging](reference/debugging.md) | Troubleshooting, common issues | When tests fail |
| [Migration Guide](reference/migration-guide.md) | Updating legacy test patterns | Modernizing old tests |
| [Best Practices](reference/best-practices.md) | Standards checklist, quality requirements | Code review, validation |

## Search This Documentation

Use your editor's project search across `docs/testing/` for keywords:
- **ConfigBuilder, ConfigFactory** → [Writing Tests](writing-tests.md)
- **MockBoundaryFactory** → [Writing Tests](writing-tests.md#boundary-mock-creation)
- **Fixtures** → [Test Infrastructure](test-infrastructure.md#shared-fixture-system)
- **Docker, Container** → [Specialized Testing](specialized-testing.md#container-integration-testing)
- **pytest markers** → [Test Infrastructure](test-infrastructure.md#test-categories-and-markers)
- **Debugging tests** → [Reference: Debugging](reference/debugging.md)
- **Error testing** → [Specialized Testing](specialized-testing.md#error-testing)

## Overview

The GitHub Data project employs a comprehensive testing strategy:
- **Unit Tests**: Fast, isolated tests for individual components (< 1s each)
- **Integration Tests**: Tests for component interactions and workflows (1-10s each)
- **Container Integration Tests**: Full Docker workflow validation (30s+ each)
- **Performance Tests**: Resource usage and timing validation

All tests use pytest with custom markers for organization and selective execution.

## Contributing to Test Documentation

When updating test documentation:
- Keep hub README synchronized with file changes
- Update cross-references when moving content
- Maintain file size targets (150-500 lines per file)
- Follow the progressive disclosure principle (basics → advanced)

---

**Testing Guide** | [Getting Started →](getting-started.md)

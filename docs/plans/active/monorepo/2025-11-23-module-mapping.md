# Monorepo Module Mapping

**Date:** 2025-11-23
**Purpose:** Detailed file-by-file mapping for monorepo conversion
**Related:** [Monorepo Conversion Design](2025-11-23-18-48-monorepo-conversion-design.md)

This document provides a comprehensive mapping of every file in the current codebase to its destination in the monorepo structure.

## Legend

- **[CORE]** = Moves to `packages/core/`
- **[GIT]** = Moves to `packages/git-repo-tools/`
- **[REPO-MGR]** = Moves to `packages/github-repo-manager/`
- **[DATA]** = Moves to `packages/github-data-tools/`
- **[ORCH]** = Moves to `packages/kit-orchestrator/`
- **[SPLIT]** = File needs to be split across multiple packages
- **[NzEW]** = New file to be created
- **[DELETE]** = File will be deleted/refactored away

---

## Source Code Mapping

### github_data/ (Root Package)

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/__init__.py` | DELETE | N/A | Root package no longer needed |
| `github_data/main.py` | SPLIT | Multiple | Split into orchestrator entry points |

**main.py Split Details:**
- Lines 1-95: Parameter loading → [CORE] `parameters/env_loader.py`
- Lines 109-211: Repository creation logic → [REPO-MGR] `operations/create.py`
- Lines 212-235: Service builders → Each package's `__init__.py`
- Lines 236-270: Orchestration → [ORCH] `orchestrator.py`

---

### github_data/config/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/config/__init__.py` | `packages/core/src/github_data_core/config/__init__.py` | CORE | |
| `github_data/config/number_parser.py` | `packages/core/src/github_data_core/config/number_parser.py` | CORE | Used for boolean parsing |

---

### github_data/entities/

**Base Framework (Core):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/entities/__init__.py` | `packages/core/src/github_data_core/entities/__init__.py` | CORE | Exports base classes only |
| `github_data/entities/base.py` | `packages/core/src/github_data_core/entities/base.py` | CORE | BaseEntity class |
| `github_data/entities/registry.py` | `packages/core/src/github_data_core/entities/registry.py` | CORE | Entity registry framework |
| `github_data/entities/strategy_context.py` | `packages/core/src/github_data_core/entities/strategy_context.py` | CORE | Strategy pattern support |

**Git Repository Entity (Git Package):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/entities/git_repositories/__init__.py` | `packages/git-repo-tools/src/git_repo_tools/entities/__init__.py` | GIT | |
| `github_data/entities/git_repositories/entity_config.py` | `packages/git-repo-tools/src/git_repo_tools/entities/entity_config.py` | GIT | |
| `github_data/entities/git_repositories/models.py` | `packages/git-repo-tools/src/git_repo_tools/entities/models.py` | GIT | |
| `github_data/entities/git_repositories/restore_strategy.py` | `packages/git-repo-tools/src/git_repo_tools/entities/restore_strategy.py` | GIT | |
| `github_data/entities/git_repositories/save_strategy.py` | `packages/git-repo-tools/src/git_repo_tools/entities/save_strategy.py` | GIT | |

**Repository Entity (Repo Manager - potentially):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/entities/repository/__init__.py` | `packages/github-repo-manager/src/github_repo_manager/entities/__init__.py` | REPO-MGR | Repository metadata model |
| `github_data/entities/repository/models.py` | `packages/github-repo-manager/src/github_repo_manager/entities/models.py` | REPO-MGR | |

**GitHub Data Entities (Data Tools):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/entities/comments/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/__init__.py` | DATA | |
| `github_data/entities/comments/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/converters.py` | DATA | |
| `github_data/entities/comments/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/entity_config.py` | DATA | |
| `github_data/entities/comments/models.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/models.py` | DATA | |
| `github_data/entities/comments/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/restore_strategy.py` | DATA | |
| `github_data/entities/comments/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/comments/save_strategy.py` | DATA | |
| `github_data/entities/issues/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/__init__.py` | DATA | |
| `github_data/entities/issues/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/converters.py` | DATA | |
| `github_data/entities/issues/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/entity_config.py` | DATA | |
| `github_data/entities/issues/models.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/models.py` | DATA | |
| `github_data/entities/issues/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/restore_strategy.py` | DATA | |
| `github_data/entities/issues/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/issues/save_strategy.py` | DATA | |
| `github_data/entities/labels/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/__init__.py` | DATA | |
| `github_data/entities/labels/conflict_strategies.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/conflict_strategies.py` | DATA | |
| `github_data/entities/labels/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/converters.py` | DATA | |
| `github_data/entities/labels/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/entity_config.py` | DATA | |
| `github_data/entities/labels/models.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/models.py` | DATA | |
| `github_data/entities/labels/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/restore_strategy.py` | DATA | |
| `github_data/entities/labels/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/labels/save_strategy.py` | DATA | |
| `github_data/entities/milestones/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/__init__.py` | DATA | |
| `github_data/entities/milestones/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/converters.py` | DATA | |
| `github_data/entities/milestones/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/entity_config.py` | DATA | |
| `github_data/entities/milestones/models.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/models.py` | DATA | |
| `github_data/entities/milestones/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/restore_strategy.py` | DATA | |
| `github_data/entities/milestones/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/milestones/save_strategy.py` | DATA | |
| `github_data/entities/pr_comments/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/__init__.py` | DATA | |
| `github_data/entities/pr_comments/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/converters.py` | DATA | |
| `github_data/entities/pr_comments/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/entity_config.py` | DATA | |
| `github_data/entities/pr_comments/models.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/models.py` | DATA | |
| `github_data/entities/pr_comments/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/restore_strategy.py` | DATA | |
| `github_data/entities/pr_comments/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_comments/save_strategy.py` | DATA | |
| `github_data/entities/pr_review_comments/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/__init__.py` | DATA | |
| `github_data/entities/pr_review_comments/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/converters.py` | DATA | |
| `github_data/entities/pr_review_comments/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/entity_config.py` | DATA | |
| `github_data/entities/pr_review_comments/models.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/models.py` | DATA | |
| `github_data/entities/pr_review_comments/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/restore_strategy.py` | DATA | |
| `github_data/entities/pr_review_comments/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_review_comments/save_strategy.py` | DATA | |
| `github_data/entities/pr_reviews/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/__init__.py` | DATA | |
| `github_data/entities/pr_reviews/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/converters.py` | DATA | |
| `github_data/entities/pr_reviews/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/entity_config.py` | DATA | |
| `github_data/entities/pr_reviews/models.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/models.py` | DATA | |
| `github_data/entities/pr_reviews/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/restore_strategy.py` | DATA | |
| `github_data/entities/pr_reviews/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pr_reviews/save_strategy.py` | DATA | |
| `github_data/entities/pull_requests/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/__init__.py` | DATA | |
| `github_data/entities/pull_requests/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/converters.py` | DATA | |
| `github_data/entities/pull_requests/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/entity_config.py` | DATA | |
| `github_data/entities/pull_requests/models.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/models.py` | DATA | |
| `github_data/entities/pull_requests/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/restore_strategy.py` | DATA | |
| `github_data/entities/pull_requests/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/pull_requests/save_strategy.py` | DATA | |
| `github_data/entities/releases/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/__init__.py` | DATA | |
| `github_data/entities/releases/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/converters.py` | DATA | |
| `github_data/entities/releases/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/entity_config.py` | DATA | |
| `github_data/entities/releases/models.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/models.py` | DATA | |
| `github_data/entities/releases/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/restore_strategy.py` | DATA | |
| `github_data/entities/releases/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/releases/save_strategy.py` | DATA | |
| `github_data/entities/sub_issues/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/__init__.py` | DATA | |
| `github_data/entities/sub_issues/converters.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/converters.py` | DATA | |
| `github_data/entities/sub_issues/entity_config.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/entity_config.py` | DATA | |
| `github_data/entities/sub_issues/models.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/models.py` | DATA | |
| `github_data/entities/sub_issues/restore_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/restore_strategy.py` | DATA | |
| `github_data/entities/sub_issues/save_strategy.py` | `packages/github-data-tools/src/github_data_tools/entities/sub_issues/save_strategy.py` | DATA | |
| `github_data/entities/users/__init__.py` | `packages/github-data-tools/src/github_data_tools/entities/users/__init__.py` | DATA | |
| `github_data/entities/users/models.py` | `packages/github-data-tools/src/github_data_tools/entities/users/models.py` | DATA | |

---

### github_data/git/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/git/__init__.py` | `packages/git-repo-tools/src/git_repo_tools/git/__init__.py` | GIT | |
| `github_data/git/command_executor.py` | `packages/git-repo-tools/src/git_repo_tools/git/command_executor.py` | GIT | |
| `github_data/git/protocols.py` | `packages/git-repo-tools/src/git_repo_tools/git/protocols.py` | GIT | |
| `github_data/git/service.py` | `packages/git-repo-tools/src/git_repo_tools/git/service.py` | GIT | |

---

### github_data/github/

**Core Infrastructure (Base REST client, rate limiting, retry):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/github/restapi_client.py` | `packages/core/src/github_data_core/github/restapi_client.py` | CORE | Base REST client (may need refactoring) |
| `github_data/github/rate_limiter.py` | `packages/core/src/github_data_core/github/rate_limiter.py` | CORE | Rate limiting logic |
| `github_data/github/cache.py` | `packages/core/src/github_data_core/github/cache.py` | CORE | Caching infrastructure |

**GitHub Data Tools (Full API, GraphQL, service layer):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/github/__init__.py` | SPLIT | Multiple | Factory split between packages |
| `github_data/github/boundary.py` | SPLIT | REPO-MGR + DATA | Narrow boundary for repo-mgr, full for data-tools |
| `github_data/github/common_converters_config.py` | `packages/github-data-tools/src/github_data_tools/github/common_converters_config.py` | DATA | |
| `github_data/github/converter_registry.py` | `packages/github-data-tools/src/github_data_tools/github/converter_registry.py` | DATA | |
| `github_data/github/converters.py` | `packages/github-data-tools/src/github_data_tools/github/converters.py` | DATA | |
| `github_data/github/graphql_client.py` | `packages/github-data-tools/src/github_data_tools/github/graphql_client.py` | DATA | GraphQL only needed by data-tools |
| `github_data/github/graphql_converters.py` | `packages/github-data-tools/src/github_data_tools/github/graphql_converters.py` | DATA | |
| `github_data/github/metadata.py` | `packages/github-data-tools/src/github_data_tools/github/metadata.py` | DATA | |
| `github_data/github/operation_registry.py` | `packages/github-data-tools/src/github_data_tools/github/operation_registry.py` | DATA | |
| `github_data/github/protocols.py` | SPLIT | Multiple | Base protocols in core, specific in packages |
| `github_data/github/service.py` | SPLIT | REPO-MGR + DATA | create_repository → repo-mgr, rest → data-tools |
| `github_data/github/sanitizers.py` | `packages/github-data-tools/src/github_data_tools/github/sanitizers.py` | DATA | |
| `github_data/github/utils/__init__.py` | `packages/github-data-tools/src/github_data_tools/github/utils/__init__.py` | DATA | |
| `github_data/github/utils/data_enrichment.py` | `packages/github-data-tools/src/github_data_tools/github/utils/data_enrichment.py` | DATA | |
| `github_data/github/utils/graphql_paginator.py` | `packages/github-data-tools/src/github_data_tools/github/utils/graphql_paginator.py` | DATA | |
| `github_data/github/queries/__init__.py` | `packages/github-data-tools/src/github_data_tools/github/queries/__init__.py` | DATA | |
| `github_data/github/queries/comments.py` | `packages/github-data-tools/src/github_data_tools/github/queries/comments.py` | DATA | |
| `github_data/github/queries/issues.py` | `packages/github-data-tools/src/github_data_tools/github/queries/issues.py` | DATA | |
| `github_data/github/queries/labels.py` | `packages/github-data-tools/src/github_data_tools/github/queries/labels.py` | DATA | |
| `github_data/github/queries/milestones.py` | `packages/github-data-tools/src/github_data_tools/github/queries/milestones.py` | DATA | |
| `github_data/github/queries/pr_reviews.py` | `packages/github-data-tools/src/github_data_tools/github/queries/pr_reviews.py` | DATA | |
| `github_data/github/queries/pull_requests.py` | `packages/github-data-tools/src/github_data_tools/github/queries/pull_requests.py` | DATA | |
| `github_data/github/queries/sub_issues.py` | `packages/github-data-tools/src/github_data_tools/github/queries/sub_issues.py` | DATA | |
| `github_data/github/queries/utility.py` | `packages/github-data-tools/src/github_data_tools/github/queries/utility.py` | DATA | |

---

### github_data/operations/

**Core Orchestration Framework:**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/operations/__init__.py` | `packages/core/src/github_data_core/operations/__init__.py` | CORE | Base orchestrator exports |
| `github_data/operations/orchestrator_base.py` | `packages/core/src/github_data_core/operations/orchestrator_base.py` | CORE | Base orchestrator class |
| `github_data/operations/strategy_factory.py` | `packages/core/src/github_data_core/operations/strategy_factory.py` | CORE | Strategy factory pattern |

**Save/Restore Operations (GitHub Data Tools):**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/operations/restore/__init__.py` | `packages/github-data-tools/src/github_data_tools/operations/restore/__init__.py` | DATA | |
| `github_data/operations/restore/orchestrator.py` | `packages/github-data-tools/src/github_data_tools/operations/restore/orchestrator.py` | DATA | |
| `github_data/operations/restore/strategy.py` | `packages/github-data-tools/src/github_data_tools/operations/restore/strategy.py` | DATA | |
| `github_data/operations/save/__init__.py` | `packages/github-data-tools/src/github_data_tools/operations/save/__init__.py` | DATA | |
| `github_data/operations/save/mixins/__init__.py` | `packages/github-data-tools/src/github_data_tools/operations/save/mixins/__init__.py` | DATA | |
| `github_data/operations/save/mixins/entity_coupling.py` | `packages/github-data-tools/src/github_data_tools/operations/save/mixins/entity_coupling.py` | DATA | |
| `github_data/operations/save/mixins/selective_filtering.py` | `packages/github-data-tools/src/github_data_tools/operations/save/mixins/selective_filtering.py` | DATA | |
| `github_data/operations/save/orchestrator.py` | `packages/github-data-tools/src/github_data_tools/operations/save/orchestrator.py` | DATA | |
| `github_data/operations/save/strategy.py` | `packages/github-data-tools/src/github_data_tools/operations/save/strategy.py` | DATA | |

---

### github_data/storage/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/storage/__init__.py` | `packages/core/src/github_data_core/storage/__init__.py` | CORE | |
| `github_data/storage/json_storage.py` | `packages/core/src/github_data_core/storage/json_storage.py` | CORE | |
| `github_data/storage/json_storage_service.py` | `packages/core/src/github_data_core/storage/json_storage_service.py` | CORE | |
| `github_data/storage/protocols.py` | `packages/core/src/github_data_core/storage/protocols.py` | CORE | |

---

### github_data/tools/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `github_data/tools/__init__.py` | `packages/github-data-tools/src/github_data_tools/tools/__init__.py` | DATA | Entity generation tool |
| `github_data/tools/generate_entity.py` | `packages/github-data-tools/src/github_data_tools/tools/generate_entity.py` | DATA | |
| `github_data/tools/templates/__init__.py` | `packages/github-data-tools/src/github_data_tools/tools/templates/__init__.py` | DATA | |

---

## Test Mapping

### tests/shared/

**Shared test infrastructure:**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/shared/builders/` | `packages/core/tests/shared/builders/` | CORE | Shared data builders |
| `tests/shared/fixtures/core/` | `packages/core/tests/shared/fixtures/` | CORE | Core fixtures |
| `tests/shared/fixtures/boundary_mocks/` | `packages/github-data-tools/tests/shared/fixtures/boundary_mocks/` | DATA | GitHub boundary mocks |
| `tests/shared/fixtures/enhanced/` | SPLIT | Multiple | Split based on what's being tested |
| `tests/shared/fixtures/error_simulation/` | `packages/core/tests/shared/fixtures/error_simulation/` | CORE | Error simulation framework |
| `tests/shared/fixtures/support/` | `packages/core/tests/shared/fixtures/support/` | CORE | Support utilities |
| `tests/shared/fixtures/test_data/` | SPLIT | Multiple | Split based on entity type |
| `tests/shared/fixtures/workflow_services/` | `packages/github-data-tools/tests/shared/fixtures/workflow_services/` | DATA | Workflow services |
| `tests/shared/mocks/` | SPLIT | Multiple | Split based on what's being mocked |

---

### tests/unit/

**Core Unit Tests:**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/unit/config/test_number_parser.py` | `packages/core/tests/unit/config/test_number_parser.py` | CORE | |
| `tests/unit/test_json_storage_unit.py` | `packages/core/tests/unit/storage/test_json_storage_unit.py` | CORE | |
| `tests/unit/operations/test_strategy_factory.py` | `packages/core/tests/unit/operations/test_strategy_factory.py` | CORE | |
| `tests/unit/operations/test_strategy_factory_registry.py` | `packages/core/tests/unit/operations/test_strategy_factory_registry.py` | CORE | |
| `tests/unit/operations/test_strategy_factory_validation.py` | `packages/core/tests/unit/operations/test_strategy_factory_validation.py` | CORE | |

**Git Unit Tests:**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/unit/entities/git_repositories/` | `packages/git-repo-tools/tests/unit/entities/` | GIT | Git repository entity tests |

**GitHub Data Tools Unit Tests:**

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/unit/github/` | `packages/github-data-tools/tests/unit/github/` | DATA | Most GitHub service tests |
| `tests/unit/entities/comments/` | `packages/github-data-tools/tests/unit/entities/comments/` | DATA | |
| `tests/unit/entities/issues/` | `packages/github-data-tools/tests/unit/entities/issues/` | DATA | |
| `tests/unit/entities/labels/` | `packages/github-data-tools/tests/unit/entities/labels/` | DATA | |
| `tests/unit/entities/milestones/` | `packages/github-data-tools/tests/unit/entities/milestones/` | DATA | |
| `tests/unit/entities/pr_comments/` | `packages/github-data-tools/tests/unit/entities/pr_comments/` | DATA | |
| `tests/unit/entities/pr_review_comments/` | `packages/github-data-tools/tests/unit/entities/pr_review_comments/` | DATA | |
| `tests/unit/entities/pr_reviews/` | `packages/github-data-tools/tests/unit/entities/pr_reviews/` | DATA | |
| `tests/unit/entities/pull_requests/` | `packages/github-data-tools/tests/unit/entities/pull_requests/` | DATA | |
| `tests/unit/entities/releases/` | `packages/github-data-tools/tests/unit/entities/releases/` | DATA | |
| `tests/unit/entities/sub_issues/` | `packages/github-data-tools/tests/unit/entities/sub_issues/` | DATA | |
| `tests/unit/operations/restore/` | `packages/github-data-tools/tests/unit/operations/restore/` | DATA | |
| `tests/unit/operations/save/` | `packages/github-data-tools/tests/unit/operations/save/` | DATA | |
| `tests/unit/tools/` | `packages/github-data-tools/tests/unit/tools/` | DATA | |
| `tests/unit/test_*.py` (various) | `packages/github-data-tools/tests/unit/` | DATA | Most other unit tests |

---

### tests/integration/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/integration/` | `packages/github-data-tools/tests/integration/` | DATA | Most integration tests focus on GitHub data |
| `tests/integration/operations/` | `packages/github-data-tools/tests/integration/operations/` | DATA | |

---

### tests/container/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/container/` | SPLIT | Multiple | Split based on container being tested |
| Container tests for git operations | `packages/git-repo-tools/tests/container/` | GIT | |
| Container tests for GitHub data operations | `packages/github-data-tools/tests/container/` | DATA | |
| End-to-end workflow tests | `packages/kit-orchestrator/tests/container/` | ORCH | |

---

### tests/fixtures/

| Current Path | Destination | Package | Notes |
|-------------|-------------|---------|-------|
| `tests/fixtures/test_entities/` | `packages/core/tests/fixtures/test_entities/` | CORE | Entity framework test fixtures |

---

## New Files to Create

### Core Package

```
packages/core/src/github_data_core/
├── parameters/
│   └── env_loader.py          # NEW: Extract from main.py
├── github/
│   ├── auth.py                # NEW: Token management
│   └── retry.py               # NEW: Retry logic (if not in rate_limiter)
└── __init__.py                # NEW: Core package exports
```

### Git Repo Tools Package

```
packages/git-repo-tools/src/git_repo_tools/
├── operations/
│   ├── __init__.py            # NEW
│   ├── save.py                # NEW: Git save operation
│   └── restore.py             # NEW: Git restore operation
├── __main__.py                # NEW: CLI entry point
└── __init__.py                # NEW: Package exports
```

### GitHub Repo Manager Package

```
packages/github-repo-manager/src/github_repo_manager/
├── github/
│   ├── __init__.py            # NEW
│   ├── repo_service.py        # NEW: Extract create_repository from service.py
│   └── repo_boundary.py       # NEW: Narrow REST API for repo operations
├── operations/
│   ├── __init__.py            # NEW
│   ├── create.py              # NEW: Extract from main.py + service.py
│   ├── check.py               # NEW: Check if repo exists
│   └── delete.py              # NEW: Delete repo (post-migration)
├── __main__.py                # NEW: CLI entry point
└── __init__.py                # NEW: Package exports
```

### GitHub Data Tools Package

```
packages/github-data-tools/src/github_data_tools/
├── __main__.py                # NEW: CLI entry point
└── __init__.py                # NEW: Package exports
```

### Kit Orchestrator Package

```
packages/kit-orchestrator/src/kit_orchestrator/
├── orchestrator.py            # NEW: High-level workflow orchestration
├── __main__.py                # NEW: CLI entry point
└── __init__.py                # NEW: Package exports
```

---

## Files Requiring Splits

### main.py Split Strategy

**Target: main.py (291 lines)**

1. **Lines 49-107** → `packages/core/src/github_data_core/parameters/env_loader.py`
   - All `_load_*_from_environment()` methods
   - Create `ParameterLoader` class

2. **Lines 109-211** → `packages/github-repo-manager/src/github_repo_manager/operations/create.py`
   - `_ensure_repository_exists()`
   - `_wait_for_repository_availability()`
   - Create `RepositoryCreator` class

3. **Lines 212-234** → Each package's factory/init
   - `_build_github_service()` → Split: narrow boundary in repo-mgr, full in data-tools
   - `_build_storage_service()` → Core factory
   - `_build_git_service()` → Git repo tools factory
   - `_build_orchestrator()` → Data tools factory

4. **Lines 236-270** → `packages/kit-orchestrator/src/kit_orchestrator/orchestrator.py`
   - `_execute_operation()`
   - `_print_*()` methods

### github/boundary.py Split Strategy

**Current:** Single boundary with all GitHub API methods

**Target:**
1. `packages/github-repo-manager/src/github_repo_manager/github/repo_boundary.py`
   - Only repository CRUD methods
   - `create_repository()`, `get_repository()`, `delete_repository()`

2. `packages/github-data-tools/src/github_data_tools/github/boundary.py`
   - All other GitHub API methods
   - Issues, PRs, labels, milestones, releases, comments, etc.

### github/service.py Split Strategy

**Current:** Single service with all operations

**Target:**
1. `packages/github-repo-manager/src/github_repo_manager/github/repo_service.py`
   - `create_repository()` method
   - `get_repository_metadata()` method
   - Repository-specific logic

2. `packages/github-data-tools/src/github_data_tools/github/service.py`
   - All other service methods
   - Entity save/restore operations

### github/protocols.py Split Strategy

**Target:**
1. `packages/core/src/github_data_core/github/protocols.py`
   - Base protocol definitions
   - `GitHubClient` protocol

2. `packages/github-data-tools/src/github_data_tools/github/protocols.py`
   - Data-specific protocols
   - Entity operation protocols

---

## Import Update Strategy

After moving files, all imports must be updated:

### Core Package Imports

```python
# Old
from github_data.storage import JsonStorage

# New
from github_data_core.storage import JsonStorage
```

### Cross-Package Imports

```python
# In git-repo-tools, importing from core
from github_data_core.parameters import ParameterLoader
from github_data_core.storage import StorageService

# In github-data-tools, importing from core
from github_data_core.entities import BaseEntity, EntityRegistry
from github_data_core.operations import StrategyBasedOrchestrator
```

### No Cross-Sibling Imports

Git repo tools and GitHub data tools should NOT import from each other. They only import from core.

---

## Summary Statistics

### File Counts by Destination

- **Core:** ~20-25 files
- **Git Repo Tools:** ~10-12 files (git package + entity)
- **GitHub Repo Manager:** ~5-8 files (new package, mostly extracted code)
- **GitHub Data Tools:** ~120-130 files (most entities + operations + queries)
- **Kit Orchestrator:** ~3-5 files (new package, orchestration)

### Test File Counts by Destination

- **Core Tests:** ~15-20 test files
- **Git Repo Tools Tests:** ~5-8 test files
- **GitHub Repo Manager Tests:** ~3-5 test files (mostly new)
- **GitHub Data Tools Tests:** ~80-90 test files (most existing tests)
- **Kit Orchestrator Tests:** ~2-3 test files (end-to-end)

### Files Requiring Splits

- `main.py` → 4 destinations
- `github/boundary.py` → 2 destinations
- `github/service.py` → 2 destinations
- `github/protocols.py` → 2 destinations
- `github/__init__.py` → 3 destinations (factory splits)

### New Files to Create

- ~15-20 new files across all packages
- Primarily entry points, CLI wrappers, and split extracts

---

## Migration Checklist per Package

### Phase 3: Core Extraction
- [ ] Move `config/` module
- [ ] Move `entities/base.py`, `entities/registry.py`, `entities/strategy_context.py`
- [ ] Move `storage/` module
- [ ] Move `operations/orchestrator_base.py`, `operations/strategy_factory.py`
- [ ] Extract base GitHub client, rate limiter, cache from `github/`
- [ ] Create `parameters/env_loader.py` (extract from main.py)
- [ ] Update all internal imports
- [ ] Move core tests
- [ ] Move shared test fixtures

### Phase 4: Git Repo Tools Extraction
- [ ] Move `git/` module
- [ ] Move `entities/git_repositories/` entity
- [ ] Create `operations/save.py` and `operations/restore.py`
- [ ] Create `__main__.py` CLI entry point
- [ ] Update imports (internal + core references)
- [ ] Move git-related tests
- [ ] Create Dockerfile

### Phase 5: GitHub Repo Manager Creation
- [ ] Extract repository creation from `main.py`
- [ ] Extract `create_repository()` from `github/service.py`
- [ ] Create `github/repo_boundary.py` (narrow API)
- [ ] Create `operations/create.py`
- [ ] Create `operations/check.py`
- [ ] Create `__main__.py` CLI entry point
- [ ] Write tests for new operations
- [ ] Create Dockerfile

### Phase 6: GitHub Data Tools Extraction
- [ ] Move all entity directories (comments, issues, labels, etc.)
- [ ] Move `github/` module (except repo creation parts)
- [ ] Move `operations/save/` and `operations/restore/`
- [ ] Move `tools/` module
- [ ] Create `__main__.py` CLI entry point
- [ ] Update imports (internal + core references)
- [ ] Move most unit tests
- [ ] Move most integration tests
- [ ] Move most container tests
- [ ] Create Dockerfile

### Phase 7: Kit Orchestrator Creation
- [ ] Extract orchestration logic from `main.py`
- [ ] Create `orchestrator.py` (high-level workflows)
- [ ] Create `__main__.py` CLI entry point
- [ ] Create end-to-end tests
- [ ] Create Dockerfile (bundles all packages)

---

## Notes for Implementers

1. **Start with Core**: Core has no dependencies, so extract it first
2. **Git is Independent**: Git repo tools only depends on core, can be done in parallel with repo manager
3. **Repo Manager Before Data Tools**: Some data tools tests may reference repo creation
4. **Data Tools is Largest**: Budget most time for this package
5. **Orchestrator Last**: Requires all other packages to exist

6. **Test Early, Test Often**: Run tests after each package extraction
7. **Update Imports Incrementally**: Don't try to fix all imports at once
8. **Use Find-Replace Carefully**: Many imports will follow patterns

9. **Watch for Circular Dependencies**: If you find one, it means the boundary is wrong
10. **Document Assumptions**: If you make a decision about where something goes, document it

---

**End of Module Mapping Document**

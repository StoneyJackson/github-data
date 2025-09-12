# GraphQL Hybrid Implementation

This document describes the hybrid GraphQL/REST implementation for the GitHub Data project.

## Overview

The GitHub Data project now supports a hybrid approach that uses:
- **GraphQL for read operations** (backup/export) - dramatically reduces API calls
- **REST for write operations** (restore/create) - complete feature support

## Implementation Details

### Files Added/Modified

**New Files:**
- `src/github/graphql_queries.py` - GraphQL query definitions
- `src/github/graphql_converters.py` - Convert GraphQL responses to REST format
- `tests/test_graphql_integration.py` - GraphQL functionality tests

**Modified Files:**
- `pyproject.toml` - Added `gql[all]>=3.4.0` dependency
- `src/github/boundary.py` - Added GraphQL support with REST fallback
- `src/github/service.py` - No changes needed (transparent to service layer)

### Architecture

```
GitHubService (unchanged)
    ↓
GitHubApiBoundary (hybrid)
    ├── GraphQL Client (reads) → convert to REST format
    └── PyGithub (writes) → existing functionality
```

### Required Dependencies

GraphQL is now a required dependency for read operations. If the `gql` dependency is not installed, the application will fail fast with clear import errors, ensuring consistent behavior across environments.

## Benefits Achieved

### Performance Improvements
- **Labels**: 1 GraphQL query vs multiple REST calls
- **Issues**: Single paginated query vs dozens of REST requests  
- **Comments**: Bulk fetch vs sequential API calls per issue
- **Rate Limiting**: More efficient use of GitHub API limits

### Backward Compatibility
- Existing REST functionality preserved for write operations
- Service layer unchanged - transparent upgrade
- All existing tests continue to pass
- Same data format returned (GraphQL converted to REST format)

## Installation

GraphQL is now required for read operations:

```bash
pdm install  # Installs gql[all] dependency
```

The application will fail to start without this dependency, ensuring consistent performance across environments.

## Usage

No code changes required. The boundary layer:
1. Uses GraphQL for all read operations (labels, issues, comments)
2. Uses REST for all write operations (create, update, delete)
3. Returns consistent REST-compatible data format

## Testing

Run the test suite:

```bash
make test-fast    # Fast tests excluding container integration
make test         # Full test suite
```

The tests verify both GraphQL read operations and REST write operations work correctly.

## Future Enhancements

1. **Bulk Mutations**: If GitHub adds GraphQL bulk operations
2. **Query Optimization**: Fine-tune GraphQL queries for specific use cases
3. **Caching Strategy**: Optimize caching for GraphQL's different response structure
4. **Error Handling**: Enhanced error handling for GraphQL-specific issues

## Migration Notes

No migration required. The hybrid implementation:
- Maintains existing API contracts
- Provides automatic performance improvements for read operations
- Uses GraphQL as required dependency for consistent behavior
- Requires no changes to calling code
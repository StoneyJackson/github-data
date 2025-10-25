# Entity Generator CLI Tool Guide

## Overview

The entity generator CLI tool automates the creation of entity boilerplate code, including:
- Entity configuration class
- Pydantic data models
- Save strategy skeleton
- Restore strategy skeleton
- Package __init__.py

## Usage

### Interactive Mode

Run without arguments to be prompted for each value:

```bash
python -m src.tools.generate_entity
```

### Command-Line Arguments Mode

Provide all values as arguments:

```bash
python -m src.tools.generate_entity \
    --name comment_attachments \
    --type bool \
    --default true \
    --deps issues,comments \
    --description "Save and restore comment attachments"
```

### Hybrid Mode

Provide some arguments, get prompted for missing values:

```bash
python -m src.tools.generate_entity --name comment_attachments
# Prompts for: type, default, deps, description
```

## Arguments

| Argument | Description | Example | Required |
|----------|-------------|---------|----------|
| `--name` | Entity name (snake_case) | `comment_attachments` | Yes* |
| `--type` | Value type: `bool` or `set` | `bool` | Yes* |
| `--default` | Default value: `true` or `false` | `true` | Yes* |
| `--deps` | Comma-separated dependencies | `issues,comments` | No |
| `--description` | Entity description | `"Comment attachments"` | Yes* |
| `--force` | Overwrite existing files | N/A (flag) | No |

*Required via argument or prompt

## Generated Files

The tool generates this structure:

```
src/entities/{entity_name}/
├── __init__.py              # Public API exports
├── entity_config.py         # EntityConfig implementation
├── models.py                # Pydantic data models (template)
├── save_strategy.py         # Save strategy (skeleton)
└── restore_strategy.py      # Restore strategy (skeleton)
```

## Next Steps After Generation

1. **Implement save logic** in `save_strategy.py`:
   - Fetch data from GitHub
   - Transform to Pydantic models
   - Save to JSON

2. **Implement restore logic** in `restore_strategy.py`:
   - Load data from JSON
   - Validate data
   - Restore to GitHub

3. **Customize data models** in `models.py`:
   - Add entity-specific fields
   - Add validation rules

4. **Write tests** for your entity:
   - Unit tests for strategies
   - Integration tests for workflows

5. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## Examples

### Example 1: Simple Boolean Entity

```bash
python -m src.tools.generate_entity \
    --name notifications \
    --type bool \
    --default false \
    --description "Save and restore notifications"
```

### Example 2: Entity with Dependencies

```bash
python -m src.tools.generate_entity \
    --name comment_attachments \
    --type bool \
    --default true \
    --deps issues,comments \
    --description "Save and restore comment attachments"
```

### Example 3: Set-Based Entity

```bash
python -m src.tools.generate_entity \
    --name selective_issues \
    --type set \
    --default true \
    --description "Save specific issue numbers"
```

## Validation Rules

### Entity Name
- Must be lowercase
- Must use snake_case
- Alphanumeric and underscores only
- Cannot start or end with underscore

### Environment Variable
- Auto-generated as `INCLUDE_{UPPER_SNAKE}`
- Can be customized during generation

### Dependencies
- Must reference existing entity names
- Comma-separated list
- Empty list is valid

## Troubleshooting

### Error: "Invalid entity name"
- Ensure name is lowercase snake_case
- No special characters except underscores
- Example: `comment_attachments` ✓, `CommentAttachments` ✗

### Error: "Entity directory already exists"
- Use `--force` to overwrite
- Or delete the directory manually

### Generated files have syntax errors
- Report as bug
- Check template files in `src/tools/templates/`

### Entity not auto-discovered
- Verify `entity_config.py` exists
- Verify class name ends with `EntityConfig`
- Check for import errors in entity files

## See Also

- [Entity Development Guide](entity-development-guide.md)
- [Phase 2 Implementation Plan](planning/2025-10-24-phase-2-cli-generator-implementation-plan.md)
- [Entity Registry Design](planning/2025-10-24-01-11-entity-registry-system-design-and-implementation-plan.md)

"""CLI tool for generating entity boilerplate code.

Usage:
    # Interactive mode
    python -m src.tools.generate_entity

    # Command-line args mode
    python -m src.tools.generate_entity \
        --name comment_attachments \
        --type bool \
        --default true \
        --deps issues,comments \
        --description "Save and restore comment attachments"

    # Hybrid mode (some args, prompts for missing)
    python -m src.tools.generate_entity --name comment_attachments
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Callable
from jinja2 import Environment, FileSystemLoader


def main() -> None:
    """Main entry point for the entity generator CLI tool."""
    args = parse_arguments()

    # Gather all inputs
    entity_name = get_entity_name(args)
    env_var = get_env_var_name(entity_name, args)
    value_type = get_value_type(args)
    default_value = get_default_value(args)
    dependencies = get_dependencies(args)
    description = get_description(args)

    # Generate files
    generate_entity_files(
        entity_name,
        env_var,
        value_type,
        default_value,
        dependencies,
        description,
        args.force,
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Generate entity boilerplate code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--name", type=str, help="Entity name in snake_case (e.g., comment_attachments)"
    )

    parser.add_argument(
        "--type",
        type=str,
        choices=["bool", "set"],
        help="Value type: 'bool' or 'set' (for Set[int])",
    )

    parser.add_argument("--default", type=str, help="Default value: 'true' or 'false'")

    parser.add_argument(
        "--deps",
        type=str,
        help="Comma-separated dependencies (e.g., 'issues,comments')",
    )

    parser.add_argument("--description", type=str, help="Entity description")

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting",
    )

    return parser.parse_args()


def validate_entity_name(name: str) -> bool:
    """Validate entity name format.

    Args:
        name: Entity name to validate

    Returns:
        True if valid, False otherwise
    """
    # Must be snake_case, lowercase, alphanumeric + underscores
    if not name:
        return False

    if not name.islower():
        return False

    if not all(c.isalnum() or c == "_" for c in name):
        return False

    if name.startswith("_") or name.endswith("_"):
        return False

    return True


def prompt_for_value(
    prompt: str,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
) -> str:
    """Prompt user for a value with optional default and validation.

    Args:
        prompt: Prompt message
        default: Default value (shown in brackets)
        validator: Optional validation function

    Returns:
        User input or default value
    """
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "

    while True:
        value: str = input(prompt_text).strip()

        # Use default if no input
        if not value and default:
            value = default

        # Validate if validator provided
        if validator and not validator(value):
            print("Invalid input. Please try again.")
            continue

        return value


def get_entity_name(args: argparse.Namespace) -> str:
    """Get entity name from args or prompt.

    Args:
        args: Parsed command-line arguments

    Returns:
        Valid entity name
    """
    name: str
    if args.name:
        if not validate_entity_name(args.name):
            print(f"Error: Invalid entity name '{args.name}'")
            print("Entity name must be lowercase snake_case")
            sys.exit(1)
        name = str(args.name)
        return name

    name = prompt_for_value("Entity name (snake_case)", validator=validate_entity_name)
    return name


def get_env_var_name(entity_name: str, args: argparse.Namespace) -> str:
    """Get environment variable name.

    Args:
        entity_name: Entity name in snake_case
        args: Parsed arguments (for future customization)

    Returns:
        Environment variable name (e.g., INCLUDE_COMMENT_ATTACHMENTS)
    """
    # Convention: INCLUDE_{UPPER_SNAKE}
    env_var = f"INCLUDE_{entity_name.upper()}"
    return env_var


def get_value_type(args: argparse.Namespace) -> str:
    """Get value type from args or prompt.

    Args:
        args: Parsed command-line arguments

    Returns:
        'bool' or 'set'
    """
    value_type: str
    if args.type:
        value_type = str(args.type)
        return value_type

    value_type = prompt_for_value(
        "Value type (bool/set)",
        default="bool",
        validator=lambda x: x in ["bool", "set"],
    )

    return value_type


def get_default_value(args: argparse.Namespace) -> str:
    """Get default value from args or prompt.

    Args:
        args: Parsed command-line arguments

    Returns:
        'true' or 'false'
    """
    default_choice: str
    if args.default:
        if args.default.lower() not in ["true", "false"]:
            print("Error: Default must be 'true' or 'false'")
            sys.exit(1)
        default_choice = str(args.default.lower())
        return default_choice

    default_choice = prompt_for_value(
        "Default value (true/false)",
        default="true",
        validator=lambda x: x.lower() in ["true", "false"],
    )

    return default_choice.lower()


def get_dependencies(args: argparse.Namespace) -> List[str]:
    """Get dependencies from args or prompt.

    Args:
        args: Parsed command-line arguments

    Returns:
        List of dependency names
    """
    if args.deps is not None:
        if not args.deps:
            return []
        deps = [d.strip() for d in args.deps.split(",")]
        return [d for d in deps if d]  # Filter empty strings

    deps_input = prompt_for_value(
        "Dependencies (comma-separated, or empty)", default=""
    )

    if not deps_input:
        return []

    deps = [d.strip() for d in deps_input.split(",")]
    return [d for d in deps if d]


def get_description(args: argparse.Namespace) -> str:
    """Get entity description from args or prompt.

    Args:
        args: Parsed command-line arguments

    Returns:
        Entity description
    """
    description: str
    if args.description:
        description = str(args.description)
        return description

    description = prompt_for_value("Description", default="Entity description")
    return description


def snake_to_pascal(snake_str: str) -> str:
    """Convert snake_case to PascalCase.

    Args:
        snake_str: String in snake_case

    Returns:
        String in PascalCase

    Example:
        >>> snake_to_pascal("comment_attachments")
        "CommentAttachments"
    """
    components = snake_str.split("_")
    return "".join(x.title() for x in components)


def prepare_template_context(
    entity_name: str,
    env_var: str,
    value_type: str,
    default_value: str,
    dependencies: List[str],
    description: str,
) -> dict:
    """Prepare context dictionary for template rendering.

    Args:
        entity_name: Entity name in snake_case
        env_var: Environment variable name
        value_type: 'bool' or 'set'
        default_value: 'true' or 'false'
        dependencies: List of dependency names
        description: Entity description

    Returns:
        Context dictionary for Jinja2 templates
    """
    base_name = snake_to_pascal(entity_name)

    # Determine Python type representation
    if value_type == "bool":
        python_type = "bool"
        python_default = "True" if default_value == "true" else "False"
    else:  # set
        python_type = "Union[bool, Set[int]]"
        python_default = "True" if default_value == "true" else "False"

    return {
        "entity_name": entity_name,
        "class_name": f"{base_name}EntityConfig",
        "model_class_name": f"{base_name}",
        "save_strategy_class": f"{base_name}SaveStrategy",
        "restore_strategy_class": f"{base_name}RestoreStrategy",
        "env_var": env_var,
        "default_value": python_default,
        "value_type": python_type,
        "dependencies": dependencies,
        "description": description,
    }


def check_file_conflicts(entity_path: Path, force: bool) -> bool:
    """Check if entity directory already exists.

    Args:
        entity_path: Path to entity directory
        force: If True, skip conflict check

    Returns:
        True if OK to proceed, False otherwise
    """
    if not entity_path.exists():
        return True

    if force:
        print(f"Warning: Overwriting existing entity at {entity_path}")
        return True

    print(f"Error: Entity directory already exists: {entity_path}")
    print("Use --force to overwrite")
    return False


def render_templates(context: dict, entity_path: Path) -> None:
    """Render all templates and write to entity directory.

    Args:
        context: Template context dictionary
        entity_path: Path to entity directory
    """
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Create entity directory
    entity_path.mkdir(parents=True, exist_ok=True)

    # Template mappings: (template_file, output_file)
    templates = [
        ("entity_config_template.py.j2", "entity_config.py"),
        ("models_template.py.j2", "models.py"),
        ("save_strategy_template.py.j2", "save_strategy.py"),
        ("restore_strategy_template.py.j2", "restore_strategy.py"),
        ("init_template.py.j2", "__init__.py"),
    ]

    for template_file, output_file in templates:
        template = env.get_template(template_file)
        rendered = template.render(**context)

        output_path = entity_path / output_file
        output_path.write_text(rendered)
        print(f"  ✓ {output_file}")


def generate_entity_files(
    entity_name: str,
    env_var: str,
    value_type: str,
    default_value: str,
    dependencies: List[str],
    description: str,
    force: bool,
) -> None:
    """Generate all entity files from templates.

    Args:
        entity_name: Entity name in snake_case
        env_var: Environment variable name
        value_type: 'bool' or 'set'
        default_value: 'true' or 'false'
        dependencies: List of dependency names
        description: Entity description
        force: Overwrite existing files
    """
    # Determine entity path
    project_root = Path(__file__).parent.parent.parent
    entity_path = project_root / "src" / "entities" / entity_name

    # Check for conflicts
    if not check_file_conflicts(entity_path, force):
        sys.exit(1)

    # Prepare template context
    context = prepare_template_context(
        entity_name, env_var, value_type, default_value, dependencies, description
    )

    # Render templates
    print(f"\n✓ Generating entity: {entity_name}")
    print(f"  Path: {entity_path}")
    render_templates(context, entity_path)

    print("\n✓ Entity generated successfully!")
    print("\nNext steps:")
    print(f"  1. Implement save logic in {entity_path}/save_strategy.py")
    print(f"  2. Implement restore logic in {entity_path}/restore_strategy.py")
    print(f"  3. Customize data models in {entity_path}/models.py")
    print("  4. Write entity-specific tests")
    print("  5. Run: pytest tests/ -v")


if __name__ == "__main__":
    main()

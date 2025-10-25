"""Labels entity configuration for EntityRegistry."""


class LabelsEntityConfig:
    """Configuration for labels entity.

    Labels have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "labels"
    env_var = "INCLUDE_LABELS"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None  # Use convention
    restore_strategy_class = None  # Use convention
    storage_filename = None  # Use convention (labels.json)
    description = "Repository labels for issue/PR categorization"

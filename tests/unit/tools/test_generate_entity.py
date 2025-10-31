"""Unit tests for entity generator CLI tool."""

import pytest
import ast
from github_data.tools.generate_entity import (
    validate_entity_name,
    snake_to_pascal,
    prepare_template_context,
    check_file_conflicts,
    render_templates,
)


@pytest.mark.unit
@pytest.mark.fast
class TestValidateEntityName:
    """Test entity name validation."""

    def test_valid_snake_case(self):
        """Valid snake_case names should pass."""
        assert validate_entity_name("comment_attachments")
        assert validate_entity_name("issues")
        assert validate_entity_name("pr_review_comments")

    def test_invalid_uppercase(self):
        """Uppercase letters should fail."""
        assert not validate_entity_name("CommentAttachments")
        assert not validate_entity_name("Issues")

    def test_invalid_special_chars(self):
        """Special characters should fail."""
        assert not validate_entity_name("comment-attachments")
        assert not validate_entity_name("comment.attachments")
        assert not validate_entity_name("comment/attachments")

    def test_invalid_leading_underscore(self):
        """Leading underscores should fail."""
        assert not validate_entity_name("_comments")

    def test_invalid_trailing_underscore(self):
        """Trailing underscores should fail."""
        assert not validate_entity_name("comments_")

    def test_empty_string(self):
        """Empty string should fail."""
        assert not validate_entity_name("")


@pytest.mark.unit
@pytest.mark.fast
class TestSnakeToPascal:
    """Test snake_case to PascalCase conversion."""

    def test_single_word(self):
        """Single word conversion."""
        assert snake_to_pascal("issues") == "Issues"

    def test_multiple_words(self):
        """Multiple word conversion."""
        assert snake_to_pascal("comment_attachments") == "CommentAttachments"
        assert snake_to_pascal("pr_review_comments") == "PrReviewComments"

    def test_preserves_numbers(self):
        """Numbers should be preserved."""
        assert snake_to_pascal("test_123_entity") == "Test123Entity"


@pytest.mark.unit
@pytest.mark.fast
class TestPrepareTemplateContext:
    """Test template context preparation."""

    def test_bool_type_context(self):
        """Context for bool type entity."""
        context = prepare_template_context(
            entity_name="test_entity",
            env_var="INCLUDE_TEST_ENTITY",
            value_type="bool",
            default_value="true",
            dependencies=["issues"],
            save_services=["github_service"],
            restore_services=["github_service", "conflict_strategy"],
            description="Test entity",
        )

        assert context["entity_name"] == "test_entity"
        assert context["class_name"] == "TestEntityEntityConfig"
        assert context["model_class_name"] == "TestEntity"
        assert context["save_strategy_class"] == "TestEntitySaveStrategy"
        assert context["restore_strategy_class"] == "TestEntityRestoreStrategy"
        assert context["env_var"] == "INCLUDE_TEST_ENTITY"
        assert context["default_value"] == "True"
        assert context["value_type"] == "bool"
        assert context["dependencies"] == ["issues"]
        assert context["description"] == "Test entity"

    def test_set_type_context(self):
        """Context for set type entity."""
        context = prepare_template_context(
            entity_name="issues",
            env_var="INCLUDE_ISSUES",
            value_type="set",
            default_value="false",
            dependencies=[],
            save_services=["github_service"],
            restore_services=["github_service", "conflict_strategy"],
            description="Issues entity",
        )

        assert context["value_type"] == "Union[bool, Set[int]]"
        assert context["default_value"] == "False"

    def test_no_dependencies(self):
        """Context with no dependencies."""
        context = prepare_template_context(
            entity_name="labels",
            env_var="INCLUDE_LABELS",
            value_type="bool",
            default_value="true",
            dependencies=[],
            save_services=["github_service"],
            restore_services=["github_service", "conflict_strategy"],
            description="Labels",
        )

        assert context["dependencies"] == []


@pytest.mark.unit
@pytest.mark.fast
class TestCheckFileConflicts:
    """Test file conflict detection."""

    def test_no_conflict_if_not_exists(self, tmp_path):
        """Should return True if directory doesn't exist."""
        entity_path = tmp_path / "entities" / "new_entity"
        assert check_file_conflicts(entity_path, force=False)

    def test_conflict_if_exists_without_force(self, tmp_path):
        """Should return False if directory exists and force=False."""
        entity_path = tmp_path / "entities" / "existing_entity"
        entity_path.mkdir(parents=True)

        assert not check_file_conflicts(entity_path, force=False)

    def test_no_conflict_if_exists_with_force(self, tmp_path, capsys):
        """Should return True if directory exists and force=True."""
        entity_path = tmp_path / "entities" / "existing_entity"
        entity_path.mkdir(parents=True)

        assert check_file_conflicts(entity_path, force=True)

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Overwriting" in captured.out


@pytest.mark.unit
@pytest.mark.fast
class TestRenderTemplates:
    """Test template rendering."""

    def test_renders_all_files(self, tmp_path):
        """Should render all entity files."""
        context = {
            "entity_name": "test_entity",
            "class_name": "TestEntityEntityConfig",
            "model_class_name": "TestEntity",
            "save_strategy_class": "TestEntitySaveStrategy",
            "restore_strategy_class": "TestEntityRestoreStrategy",
            "env_var": "INCLUDE_TEST_ENTITY",
            "default_value": "True",
            "value_type": "bool",
            "dependencies": ["issues"],
            "description": "Test entity",
            "required_services_save": "['github_service']",
            "required_services_restore": "['github_service', 'conflict_strategy']",
            "save_services": ["github_service"],
            "restore_services": ["github_service", "conflict_strategy"],
            "service_descriptions": {
                "github_service": "GitHub API service",
                "conflict_strategy": "Conflict resolution strategy",
            },
        }

        entity_path = tmp_path / "test_entity"
        render_templates(context, entity_path)

        # Verify all files were created
        assert (entity_path / "entity_config.py").exists()
        assert (entity_path / "models.py").exists()
        assert (entity_path / "save_strategy.py").exists()
        assert (entity_path / "restore_strategy.py").exists()
        assert (entity_path / "__init__.py").exists()

    def test_entity_config_contains_correct_values(self, tmp_path):
        """Entity config should contain correct values."""
        context = {
            "entity_name": "comment_attachments",
            "class_name": "CommentAttachmentsEntityConfig",
            "model_class_name": "CommentAttachments",
            "save_strategy_class": "CommentAttachmentsSaveStrategy",
            "restore_strategy_class": "CommentAttachmentsRestoreStrategy",
            "env_var": "INCLUDE_COMMENT_ATTACHMENTS",
            "default_value": "True",
            "value_type": "bool",
            "dependencies": ["issues", "comments"],
            "description": "Comment attachments",
            "required_services_save": "['github_service']",
            "required_services_restore": "['github_service', 'conflict_strategy']",
            "save_services": ["github_service"],
            "restore_services": ["github_service", "conflict_strategy"],
            "service_descriptions": {
                "github_service": "GitHub API service",
                "conflict_strategy": "Conflict resolution strategy",
            },
        }

        entity_path = tmp_path / "comment_attachments"
        render_templates(context, entity_path)

        config_content = (entity_path / "entity_config.py").read_text()

        # Verify key content
        assert 'name = "comment_attachments"' in config_content
        assert 'env_var = "INCLUDE_COMMENT_ATTACHMENTS"' in config_content
        assert "default_value = True" in config_content
        assert "value_type = bool" in config_content
        assert "dependencies = ['issues', 'comments']" in config_content

    def test_generated_files_are_valid_python(self, tmp_path):
        """Generated files should be valid Python."""
        context = {
            "entity_name": "test_entity",
            "class_name": "TestEntityEntityConfig",
            "model_class_name": "TestEntity",
            "save_strategy_class": "TestEntitySaveStrategy",
            "restore_strategy_class": "TestEntityRestoreStrategy",
            "env_var": "INCLUDE_TEST_ENTITY",
            "default_value": "True",
            "value_type": "bool",
            "dependencies": [],
            "description": "Test",
            "required_services_save": "['github_service']",
            "required_services_restore": "['github_service', 'conflict_strategy']",
            "save_services": ["github_service"],
            "restore_services": ["github_service", "conflict_strategy"],
            "service_descriptions": {
                "github_service": "GitHub API service",
                "conflict_strategy": "Conflict resolution strategy",
            },
        }

        entity_path = tmp_path / "test_entity"
        render_templates(context, entity_path)

        # Try to parse each file as valid Python
        for py_file in entity_path.glob("*.py"):
            content = py_file.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Invalid Python syntax in {py_file.name}: {e}")


@pytest.mark.unit
@pytest.mark.fast
class TestGenerateEntityFiles:
    """Test complete entity file generation."""

    def test_full_workflow_with_all_files(self, tmp_path):
        """Test full workflow from context to file generation."""
        # Prepare context
        context = prepare_template_context(
            entity_name="full_test",
            env_var="INCLUDE_FULL_TEST",
            value_type="bool",
            default_value="true",
            dependencies=["issues", "comments"],
            save_services=["github_service"],
            restore_services=["github_service", "conflict_strategy"],
            description="Full workflow test",
        )

        # Render templates
        entity_path = tmp_path / "full_test"
        render_templates(context, entity_path)

        # Verify all files exist and are valid Python
        assert entity_path.exists()
        assert (entity_path / "entity_config.py").exists()
        assert (entity_path / "models.py").exists()
        assert (entity_path / "save_strategy.py").exists()
        assert (entity_path / "restore_strategy.py").exists()
        assert (entity_path / "__init__.py").exists()

        # Verify all files can be parsed as Python
        for py_file in entity_path.glob("*.py"):
            content = py_file.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Invalid Python in {py_file.name}: {e}")

        # Verify entity_config has correct structure
        config_content = (entity_path / "entity_config.py").read_text()
        assert "class FullTestEntityConfig" in config_content
        assert 'name = "full_test"' in config_content
        assert "dependencies = ['issues', 'comments']" in config_content

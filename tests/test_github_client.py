"""Tests for the GitHub client module."""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest
from github import Github
from github.Repository import Repository
from github.Issue import Issue as PyGithubIssue
from github.Label import Label as PyGithubLabel
from github.IssueComment import IssueComment as PyGithubComment
from github.PaginatedList import PaginatedList

from src.github_client import GitHubClient
from src.models import Issue, Label, Comment, GitHubUser


class TestGitHubClient:
    """Test cases for GitHubClient class."""

    @pytest.fixture
    def mock_github(self):
        """Create a mock Github instance."""
        return Mock(spec=Github)

    @pytest.fixture
    def mock_repo(self):
        """Create a mock Repository instance."""
        return Mock(spec=Repository)

    @pytest.fixture
    def github_client(self, mock_github):
        """Create a GitHubClient instance with mocked Github."""
        with patch("src.github_client.Github", return_value=mock_github):
            return GitHubClient("fake_token")

    @pytest.fixture
    def sample_user_data(self):
        """Sample GitHub user data."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_user.id = 12345
        mock_user.avatar_url = "https://github.com/avatar.png"
        mock_user.html_url = "https://github.com/testuser"
        return mock_user

    @pytest.fixture
    def sample_label_data(self):
        """Sample GitHub label data."""
        mock_label = Mock(spec=PyGithubLabel)
        mock_label.name = "bug"
        mock_label.color = "ff0000"
        mock_label.description = "Something isn't working"
        mock_label.url = "https://api.github.com/repos/owner/repo/labels/bug"
        mock_label.id = 54321
        return mock_label

    @pytest.fixture
    def sample_issue_data(self, sample_user_data, sample_label_data):
        """Sample GitHub issue data."""
        mock_issue = Mock(spec=PyGithubIssue)
        mock_issue.id = 98765
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.body = "This is a test issue"
        mock_issue.state = "open"
        mock_issue.user = sample_user_data
        mock_issue.assignees = []
        mock_issue.labels = [sample_label_data]
        mock_issue.created_at = datetime(2023, 1, 1, 10, 0, 0)
        mock_issue.updated_at = datetime(2023, 1, 2, 10, 0, 0)
        mock_issue.closed_at = None
        mock_issue.html_url = "https://github.com/owner/repo/issues/1"
        mock_issue.comments = 2
        return mock_issue

    @pytest.fixture
    def sample_comment_data(self, sample_user_data):
        """Sample GitHub comment data."""
        mock_comment = Mock(spec=PyGithubComment)
        mock_comment.id = 11111
        mock_comment.body = "This is a test comment"
        mock_comment.user = sample_user_data
        mock_comment.created_at = datetime(2023, 1, 1, 11, 0, 0)
        mock_comment.updated_at = datetime(2023, 1, 1, 11, 30, 0)
        mock_comment.html_url = (
            "https://github.com/owner/repo/issues/1#issuecomment-11111"
        )
        mock_comment.issue_url = "https://api.github.com/repos/owner/repo/issues/1"
        return mock_comment

    def test_init_creates_github_client(self):
        """Test that initialization creates a Github client."""
        with patch("src.github_client.Github") as mock_github:
            client = GitHubClient("test_token")
            mock_github.assert_called_once_with("test_token")
            assert client._github == mock_github.return_value

    def test_get_repository_labels(
        self, github_client, mock_github, mock_repo, sample_label_data
    ):
        """Test getting repository labels."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_labels = Mock(spec=PaginatedList)
        mock_labels.__iter__ = Mock(return_value=iter([sample_label_data]))
        mock_repo.get_labels.return_value = mock_labels

        # Execute
        result = github_client.get_repository_labels("owner/repo")

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_labels.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], Label)
        assert result[0].name == "bug"
        assert result[0].color == "ff0000"
        assert result[0].description == "Something isn't working"

    def test_get_repository_issues(
        self, github_client, mock_github, mock_repo, sample_issue_data
    ):
        """Test getting repository issues."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_issues = Mock(spec=PaginatedList)
        mock_issues.__iter__ = Mock(return_value=iter([sample_issue_data]))
        mock_repo.get_issues.return_value = mock_issues

        # Execute
        result = github_client.get_repository_issues("owner/repo")

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_issues.assert_called_once_with(state="all")
        assert len(result) == 1
        assert isinstance(result[0], Issue)
        assert result[0].title == "Test Issue"
        assert result[0].number == 1

    def test_get_issue_comments(
        self, github_client, mock_github, mock_repo, sample_comment_data
    ):
        """Test getting comments for a specific issue."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_issue = Mock(spec=PyGithubIssue)
        mock_repo.get_issue.return_value = mock_issue
        mock_comments = Mock(spec=PaginatedList)
        mock_comments.__iter__ = Mock(return_value=iter([sample_comment_data]))
        mock_issue.get_comments.return_value = mock_comments

        # Execute
        result = github_client.get_issue_comments("owner/repo", 1)

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_issue.assert_called_once_with(1)
        mock_issue.get_comments.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], Comment)
        assert result[0].body == "This is a test comment"

    def test_get_all_issue_comments(
        self,
        github_client,
        mock_github,
        mock_repo,
        sample_issue_data,
        sample_comment_data,
    ):
        """Test getting all comments from all issues."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_issues = Mock(spec=PaginatedList)
        mock_issues.__iter__ = Mock(return_value=iter([sample_issue_data]))
        mock_repo.get_issues.return_value = mock_issues

        # Mock the issue to have comments
        sample_issue_data.comments = 1
        mock_comments = Mock(spec=PaginatedList)
        mock_comments.__iter__ = Mock(return_value=iter([sample_comment_data]))
        sample_issue_data.get_comments.return_value = mock_comments

        # Execute
        result = github_client.get_all_issue_comments("owner/repo")

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_issues.assert_called_once_with(state="all")
        sample_issue_data.get_comments.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], Comment)

    def test_get_all_issue_comments_skips_issues_without_comments(
        self, github_client, mock_github, mock_repo, sample_issue_data
    ):
        """Test that issues without comments are skipped."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_issues = Mock(spec=PaginatedList)
        mock_issues.__iter__ = Mock(return_value=iter([sample_issue_data]))
        mock_repo.get_issues.return_value = mock_issues

        # Mock the issue to have no comments
        sample_issue_data.comments = 0

        # Execute
        result = github_client.get_all_issue_comments("owner/repo")

        # Verify
        assert len(result) == 0
        # get_comments should not be called for issues with no comments
        assert (
            not hasattr(sample_issue_data, "get_comments")
            or not sample_issue_data.get_comments.called
        )

    def test_create_label(
        self, github_client, mock_github, mock_repo, sample_label_data
    ):
        """Test creating a new label."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_label.return_value = sample_label_data

        # Create test label
        test_label = Label(
            name="feature",
            color="00ff00",
            description="New feature",
            url="https://api.github.com/repos/owner/repo/labels/feature",
            id=99999,
        )

        # Execute
        result = github_client.create_label("owner/repo", test_label)

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.create_label.assert_called_once_with(
            name="feature", color="00ff00", description="New feature"
        )
        assert isinstance(result, Label)
        assert result.name == "bug"  # Returns the mocked sample_label_data

    def test_create_label_with_none_description(
        self, github_client, mock_github, mock_repo, sample_label_data
    ):
        """Test creating a label with None description."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_label.return_value = sample_label_data

        # Create test label with None description
        test_label = Label(
            name="feature",
            color="00ff00",
            description=None,
            url="https://api.github.com/repos/owner/repo/labels/feature",
            id=99999,
        )

        # Execute
        github_client.create_label("owner/repo", test_label)

        # Verify description is converted to empty string
        mock_repo.create_label.assert_called_once_with(
            name="feature", color="00ff00", description=""
        )

    def test_create_issue(
        self,
        github_client,
        mock_github,
        mock_repo,
        sample_issue_data,
        sample_label_data,
    ):
        """Test creating a new issue."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_issue.return_value = sample_issue_data

        # Create test issue with labels
        test_user = GitHubUser(
            login="testuser",
            id=12345,
            avatar_url="https://github.com/avatar.png",
            html_url="https://github.com/testuser",
        )
        test_label = Label(
            name="bug",
            color="ff0000",
            description="Something isn't working",
            url="https://api.github.com/repos/owner/repo/labels/bug",
            id=54321,
        )
        test_issue = Issue(
            id=98765,
            number=1,
            title="New Test Issue",
            body="This is a new test issue",
            state="open",
            user=test_user,
            assignees=[],
            labels=[test_label],
            created_at=datetime(2023, 1, 1, 10, 0, 0),
            updated_at=datetime(2023, 1, 2, 10, 0, 0),
            closed_at=None,
            html_url="https://github.com/owner/repo/issues/1",
            comments=0,
        )

        # Execute
        result = github_client.create_issue("owner/repo", test_issue)

        # Verify
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.create_issue.assert_called_once_with(
            title="New Test Issue", body="This is a new test issue", labels=["bug"]
        )
        assert isinstance(result, Issue)

    def test_create_issue_with_none_body(
        self, github_client, mock_github, mock_repo, sample_issue_data
    ):
        """Test creating an issue with None body."""
        # Setup mocks
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_issue.return_value = sample_issue_data

        # Create test issue with None body
        test_user = GitHubUser(
            login="testuser",
            id=12345,
            avatar_url="https://github.com/avatar.png",
            html_url="https://github.com/testuser",
        )
        test_issue = Issue(
            id=98765,
            number=1,
            title="New Test Issue",
            body=None,
            state="open",
            user=test_user,
            assignees=[],
            labels=[],
            created_at=datetime(2023, 1, 1, 10, 0, 0),
            updated_at=datetime(2023, 1, 2, 10, 0, 0),
            closed_at=None,
            html_url="https://github.com/owner/repo/issues/1",
            comments=0,
        )

        # Execute
        github_client.create_issue("owner/repo", test_issue)

        # Verify body is converted to empty string
        mock_repo.create_issue.assert_called_once_with(
            title="New Test Issue", body="", labels=[]
        )

    def test_convert_user_to_model(self, github_client, sample_user_data):
        """Test converting PyGithub user to our model."""
        result = github_client._convert_user_to_model(sample_user_data)

        assert isinstance(result, GitHubUser)
        assert result.login == "testuser"
        assert result.id == 12345
        assert result.avatar_url == "https://github.com/avatar.png"
        assert result.html_url == "https://github.com/testuser"

    def test_convert_label_to_model(self, github_client, sample_label_data):
        """Test converting PyGithub label to our model."""
        result = github_client._convert_label_to_model(sample_label_data)

        assert isinstance(result, Label)
        assert result.name == "bug"
        assert result.color == "ff0000"
        assert result.description == "Something isn't working"
        assert result.url == "https://api.github.com/repos/owner/repo/labels/bug"
        assert result.id == 54321

    def test_convert_issue_to_model(self, github_client, sample_issue_data):
        """Test converting PyGithub issue to our model."""
        result = github_client._convert_issue_to_model(sample_issue_data)

        assert isinstance(result, Issue)
        assert result.id == 98765
        assert result.number == 1
        assert result.title == "Test Issue"
        assert result.body == "This is a test issue"
        assert result.state == "open"
        assert isinstance(result.user, GitHubUser)
        assert len(result.assignees) == 0
        assert len(result.labels) == 1
        assert isinstance(result.labels[0], Label)
        assert result.created_at == datetime(2023, 1, 1, 10, 0, 0)
        assert result.updated_at == datetime(2023, 1, 2, 10, 0, 0)
        assert result.closed_at is None
        assert result.html_url == "https://github.com/owner/repo/issues/1"
        assert result.comments_count == 2

    def test_convert_comment_to_model(self, github_client, sample_comment_data):
        """Test converting PyGithub comment to our model."""
        result = github_client._convert_comment_to_model(sample_comment_data)

        assert isinstance(result, Comment)
        assert result.id == 11111
        assert result.body == "This is a test comment"
        assert isinstance(result.user, GitHubUser)
        assert result.created_at == datetime(2023, 1, 1, 11, 0, 0)
        assert result.updated_at == datetime(2023, 1, 1, 11, 30, 0)
        assert (
            result.html_url
            == "https://github.com/owner/repo/issues/1#issuecomment-11111"
        )
        assert result.issue_url == "https://api.github.com/repos/owner/repo/issues/1"

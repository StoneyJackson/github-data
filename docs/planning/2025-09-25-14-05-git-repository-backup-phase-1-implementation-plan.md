# Git Repository Backup - Phase 1 Implementation Plan

**Date:** September 25, 2025  
**Author:** Claude Code Implementation Planning  
**Status:** Implementation Ready  
**Phase:** Phase 1 - Foundation (4-6 weeks)  

## Executive Summary

This document provides a detailed implementation plan for Phase 1 of the Git repository backup feature, as defined in the [Git Repository Backup Feature Analysis](2025-09-24-20-43-git-repository-backup-feature-analysis.md). Phase 1 establishes the foundation with basic Git mirror clone functionality, storage abstraction extensions, and container integration.

**Phase 1 Scope:**
- GitRepositoryService with mirror clone capability
- Enhanced storage abstraction for binary/filesystem data
- Container integration with Git tools
- Basic restore functionality
- Unit and integration testing framework
- Documentation updates

## Current System Architecture Analysis

### Existing Architecture Strengths

The current system provides an excellent foundation for Git repository backup:

1. **Strategy Pattern Architecture**: `SaveEntityStrategy` and `StrategyBasedSaveOrchestrator` provide extensible framework
2. **Dependency Injection**: Clean protocol-based interfaces in `src/github/protocols.py` and `src/storage/protocols.py`
3. **Service Layer**: Well-defined separation between GitHub API, storage, and business logic
4. **Container Support**: Existing Dockerfile and PDM-based dependency management
5. **Testing Framework**: Comprehensive test structure with unit, integration, and container tests

### Integration Points

Phase 1 will integrate seamlessly with existing architecture:
- **No Storage Changes**: Existing `StorageService` remains unchanged, handles JSON only
- **New Service Protocol**: Add `GitRepositoryService` protocol alongside existing `RepositoryService`
- **Strategy Extension**: Add `GitRepositoryStrategy` to existing save/restore strategies
- **Orchestrator Enhancement**: Extend orchestrators to coordinate Git operations via CLI
- **Filesystem Operations**: Git CLI handles all binary operations directly

## Phase 1 Detailed Implementation Plan

### 1. Simplified Architecture Approach

#### 1.1 No Storage Service Changes Required

The key insight is that **Git CLI handles all binary operations**, eliminating the need for storage service modifications:

- **Existing `StorageService`**: Continues handling JSON data unchanged
- **Git Operations**: Performed directly via subprocess calls to Git CLI
- **File Management**: Git manages its own binary formats (.git directories, bundles)
- **Directory Operations**: Simple Python `pathlib` operations for basic directory management

This approach significantly simplifies the implementation while maintaining clean separation of concerns.

#### 1.2 Directory Operations via Pathlib

Simple filesystem operations are handled directly in the Git strategies using Python's built-in `pathlib`:

```python
# Create directories
git_data_dir = Path(output_path) / "git-data"
git_data_dir.mkdir(parents=True, exist_ok=True)

# Check directory existence
if git_data_dir.exists():
    # Process Git repositories

# Directory size calculation (when needed)
def get_directory_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
```

No storage service modifications required.

### 2. Git Repository Service (Core Implementation)

#### 2.1 Git Repository Models and Enums

**File:** `src/entities/git_repositories/__init__.py` (new directory)
**File:** `src/entities/git_repositories/models.py` (new file)

```python
"""Git repository data models and enums."""

from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

class GitBackupFormat(Enum):
    """Git backup format options."""
    MIRROR = "mirror"
    BUNDLE = "bundle"
    BOTH = "both"

class GitAuthMethod(Enum):
    """Git authentication method options."""
    TOKEN = "token"
    SSH = "ssh"

@dataclass
class GitRepositoryInfo:
    """Git repository information model."""
    repo_name: str
    repo_url: str
    backup_format: GitBackupFormat
    size_bytes: Optional[int] = None
    commit_count: Optional[int] = None
    branch_count: Optional[int] = None
    tag_count: Optional[int] = None
    
@dataclass
class GitOperationResult:
    """Result of a Git operation."""
    success: bool
    backup_format: str
    destination: Optional[str] = None
    size_bytes: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

#### 2.2 Git Repository Protocol

**File:** `src/git/__init__.py` (new directory)
**File:** `src/git/protocols.py` (new file)

```python
"""Abstract protocols for Git repository operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from src.entities.git_repositories.models import GitBackupFormat, GitOperationResult, GitRepositoryInfo

class GitRepositoryService(ABC):
    """Abstract interface for Git repository operations."""
    
    @abstractmethod
    def clone_repository(
        self, 
        repo_url: str, 
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Clone repository to destination path."""
        pass
    
    @abstractmethod
    def update_repository(
        self, 
        repo_path: Path, 
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Update existing repository backup."""
        pass
    
    @abstractmethod
    def validate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository integrity."""
        pass
    
    @abstractmethod
    def get_repository_info(self, repo_path: Path) -> GitRepositoryInfo:
        """Get repository metadata and statistics."""
        pass
    
    @abstractmethod
    def restore_repository(
        self, 
        backup_path: Path, 
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> GitOperationResult:
        """Restore repository from backup."""
        pass

class GitCommandExecutor(ABC):
    """Abstract interface for low-level Git command execution."""
    
    @abstractmethod
    def execute_clone_mirror(self, repo_url: str, destination: Path) -> Dict[str, Any]:
        """Execute git clone --mirror command."""
        pass
        
    @abstractmethod
    def execute_clone_bundle(self, repo_url: str, bundle_path: Path) -> Dict[str, Any]:
        """Execute git bundle create command."""
        pass
        
    @abstractmethod
    def execute_remote_update(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git remote update command."""
        pass
        
    @abstractmethod
    def execute_fsck(self, repo_path: Path) -> Dict[str, Any]:
        """Execute git fsck command."""
        pass
        
    @abstractmethod
    def get_repository_stats(self, repo_path: Path) -> Dict[str, Any]:
        """Get repository statistics via Git commands."""
        pass
```

#### 2.2 Git Repository Service Implementation

**File:** `src/git/service.py` (new file)

```python
"""Git repository service implementation."""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from .protocols import GitRepositoryService, GitCommandExecutor
from .command_executor import GitCommandExecutorImpl
from src.entities.git_repositories.models import GitBackupFormat, GitOperationResult, GitRepositoryInfo

class GitRepositoryServiceImpl(GitRepositoryService):
    """High-level Git repository operations orchestration."""
    
    def __init__(self, command_executor: GitCommandExecutor = None, auth_token: str = None):
        self._command_executor = command_executor or GitCommandExecutorImpl(auth_token)
    
    def clone_repository(
        self, 
        repo_url: str, 
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> Dict[str, Any]:
        """Clone repository to destination path."""
        try:
            # Ensure destination parent exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare authenticated URL if token provided
            auth_url = self._prepare_authenticated_url(repo_url)
            
            if backup_format == GitBackupFormat.MIRROR:
                return self._clone_mirror(auth_url, destination)
            elif backup_format == GitBackupFormat.BUNDLE:
                return self._create_bundle(auth_url, destination)
            elif backup_format == GitBackupFormat.BOTH:
                # Create both mirror and bundle
                mirror_result = self._clone_mirror(auth_url, destination)
                bundle_path = destination.with_suffix('.bundle')
                bundle_result = self._create_bundle(auth_url, bundle_path)
                
                return {
                    "success": True,
                    "backup_format": backup_format.value,
                    "mirror": mirror_result,
                    "bundle": bundle_result
                }
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_format": backup_format.value
            }
    
    def _clone_mirror(self, repo_url: str, destination: Path) -> Dict[str, Any]:
        """Create mirror clone of repository."""
        cmd = ["git", "clone", "--mirror", repo_url, str(destination)]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=self._git_timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")
        
        # Get repository statistics
        repo_info = self._get_mirror_info(destination)
        
        return {
            "success": True,
            "method": "mirror",
            "destination": str(destination),
            "size_bytes": self._get_directory_size(destination),
            **repo_info
        }
    
    def _create_bundle(self, repo_url: str, bundle_path: Path) -> Dict[str, Any]:
        """Create bundle backup of repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_clone = Path(temp_dir) / "temp_clone"
            
            # First clone the repository
            clone_cmd = ["git", "clone", repo_url, str(temp_clone)]
            result = subprocess.run(
                clone_cmd, 
                capture_output=True, 
                text=True, 
                timeout=self._git_timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone for bundle failed: {result.stderr}")
            
            # Create bundle
            bundle_cmd = [
                "git", "-C", str(temp_clone), 
                "bundle", "create", str(bundle_path), "--all"
            ]
            
            result = subprocess.run(
                bundle_cmd,
                capture_output=True,
                text=True,
                timeout=self._git_timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git bundle failed: {result.stderr}")
        
        return {
            "success": True,
            "method": "bundle",
            "destination": str(bundle_path),
            "size_bytes": bundle_path.stat().st_size
        }
    
    def update_repository(
        self, 
        repo_path: Path, 
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> Dict[str, Any]:
        """Update existing repository backup."""
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository backup not found: {repo_path}")
        
        try:
            if backup_format == GitBackupFormat.MIRROR:
                return self._update_mirror(repo_path)
            elif backup_format == GitBackupFormat.BUNDLE:
                # For bundles, we need to recreate from original URL
                # This would require storing metadata about original URL
                raise NotImplementedError("Bundle updates require original URL")
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_format": backup_format.value
            }
    
    def _update_mirror(self, mirror_path: Path) -> Dict[str, Any]:
        """Update mirror clone."""
        cmd = ["git", "-C", str(mirror_path), "remote", "update"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self._git_timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Git mirror update failed: {result.stderr}")
        
        repo_info = self._get_mirror_info(mirror_path)
        
        return {
            "success": True,
            "method": "mirror_update",
            "path": str(mirror_path),
            "size_bytes": self._get_directory_size(mirror_path),
            **repo_info
        }
    
    def validate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository integrity."""
        try:
            if not repo_path.exists():
                return {"valid": False, "error": "Repository path does not exist"}
            
            if repo_path.suffix == '.bundle':
                return self._validate_bundle(repo_path)
            else:
                return self._validate_mirror(repo_path)
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _validate_mirror(self, mirror_path: Path) -> Dict[str, Any]:
        """Validate mirror repository."""
        # Check if it's a valid git repository
        cmd = ["git", "-C", str(mirror_path), "rev-parse", "--git-dir"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"valid": False, "error": "Not a valid git repository"}
        
        # Run git fsck for integrity check
        fsck_cmd = ["git", "-C", str(mirror_path), "fsck", "--full"]
        
        fsck_result = subprocess.run(
            fsck_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "valid": fsck_result.returncode == 0,
            "fsck_output": fsck_result.stdout if fsck_result.returncode == 0 else fsck_result.stderr
        }
    
    def _validate_bundle(self, bundle_path: Path) -> Dict[str, Any]:
        """Validate bundle file."""
        cmd = ["git", "bundle", "verify", str(bundle_path)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "valid": result.returncode == 0,
            "verify_output": result.stdout if result.returncode == 0 else result.stderr
        }
    
    def get_repository_info(self, repo_path: Path) -> Dict[str, Any]:
        """Get repository metadata and statistics."""
        if repo_path.suffix == '.bundle':
            return self._get_bundle_info(repo_path)
        else:
            return self._get_mirror_info(repo_path)
    
    def _get_mirror_info(self, mirror_path: Path) -> Dict[str, Any]:
        """Get mirror repository information."""
        info = {}
        
        try:
            # Get commit count
            count_cmd = ["git", "-C", str(mirror_path), "rev-list", "--all", "--count"]
            count_result = subprocess.run(count_cmd, capture_output=True, text=True, timeout=30)
            if count_result.returncode == 0:
                info["commit_count"] = int(count_result.stdout.strip())
            
            # Get branch count
            branch_cmd = ["git", "-C", str(mirror_path), "branch", "-r"]
            branch_result = subprocess.run(branch_cmd, capture_output=True, text=True, timeout=30)
            if branch_result.returncode == 0:
                info["branch_count"] = len(branch_result.stdout.strip().split('\n'))
            
            # Get tag count
            tag_cmd = ["git", "-C", str(mirror_path), "tag"]
            tag_result = subprocess.run(tag_cmd, capture_output=True, text=True, timeout=30)
            if tag_result.returncode == 0:
                tags = tag_result.stdout.strip()
                info["tag_count"] = len(tags.split('\n')) if tags else 0
            
        except Exception as e:
            info["info_error"] = str(e)
        
        return info
    
    def _get_bundle_info(self, bundle_path: Path) -> Dict[str, Any]:
        """Get bundle file information."""
        return {
            "file_size": bundle_path.stat().st_size,
            "is_bundle": True
        }
    
    def restore_repository(
        self, 
        backup_path: Path, 
        destination: Path,
        backup_format: GitBackupFormat = GitBackupFormat.MIRROR
    ) -> Dict[str, Any]:
        """Restore repository from backup."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            if backup_format == GitBackupFormat.MIRROR:
                return self._restore_from_mirror(backup_path, destination)
            elif backup_format == GitBackupFormat.BUNDLE:
                return self._restore_from_bundle(backup_path, destination)
            else:
                raise ValueError(f"Unsupported backup format: {backup_format}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_format": backup_format.value
            }
    
    def _restore_from_mirror(self, mirror_path: Path, destination: Path) -> Dict[str, Any]:
        """Restore from mirror backup."""
        # Clone from local mirror
        cmd = ["git", "clone", str(mirror_path), str(destination)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self._git_timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Git restore from mirror failed: {result.stderr}")
        
        return {
            "success": True,
            "method": "restore_from_mirror",
            "destination": str(destination),
            "size_bytes": self._get_directory_size(destination)
        }
    
    def _restore_from_bundle(self, bundle_path: Path, destination: Path) -> Dict[str, Any]:
        """Restore from bundle backup."""
        # Initialize new repository
        init_cmd = ["git", "init", str(destination)]
        init_result = subprocess.run(init_cmd, capture_output=True, text=True, timeout=30)
        
        if init_result.returncode != 0:
            raise RuntimeError(f"Git init failed: {init_result.stderr}")
        
        # Pull from bundle
        pull_cmd = ["git", "-C", str(destination), "pull", str(bundle_path), "main"]
        pull_result = subprocess.run(
            pull_cmd,
            capture_output=True,
            text=True,
            timeout=self._git_timeout
        )
        
        if pull_result.returncode != 0:
            raise RuntimeError(f"Git restore from bundle failed: {pull_result.stderr}")
        
        return {
            "success": True,
            "method": "restore_from_bundle",
            "destination": str(destination),
            "size_bytes": self._get_directory_size(destination)
        }
    
    def _prepare_authenticated_url(self, repo_url: str) -> str:
        """Prepare repository URL with authentication if token provided."""
        if not self._auth_token:
            return repo_url
        
        # Handle GitHub URLs
        if "github.com" in repo_url:
            if repo_url.startswith("https://"):
                return repo_url.replace("https://", f"https://{self._auth_token}@")
            elif repo_url.startswith("git@"):
                # Convert SSH to HTTPS with token
                repo_path = repo_url.replace("git@github.com:", "")
                return f"https://{self._auth_token}@github.com/{repo_path}"
        
        return repo_url
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    continue
        return total_size
```

### 3. Strategy Integration

#### 3.1 Git Repository Strategy

**File:** `src/operations/save/strategies/git_repository_strategy.py` (new file)

```python
"""Git repository save strategy."""

from pathlib import Path
from typing import List, Dict, Any
from ..strategy import SaveEntityStrategy
from src.git.protocols import GitRepositoryService
from src.entities.git_repositories.models import GitBackupFormat
from src.storage.protocols import StorageService

class GitRepositoryStrategy(SaveEntityStrategy):
    """Strategy for saving Git repository data."""
    
    def __init__(self, git_service: GitRepositoryService, backup_format: GitBackupFormat = GitBackupFormat.MIRROR):
        self._git_service = git_service
        self._backup_format = backup_format
    
    def get_entity_name(self) -> str:
        """Return entity name for this strategy."""
        return "git_repository"
    
    def get_dependencies(self) -> List[str]:
        """Return list of entity dependencies."""
        return []  # Git repository has no dependencies
    
    def collect_data(self, github_service: Any, repo_name: str) -> List[Dict[str, Any]]:
        """Collect Git repository data."""
        # For Git repositories, we don't collect data through GitHub API
        # Instead, we prepare repository URL
        repo_url = f"https://github.com/{repo_name}.git"
        
        return [{
            "repo_name": repo_name,
            "repo_url": repo_url,
            "backup_format": self._backup_format.value
        }]
    
    def process_data(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Git repository data."""
        # No processing needed for Git repositories
        return entities
    
    def save_data(self, entities: List[Dict[str, Any]], output_path: str, storage_service: StorageService) -> Dict[str, Any]:
        """Save Git repository data."""
        if not entities:
            return {"saved_repositories": 0}
        
        results = []
        
        for entity in entities:
            repo_name = entity["repo_name"]
            repo_url = entity["repo_url"]
            
            # Create Git data directory using simple filesystem operations
            git_data_dir = Path(output_path) / "git-data"
            git_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine backup destination
            if self._backup_format == GitBackupFormat.BUNDLE:
                backup_path = git_data_dir / f"{repo_name.replace('/', '_')}.bundle"
            else:
                backup_path = git_data_dir / repo_name.replace('/', '_')
            
            # Perform Git backup
            result = self._git_service.clone_repository(
                repo_url,
                backup_path,
                self._backup_format
            )
            
            results.append({
                "repo_name": repo_name,
                "backup_path": str(backup_path),
                **result
            })
        
        successful_backups = sum(1 for r in results if r.get("success", False))
        
        return {
            "saved_repositories": successful_backups,
            "total_repositories": len(entities),
            "results": results
        }
```

#### 3.2 Git Repository Restore Strategy

**File:** `src/operations/restore/strategies/git_repository_strategy.py` (new file)

```python
"""Git repository restore strategy."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from ..strategy import RestoreEntityStrategy
from src.git.protocols import GitRepositoryService
from src.entities.git_repositories.models import GitBackupFormat
from src.storage.protocols import StorageService

class GitRepositoryRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring Git repository data."""
    
    def __init__(self, git_service: GitRepositoryService):
        self._git_service = git_service
    
    def get_entity_name(self) -> str:
        """Return entity name for this strategy."""
        return "git_repository"
    
    def get_dependencies(self) -> List[str]:
        """Return list of entity dependencies."""
        return []  # Git repository has no dependencies
    
    def load_data(self, input_path: str, storage_service: StorageService) -> List[Dict[str, Any]]:
        """Load Git repository backup data."""
        git_data_dir = Path(input_path) / "git-data"
        
        if not git_data_dir.exists():
            return []
        
        repositories = []
        
        # Find all Git repositories (directories and bundle files)
        for item in git_data_dir.iterdir():
            if item.is_dir():
                repositories.append({
                    "backup_path": str(item),
                    "backup_format": GitBackupFormat.MIRROR.value,
                    "repo_name": item.name.replace('_', '/')
                })
            elif item.suffix == '.bundle':
                repo_name = item.stem.replace('_', '/')
                repositories.append({
                    "backup_path": str(item),
                    "backup_format": GitBackupFormat.BUNDLE.value,
                    "repo_name": repo_name
                })
        
        return repositories
    
    def process_data(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Git repository restoration data."""
        # No processing needed for Git repositories
        return entities
    
    def restore_data(self, entities: List[Dict[str, Any]], destination_path: str) -> Dict[str, Any]:
        """Restore Git repository data."""
        if not entities:
            return {"restored_repositories": 0}
        
        results = []
        
        for entity in entities:
            backup_path = Path(entity["backup_path"])
            repo_name = entity["repo_name"]
            backup_format = GitBackupFormat(entity["backup_format"])
            
            # Create restore destination
            restore_path = Path(destination_path) / "restored-repositories" / repo_name.replace('/', '_')
            
            # Perform Git restore
            result = self._git_service.restore_repository(
                backup_path,
                restore_path,
                backup_format
            )
            
            results.append({
                "repo_name": repo_name,
                "restore_path": str(restore_path),
                **result
            })
        
        successful_restores = sum(1 for r in results if r.get("success", False))
        
        return {
            "restored_repositories": successful_restores,
            "total_repositories": len(entities),
            "results": results
        }
```

### 4. Container Integration

#### 4.1 Enhanced Dockerfile

**File:** `Dockerfile` (modify existing)

```dockerfile
FROM python:3.11-slim

# Install system dependencies including Git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy PDM files and README first for better caching
COPY pyproject.toml pdm.lock* README.md ./

# Install dependencies
RUN pdm install --prod --no-editable

# Copy source code
COPY src/ ./src/

# Create data directory for volume mounting
RUN mkdir -p /data

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_PATH=/data

# Git-specific environment variables with defaults
ENV INCLUDE_GIT_REPO=true
ENV GIT_BACKUP_FORMAT=mirror
ENV GIT_AUTH_METHOD=token

# Run the application using PDM
CMD ["pdm", "run", "python", "-m", "src.main"]
```

#### 4.2 Enhanced Main Entry Point

**File:** `src/main.py` (modify existing)

```python
"""Enhanced main entry point with Git repository support."""

import os
import sys
from pathlib import Path
from src.git.service import GitRepositoryServiceImpl
from src.entities.git_repositories.models import GitBackupFormat, GitAuthMethod
from src.operations.save.strategies.git_repository_strategy import GitRepositoryStrategy
from src.operations.restore.strategies.git_repository_strategy import GitRepositoryRestoreStrategy

# Existing imports...

def create_git_repository_service(config: Dict[str, str]) -> GitRepositoryServiceImpl:
    """Create Git repository service with configuration."""
    auth_token = config.get("GITHUB_TOKEN")
    return GitRepositoryServiceImpl(auth_token=auth_token)

def register_git_strategies(save_orchestrator, restore_orchestrator, git_service, config):
    """Register Git repository strategies if enabled."""
    include_git_repo = config.get("INCLUDE_GIT_REPO", "true").lower() == "true"
    
    if include_git_repo:
        # Parse backup format
        backup_format_str = config.get("GIT_BACKUP_FORMAT", "mirror").lower()
        try:
            backup_format = GitBackupFormat(backup_format_str)
        except ValueError:
            print(f"Invalid Git backup format: {backup_format_str}, using mirror")
            backup_format = GitBackupFormat.MIRROR
        
        # Register save strategy
        git_save_strategy = GitRepositoryStrategy(git_service, backup_format)
        save_orchestrator.register_strategy(git_save_strategy)
        
        # Register restore strategy  
        git_restore_strategy = GitRepositoryRestoreStrategy(git_service)
        restore_orchestrator.register_strategy(git_restore_strategy)
        
        print(f"Git repository backup enabled with format: {backup_format.value}")

def main() -> None:
    """Enhanced main function with Git support."""
    config = get_environment_config()
    
    # Create services
    github_service = create_github_service(config)
    storage_service = create_storage_service(config)
    git_service = create_git_repository_service(config)
    
    # Create orchestrators
    save_orchestrator = create_save_orchestrator(github_service, storage_service)
    restore_orchestrator = create_restore_orchestrator(github_service, storage_service)
    
    # Register existing strategies
    register_existing_strategies(save_orchestrator, restore_orchestrator)
    
    # Register Git strategies
    register_git_strategies(save_orchestrator, restore_orchestrator, git_service, config)
    
    # Continue with existing main logic...
    operation = config.get("OPERATION", "save").lower()
    
    if operation == "save":
        execute_save_operation(save_orchestrator, config)
    elif operation == "restore":
        execute_restore_operation(restore_orchestrator, config)
    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)

# Existing functions remain unchanged...
```

### 5. Testing Strategy

#### 5.1 Unit Tests

**File:** `tests/unit/test_git_repository_service_unit.py` (new file)

```python
"""Unit tests for Git repository service."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.git.service import GitRepositoryServiceImpl
from src.git.command_executor import GitCommandExecutorImpl
from src.entities.git_repositories.models import GitBackupFormat, GitOperationResult
from tests.shared import temp_data_dir

# Test markers following project standards
pytestmark = [pytest.mark.unit, pytest.mark.fast]

class TestGitRepositoryService:
    """Test suite for Git repository service."""
    
    @pytest.fixture
    def mock_command_executor(self):
        """Create mock command executor."""
        return Mock(spec=GitCommandExecutorImpl)
    
    @pytest.fixture
    def git_service(self, mock_command_executor):
        """Create Git repository service instance with mocked executor."""
        return GitRepositoryServiceImpl(command_executor=mock_command_executor)
    
    def test_clone_repository_success_mirror(self, git_service, mock_command_executor, temp_data_dir):
        """Test successful mirror repository clone."""
        # Arrange
        repo_url = "https://github.com/test/repo.git"
        destination = Path(temp_data_dir) / "test_repo"
        expected_result = {
            "success": True,
            "method": "mirror",
            "destination": str(destination),
            "size_bytes": 1024
        }
        mock_command_executor.execute_clone_mirror.return_value = expected_result
        
        # Act
        result = git_service.clone_repository(repo_url, destination, GitBackupFormat.MIRROR)
        
        # Assert
        assert result.success is True
        assert result.backup_format == "mirror"
        assert result.destination == str(destination)
        mock_command_executor.execute_clone_mirror.assert_called_once_with(repo_url, destination)
    
    def test_clone_repository_failure_returns_error_result(self, git_service, mock_command_executor, temp_data_dir):
        """Test clone repository failure handling."""
        # Arrange
        repo_url = "https://github.com/test/repo.git"
        destination = Path(temp_data_dir) / "test_repo"
        mock_command_executor.execute_clone_mirror.side_effect = RuntimeError("Clone failed")
        
        # Act
        result = git_service.clone_repository(repo_url, destination, GitBackupFormat.MIRROR)
        
        # Assert
        assert result.success is False
        assert "Clone failed" in result.error
        assert result.backup_format == "mirror"
    
    def test_validate_repository_delegates_to_executor(self, git_service, mock_command_executor, temp_data_dir):
        """Test repository validation delegates to command executor."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"
        repo_path.mkdir()
        expected_validation = {"valid": True, "fsck_output": "ok"}
        mock_command_executor.execute_fsck.return_value = expected_validation
        
        # Act
        result = git_service.validate_repository(repo_path)
        
        # Assert
        assert result == expected_validation
        mock_command_executor.execute_fsck.assert_called_once_with(repo_path)
    
    def test_validate_repository_nonexistent_path(self, git_service, mock_command_executor, temp_data_dir):
        """Test validation of nonexistent repository path."""
        # Arrange
        nonexistent_path = Path(temp_data_dir) / "nonexistent"
        
        # Act
        result = git_service.validate_repository(nonexistent_path)
        
        # Assert
        assert result["valid"] is False
        assert "does not exist" in result["error"]
    
    def test_update_repository_mirror_format(self, git_service, mock_command_executor, temp_data_dir):
        """Test updating mirror repository."""
        # Arrange
        repo_path = Path(temp_data_dir) / "test_repo.git"
        repo_path.mkdir()
        
        update_result = {"success": True, "method": "remote_update", "path": str(repo_path)}
        stats_result = {"commit_count": 150, "branch_count": 5}
        
        mock_command_executor.execute_remote_update.return_value = update_result
        mock_command_executor.get_repository_stats.return_value = stats_result
        
        # Act
        result = git_service.update_repository(repo_path, GitBackupFormat.MIRROR)
        
        # Assert
        assert result.success is True
        assert result.backup_format == "mirror"
        assert result.metadata == stats_result
        mock_command_executor.execute_remote_update.assert_called_once_with(repo_path)
        mock_command_executor.get_repository_stats.assert_called_once_with(repo_path)

class TestGitCommandExecutor:
    """Test suite for Git command executor."""
    
    @pytest.fixture
    def git_executor(self):
        """Create Git command executor instance."""
        return GitCommandExecutorImpl(auth_token="test_token")
    
    @patch('src.git.command_executor.subprocess.run')
    def test_execute_clone_mirror_success(self, mock_subprocess, git_executor, temp_data_dir):
        """Test successful git clone --mirror execution."""
        # Arrange
        destination = Path(temp_data_dir) / "test_repo.git"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Act
        with patch.object(git_executor, '_get_directory_size', return_value=2048):
            result = git_executor.execute_clone_mirror(
                "https://github.com/test/repo.git", 
                destination
            )
        
        # Assert
        assert result["success"] is True
        assert result["method"] == "mirror"
        assert result["destination"] == str(destination)
        assert result["size_bytes"] == 2048
        mock_subprocess.assert_called_once()
    
    @patch('src.git.command_executor.subprocess.run')
    def test_execute_clone_mirror_failure(self, mock_subprocess, git_executor, temp_data_dir):
        """Test git clone --mirror execution failure."""
        # Arrange
        destination = Path(temp_data_dir) / "test_repo.git"
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Authentication failed"
        mock_subprocess.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Git clone failed"):
            git_executor.execute_clone_mirror(
                "https://github.com/test/repo.git", 
                destination
            )
    
    def test_prepare_authenticated_url_https(self, git_executor):
        """Test HTTPS URL authentication preparation."""
        original_url = "https://github.com/test/repo.git"
        auth_url = git_executor._prepare_authenticated_url(original_url)
        
        assert auth_url == "https://test_token@github.com/test/repo.git"
    
    def test_prepare_authenticated_url_ssh_conversion(self, git_executor):
        """Test SSH URL conversion to authenticated HTTPS."""
        ssh_url = "git@github.com:test/repo.git"
        auth_url = git_executor._prepare_authenticated_url(ssh_url)
        
        assert auth_url == "https://test_token@github.com/test/repo.git"
    
    def test_prepare_authenticated_url_no_token(self):
        """Test URL preparation without authentication token."""
        executor = GitCommandExecutorImpl(auth_token=None)
        original_url = "https://github.com/test/repo.git"
        auth_url = executor._prepare_authenticated_url(original_url)
        
        assert auth_url == original_url
```

#### 5.2 Integration Tests

**File:** `tests/integration/test_git_repository_integration.py` (new file)

```python
"""Integration tests for Git repository operations."""

import pytest
from pathlib import Path
from unittest.mock import patch
from src.git.service import GitRepositoryServiceImpl
from src.entities.git_repositories.models import GitBackupFormat
from src.operations.save.strategies.git_repository_strategy import GitRepositoryStrategy
from tests.shared import (
    temp_data_dir, 
    storage_service_mock, 
    sample_github_data,
    github_service_with_mock
)

# Test markers following project standards
pytestmark = [pytest.mark.integration, pytest.mark.medium, pytest.mark.github_api]

class TestGitRepositoryIntegration:
    """Integration test suite for Git repository operations."""
    
    @pytest.fixture
    def git_service(self):
        """Create Git repository service."""
        return GitRepositoryServiceImpl()
    
    @pytest.fixture
    def git_strategy(self, git_service):
        """Create Git repository strategy."""
        return GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-git-integration", default=False),
        reason="Git integration tests require --run-git-integration flag"
    )
    @pytest.mark.slow
    @pytest.mark.github_api
    def test_public_repository_clone_real(self, git_service, temp_data_dir):
        """Test cloning public repository from GitHub."""
        destination = Path(temp_data_dir) / "test_repo"
        
        result = git_service.clone_repository(
            "https://github.com/octocat/Hello-World.git",
            destination,
            GitBackupFormat.MIRROR
        )
        
        assert result.success is True
        assert destination.exists()
        assert (destination / "HEAD").exists()
    
    def test_git_strategy_collect_data_structure(self, git_strategy):
        """Test Git strategy data collection creates proper structure."""
        entities = git_strategy.collect_data(None, "test/repo")
        
        assert len(entities) == 1
        entity = entities[0]
        assert entity["repo_name"] == "test/repo"
        assert entity["repo_url"] == "https://github.com/test/repo.git"
        assert entity["backup_format"] == GitBackupFormat.MIRROR.value
    
    def test_git_strategy_save_data_integration(
        self, 
        git_strategy, 
        storage_service_mock, 
        temp_data_dir
    ):
        """Test Git strategy save data with mocked Git operations."""
        entities = [{
            "repo_name": "test/repo",
            "repo_url": "https://github.com/test/repo.git",
            "backup_format": GitBackupFormat.MIRROR.value
        }]
        
        # Mock the git service to avoid actual cloning
        with patch.object(git_strategy._git_service, 'clone_repository') as mock_clone:
            mock_result = GitOperationResult(
                success=True,
                backup_format="mirror",
                destination=str(Path(temp_data_dir) / "git-data" / "test_repo"),
                size_bytes=1024
            )
            mock_clone.return_value = mock_result
            
            result = git_strategy.save_data(entities, temp_data_dir, storage_service_mock)
        
        assert result["total_repositories"] == 1
        assert result["saved_repositories"] == 1
        assert (Path(temp_data_dir) / "git-data").exists()
        mock_clone.assert_called_once()
    
    def test_git_service_and_strategy_integration(
        self, 
        git_service, 
        storage_service_mock, 
        temp_data_dir
    ):
        """Test integration between GitRepositoryService and GitRepositoryStrategy."""
        strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)
        
        # Mock the command executor to avoid actual Git operations
        with patch.object(git_service._command_executor, 'execute_clone_mirror') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "method": "mirror",
                "destination": str(Path(temp_data_dir) / "git-data" / "test_repo"),
                "size_bytes": 2048
            }
            
            entities = strategy.collect_data(None, "test/repo")
            result = strategy.save_data(entities, temp_data_dir, storage_service_mock)
            
            assert result["saved_repositories"] == 1
            mock_execute.assert_called_once()

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.storage
class TestGitRepositoryStorageIntegration:
    """Integration tests for Git repository storage operations."""
    
    def test_git_data_directory_creation(self, temp_data_dir, storage_service_mock):
        """Test that git-data directory is created properly."""
        git_service = GitRepositoryServiceImpl()
        strategy = GitRepositoryStrategy(git_service, GitBackupFormat.MIRROR)
        
        entities = [{
            "repo_name": "test/repo",
            "repo_url": "https://github.com/test/repo.git",
            "backup_format": GitBackupFormat.MIRROR.value
        }]
        
        with patch.object(git_service._command_executor, 'execute_clone_mirror') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "method": "mirror", 
                "destination": str(Path(temp_data_dir) / "git-data" / "test_repo"),
                "size_bytes": 512
            }
            
            strategy.save_data(entities, temp_data_dir, storage_service_mock)
            
            git_data_dir = Path(temp_data_dir) / "git-data"
            assert git_data_dir.exists()
            assert git_data_dir.is_dir()
```

#### 5.3 Container Tests

**File:** `tests/container/test_git_container.py` (new file)

```python
"""Container tests for Git repository functionality."""

import pytest
from tests.shared.helpers import ContainerTestHelper

# Test markers following project standards  
pytestmark = [
    pytest.mark.container, 
    pytest.mark.integration, 
    pytest.mark.docker, 
    pytest.mark.slow
]

class TestGitRepositoryContainer:
    """Container test suite for Git repository operations."""
    
    @pytest.fixture
    def container_helper(self):
        """Create container test helper following project pattern."""
        return ContainerTestHelper()
    
    def test_container_git_installation(self, container_helper):
        """Test that container has Git installed and accessible."""
        result = container_helper.run_command_in_container(["git", "--version"])
        
        assert result.returncode == 0
        output = result.stdout.decode()
        assert "git version" in output
        # Verify it's a recent Git version (2.x)
        assert "git version 2." in output
    
    def test_git_backup_environment_variables(self, container_helper):
        """Test Git-related environment variables are properly set."""
        env_vars = {
            "INCLUDE_GIT_REPO": "true",
            "GIT_BACKUP_FORMAT": "mirror",
            "GIT_AUTH_METHOD": "token",
            "GITHUB_TOKEN": "test_token_value"
        }
        
        # Test each environment variable
        for env_var, expected_value in env_vars.items():
            result = container_helper.run_container_with_env(
                {env_var: expected_value},
                ["python", "-c", f"import os; print(os.environ.get('{env_var}', 'NOT_SET'))"]
            )
            
            assert result.returncode == 0
            output = result.stdout.decode().strip()
            assert output == expected_value
    
    def test_container_git_configuration_defaults(self, container_helper):
        """Test that container has proper Git configuration defaults."""
        # Test Git config access
        result = container_helper.run_command_in_container([
            "git", "config", "--global", "--get-regexp", ".*"
        ])
        
        # Git config should be accessible (even if empty, should not error)
        assert result.returncode in [0, 1]  # 1 is OK for empty config
    
    def test_container_python_git_access(self, container_helper):
        """Test that Python can execute Git commands within container."""
        python_script = '''
import subprocess
import sys

try:
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    print(f"returncode: {result.returncode}")
    print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    sys.exit(result.returncode)
except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
'''
        
        result = container_helper.run_command_in_container([
            "python", "-c", python_script
        ])
        
        assert result.returncode == 0
        output = result.stdout.decode()
        assert "returncode: 0" in output
        assert "git version" in output
    
    @pytest.mark.performance
    def test_container_startup_performance(self, container_helper):
        """Test that container starts within acceptable time limits."""
        import time
        
        start_time = time.time()
        
        # Simple command to test startup time
        result = container_helper.run_command_in_container(["echo", "startup_test"])
        
        startup_time = time.time() - start_time
        
        assert result.returncode == 0
        assert "startup_test" in result.stdout.decode()
        # Container should start within 30 seconds
        assert startup_time < 30.0

class TestGitContainerIntegration:
    """Container integration tests for complete Git workflows."""
    
    @pytest.fixture
    def container_helper(self):
        """Create container test helper."""
        return ContainerTestHelper()
    
    def test_container_git_directory_operations(self, container_helper):
        """Test Git directory operations within container."""
        commands = [
            "mkdir -p /tmp/git-test",
            "cd /tmp/git-test && git init",
            "cd /tmp/git-test && echo 'test' > README.md", 
            "cd /tmp/git-test && git add README.md",
            "cd /tmp/git-test && git -c user.name='Test' -c user.email='test@example.com' commit -m 'Initial commit'",
            "ls -la /tmp/git-test/.git"
        ]
        
        for cmd in commands:
            result = container_helper.run_command_in_container(["bash", "-c", cmd])
            assert result.returncode == 0, f"Command failed: {cmd}"
    
    def test_container_volume_mount_git_operations(self, container_helper):
        """Test Git operations with volume mounts work correctly."""
        # This test would verify that Git operations work with mounted volumes
        # Implementation depends on ContainerTestHelper volume mounting capabilities
        
        result = container_helper.run_command_in_container([
            "bash", "-c", 
            "mkdir -p /data/git-test && cd /data/git-test && git init && echo 'Volume mount test' > test.txt"
        ])
        
        assert result.returncode == 0
```

### 6. Documentation Updates

#### 6.1 README Updates

**File:** `README.md` (add Git repository section)

```markdown
## Git Repository Backup (Phase 1)

### Overview

The Git repository backup feature extends the GitHub Data project to include complete Git repository data (commits, branches, tags, and file history) alongside existing metadata backup capabilities.

### Features

- **Complete Repository Cloning**: Full commit history, branches, and tags
- **Multiple Backup Formats**: Mirror clones and Git bundles
- **Repository Validation**: Integrity checks and verification
- **Flexible Integration**: Optional Git backup with granular control

### Configuration

Git repository backup is controlled through environment variables:

```bash
# Enable/disable Git repository backup (default: true)
INCLUDE_GIT_REPO=true

# Backup format: mirror, bundle (default: mirror)
GIT_BACKUP_FORMAT=mirror

# Authentication method: token, ssh (default: token)
GIT_AUTH_METHOD=token

# GitHub token for private repositories
GITHUB_TOKEN=your_github_token
```

### Usage Examples

```bash
# Backup with Git repository (default)
docker run -e GITHUB_TOKEN=your_token github-data

# Backup excluding Git repository
docker run -e INCLUDE_GIT_REPO=false github-data

# Backup with bundle format
docker run -e GIT_BACKUP_FORMAT=bundle github-data

# Backup only Git repository
docker run -e INCLUDE_ISSUES=false -e INCLUDE_LABELS=false \
           -e INCLUDE_PULL_REQUESTS=false github-data
```

### Directory Structure

```
/data/
├── github-data/          # JSON metadata (existing)
│   ├── issues.json
│   ├── labels.json
│   └── pull_requests.json
└── git-data/             # Git repository data (new)
    ├── repository.git/   # Mirror clone
    └── repository.bundle # Bundle file (if configured)
```
```

### 7. Required pytest.ini Updates

The following marker should be added to `pytest.ini` to support Git repository testing:

```ini
# Add to existing markers section
git_repositories: Git repository backup/restore functionality tests
```

## Phase 1 Implementation Schedule

### Week 1: Foundation Setup
- **Days 1-2**: Git repository service implementation with Clean Code principles (Step-Down Rule compliance)
- **Days 3-4**: Git strategy implementation and shared fixture integration  
- **Day 5**: Initial unit tests following project testing standards and code review

### Week 2: Core Git Operations
- **Days 1-2**: Complete GitRepositoryServiceImpl with bundle support
- **Days 3-4**: Strategy integration with orchestrator and main entry point
- **Day 5**: Integration testing and validation

### Week 3: Container Integration
- **Days 1-2**: Enhanced Dockerfile and container configuration
- **Days 3-4**: Main entry point integration and orchestrator updates
- **Day 5**: Container testing and environment validation

### Week 4: Testing & Documentation
- **Days 1-2**: Comprehensive unit test suite
- **Days 3-4**: Integration and container tests
- **Day 5**: Documentation updates and code review

### Week 5: Validation & Polish
- **Days 1-3**: End-to-end testing with real repositories
- **Days 4-5**: Bug fixes, performance optimization, and final review

### Week 6: Release Preparation
- **Days 1-2**: Final integration testing
- **Days 3-4**: Documentation completion
- **Day 5**: Release preparation and handoff

## Risk Mitigation Strategies

### High-Priority Risks

1. **Large Repository Timeouts**
   - **Mitigation**: Configurable timeout settings (default: 5 minutes)
   - **Implementation**: `_git_timeout` parameter in service
   - **Testing**: Include timeout tests with mock delays

2. **Authentication Failures**
   - **Mitigation**: Token-based authentication via URL modification
   - **Implementation**: URL transformation for GitHub token auth
   - **Testing**: Mock authentication scenarios

3. **Storage Space Requirements**
   - **Mitigation**: Directory size reporting via pathlib operations
   - **Implementation**: Simple directory traversal for size calculation
   - **Testing**: Storage monitoring tests with temporary directories

### Medium-Priority Risks

1. **Network Connectivity Issues**
   - **Mitigation**: Proper error handling and timeout management
   - **Implementation**: Comprehensive exception handling
   - **Testing**: Network failure simulation

2. **Git Tool Dependencies**
   - **Mitigation**: Dockerfile includes Git installation
   - **Implementation**: Container tests verify Git availability
   - **Testing**: Git version and functionality tests

## Success Criteria

### Functional Requirements
- ✅ GitRepositoryService with mirror clone capability via Git CLI
- ✅ Enhanced container with Git CLI tools
- ✅ Basic restore functionality from mirrors using Git commands
- ✅ Integration with existing orchestrator pattern (no storage changes)
- ✅ Granular configuration control

### Quality Requirements
- ✅ Unit test coverage >90% for new code
- ✅ Integration tests for public repository cloning
- ✅ Container tests verify Git functionality
- ✅ Documentation covers all new features
- ✅ Backward compatibility maintained

### Performance Requirements
- ✅ Repository backup within 2x of native git clone time
- ✅ Successful validation of cloned repositories
- ✅ Proper error handling for large repositories
- ✅ Memory usage within acceptable limits

## Next Steps for Phase 2

Phase 1 establishes the foundation for Git repository backup. Phase 2 will build upon this foundation to add:

1. **Bundle Support**: Complete bundle creation and restoration
2. **Authentication Enhancement**: SSH keys and enhanced token management
3. **Incremental Updates**: Efficient synchronization for existing backups
4. **Progress Reporting**: User feedback during long-running operations
5. **Advanced Error Recovery**: Resume capability for interrupted operations

The modular design ensures Phase 2 enhancements can be added without disrupting Phase 1 functionality.
from pathlib import Path
from typing import List

from ...requests import ValidateRestoreDataRequest, OperationResult
from ... import UseCase


class ValidateRestoreDataUseCase(UseCase[ValidateRestoreDataRequest, OperationResult]):
    def execute(self, request: ValidateRestoreDataRequest) -> OperationResult:
        try:
            input_dir = Path(request.input_path)
            required_files = self._determine_required_files(request)
            missing_files = []

            for filename in required_files:
                file_path = input_dir / filename
                if not file_path.exists():
                    missing_files.append(str(file_path))

            if missing_files:
                raise FileNotFoundError(
                    f"Required files not found: {', '.join(missing_files)}"
                )

            return OperationResult(
                success=True,
                data_type="validation",
                items_processed=len(required_files),
            )
        except FileNotFoundError:
            # Re-raise FileNotFoundError as-is for backward compatibility
            raise
        except Exception as e:
            return OperationResult(
                success=False,
                data_type="validation",
                error_message=f"Validation failed: {str(e)}",
            )

    def _determine_required_files(
        self, request: ValidateRestoreDataRequest
    ) -> List[str]:
        required = ["labels.json", "issues.json", "comments.json"]

        if request.include_prs:
            required.extend(["pull_requests.json", "pr_comments.json"])

        if request.include_sub_issues:
            required.append("sub_issues.json")

        return required

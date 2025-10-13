"""Utilities for migrating from manual boundary mocks to MockBoundaryFactory."""

import ast
import re
from typing import List, Dict, Tuple, Optional
from unittest.mock import Mock


class BoundaryMockMigrator:
    """Utility class for migrating manual boundary mocks to factory pattern."""

    @staticmethod
    def detect_manual_mock_patterns(file_content: str) -> List[Dict[str, any]]:
        """Detect common manual mock patterns in test code.
        
        Args:
            file_content: Content of a test file
            
        Returns:
            List of detected mock patterns with line numbers and patterns
        """
        patterns = []
        
        # Pattern 1: Mock() boundary creation
        mock_creation_pattern = r'(\w+)\s*=\s*Mock\(\)'
        mock_creations = []
        for match in re.finditer(mock_creation_pattern, file_content):
            line_num = file_content[:match.start()].count('\n') + 1
            var_name = match.group(1)
            if 'boundary' in var_name.lower():
                mock_creations.append({
                    'type': 'mock_creation',
                    'line': line_num,
                    'variable': var_name,
                    'pattern': match.group(0)
                })
        
        # Pattern 2: Manual return_value assignments
        for creation in mock_creations:
            var_name = creation['variable']
            return_value_pattern = rf'{var_name}\.(\w+)\.return_value\s*=\s*(.+)'
            for match in re.finditer(return_value_pattern, file_content):
                line_num = file_content[:match.start()].count('\n') + 1
                method_name = match.group(1)
                return_value = match.group(2)
                patterns.append({
                    'type': 'manual_return_value',
                    'line': line_num,
                    'variable': var_name,
                    'method': method_name,
                    'return_value': return_value,
                    'pattern': match.group(0)
                })
        
        # Pattern 3: Manual side_effect assignments
        for creation in mock_creations:
            var_name = creation['variable']
            side_effect_pattern = rf'{var_name}\.(\w+)\.side_effect\s*=\s*(.+)'
            for match in re.finditer(side_effect_pattern, file_content):
                line_num = file_content[:match.start()].count('\n') + 1
                method_name = match.group(1)
                side_effect = match.group(2)
                patterns.append({
                    'type': 'manual_side_effect',
                    'line': line_num,
                    'variable': var_name,
                    'method': method_name,
                    'side_effect': side_effect,
                    'pattern': match.group(0)
                })
        
        return patterns + mock_creations

    @staticmethod
    def generate_factory_replacement(patterns: List[Dict[str, any]], 
                                   sample_data_var: Optional[str] = None) -> str:
        """Generate MockBoundaryFactory replacement code.
        
        Args:
            patterns: Detected mock patterns from detect_manual_mock_patterns
            sample_data_var: Optional variable name containing sample data
            
        Returns:
            Generated replacement code using MockBoundaryFactory
        """
        # Group patterns by variable name
        variables = {}
        for pattern in patterns:
            if 'variable' in pattern:
                var_name = pattern['variable']
                if var_name not in variables:
                    variables[var_name] = []
                variables[var_name].append(pattern)
        
        replacement_code = []
        
        for var_name, var_patterns in variables.items():
            # Determine if this looks like a boundary mock
            is_boundary = any('boundary' in var_name.lower() for _ in [None])
            if not is_boundary:
                # Check if it has GitHub API-like methods
                methods = [p.get('method', '') for p in var_patterns if p.get('method')]
                github_methods = ['get_repository_', 'create_', 'get_issue', 'get_pull']
                is_boundary = any(any(github in method for github in github_methods) 
                                for method in methods)
            
            if is_boundary:
                # Generate factory-based replacement
                if sample_data_var:
                    factory_call = f'MockBoundaryFactory.create_auto_configured({sample_data_var})'
                else:
                    factory_call = 'MockBoundaryFactory.create_auto_configured()'
                
                replacement_code.append(f'{var_name} = {factory_call}')
                
                # Add any custom configurations that aren't covered by patterns
                custom_configs = []
                for pattern in var_patterns:
                    if pattern['type'] in ['manual_return_value', 'manual_side_effect']:
                        method = pattern['method']
                        # Skip common methods that are auto-configured
                        common_methods = [
                            'get_repository_labels', 'get_repository_issues',
                            'get_all_issue_comments', 'create_label', 'create_issue'
                        ]
                        if method not in common_methods:
                            if pattern['type'] == 'manual_return_value':
                                custom_configs.append(
                                    f'{var_name}.{method}.return_value = {pattern["return_value"]}'
                                )
                            else:  # manual_side_effect
                                custom_configs.append(
                                    f'{var_name}.{method}.side_effect = {pattern["side_effect"]}'
                                )
                
                replacement_code.extend(custom_configs)
        
        return '\n'.join(replacement_code)

    @staticmethod
    def suggest_sample_data_usage(patterns: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """Analyze patterns and suggest sample data structure.
        
        Args:
            patterns: Detected mock patterns
            
        Returns:
            Suggested sample data structure with entity types and methods
        """
        suggestions = {
            'labels': [],
            'issues': [], 
            'comments': [],
            'pull_requests': [],
            'pr_comments': [],
            'pr_reviews': [],
            'pr_review_comments': [],
            'sub_issues': []
        }
        
        for pattern in patterns:
            if pattern['type'] == 'manual_return_value':
                method = pattern.get('method', '')
                return_val = pattern.get('return_value', '')
                
                # Analyze method names to suggest data types
                if 'labels' in method:
                    suggestions['labels'].append(f'{method}: {return_val}')
                elif 'issues' in method and 'sub_issues' not in method:
                    suggestions['issues'].append(f'{method}: {return_val}')
                elif 'sub_issues' in method:
                    suggestions['sub_issues'].append(f'{method}: {return_val}')
                elif 'comments' in method and 'pull_request' not in method:
                    suggestions['comments'].append(f'{method}: {return_val}')
                elif 'pull_requests' in method:
                    suggestions['pull_requests'].append(f'{method}: {return_val}')
                elif 'pull_request_comments' in method:
                    suggestions['pr_comments'].append(f'{method}: {return_val}')
                elif 'reviews' in method and 'comment' not in method:
                    suggestions['pr_reviews'].append(f'{method}: {return_val}')
                elif 'review_comments' in method:
                    suggestions['pr_review_comments'].append(f'{method}: {return_val}')
        
        # Remove empty categories
        return {k: v for k, v in suggestions.items() if v}

    @staticmethod
    def create_migration_report(file_path: str, patterns: List[Dict[str, any]]) -> str:
        """Create a migration report for a file.
        
        Args:
            file_path: Path to the test file
            patterns: Detected patterns
            
        Returns:
            Formatted migration report
        """
        report = [f"# Migration Report: {file_path}", ""]
        
        if not patterns:
            report.append("✅ No manual boundary mock patterns detected.")
            return '\n'.join(report)
        
        # Group by variable
        variables = {}
        for pattern in patterns:
            if 'variable' in pattern:
                var_name = pattern['variable']
                if var_name not in variables:
                    variables[var_name] = []
                variables[var_name].append(pattern)
        
        report.append(f"🔍 Found {len(variables)} mock variables with {len(patterns)} total patterns")
        report.append("")
        
        for var_name, var_patterns in variables.items():
            report.append(f"## Variable: `{var_name}`")
            
            creation_patterns = [p for p in var_patterns if p['type'] == 'mock_creation']
            if creation_patterns:
                report.append(f"- **Line {creation_patterns[0]['line']}**: Mock creation")
            
            method_patterns = [p for p in var_patterns if p['type'] in ['manual_return_value', 'manual_side_effect']]
            if method_patterns:
                report.append(f"- **{len(method_patterns)} method configurations**:")
                for pattern in method_patterns[:5]:  # Show first 5
                    report.append(f"  - Line {pattern['line']}: `{pattern['method']}`")
                if len(method_patterns) > 5:
                    report.append(f"  - ... and {len(method_patterns) - 5} more")
            
            report.append("")
        
        # Suggested replacement
        sample_data_suggestions = BoundaryMockMigrator.suggest_sample_data_usage(patterns)
        if sample_data_suggestions:
            report.append("## Suggested Migration")
            report.append("```python")
            report.append("# Use shared sample data")
            for entity_type in sample_data_suggestions.keys():
                report.append(f"# - {entity_type}")
            report.append("")
            replacement = BoundaryMockMigrator.generate_factory_replacement(patterns, "sample_github_data")
            report.append(replacement)
            report.append("```")
        
        return '\n'.join(report)


class BoundaryMockValidator:
    """Validator for boundary mock completeness and correctness."""

    @staticmethod
    def validate_mock_against_protocol(mock_boundary, protocol_class) -> Tuple[bool, List[str], List[str]]:
        """Validate that a mock implements all protocol methods correctly.
        
        Args:
            mock_boundary: Mock boundary to validate
            protocol_class: Protocol class to validate against
            
        Returns:
            Tuple of (is_valid, missing_methods, incorrectly_configured_methods)
        """
        from tests.shared.mocks.boundary_factory import MockBoundaryFactory
        
        protocol_methods = []
        for name in dir(protocol_class):
            if not name.startswith("_"):
                attr = getattr(protocol_class, name)
                if callable(attr) and hasattr(attr, '__isabstractmethod__'):
                    protocol_methods.append(name)
        
        missing_methods = []
        incorrectly_configured = []
        
        for method_name in protocol_methods:
            try:
                method = getattr(mock_boundary, method_name)
                # Check if method is properly configured
                if not (hasattr(method, 'return_value') or hasattr(method, 'side_effect')):
                    incorrectly_configured.append(method_name)
            except AttributeError:
                missing_methods.append(method_name)
        
        is_valid = len(missing_methods) == 0 and len(incorrectly_configured) == 0
        return is_valid, missing_methods, incorrectly_configured

    @staticmethod
    def generate_completeness_report(mock_boundary, protocol_class) -> str:
        """Generate a completeness report for a mock boundary.
        
        Args:
            mock_boundary: Mock boundary to analyze
            protocol_class: Protocol class to validate against
            
        Returns:
            Formatted completeness report
        """
        is_valid, missing, incorrect = BoundaryMockValidator.validate_mock_against_protocol(
            mock_boundary, protocol_class
        )
        
        report = ["# Mock Boundary Completeness Report", ""]
        
        if is_valid:
            report.append("✅ **Mock boundary is fully protocol-compliant**")
        else:
            report.append("❌ **Mock boundary has protocol compliance issues**")
        
        report.append("")
        
        if missing:
            report.append(f"## Missing Methods ({len(missing)})")
            for method in missing:
                report.append(f"- `{method}`")
            report.append("")
        
        if incorrect:
            report.append(f"## Incorrectly Configured Methods ({len(incorrect)})")
            for method in incorrect:
                report.append(f"- `{method}` (no return_value or side_effect)")
            report.append("")
        
        report.append("## Recommendation")
        if not is_valid:
            report.append("Use `MockBoundaryFactory.create_auto_configured()` for guaranteed protocol completeness.")
        else:
            report.append("Mock boundary is properly configured. ✅")
        
        return '\n'.join(report)
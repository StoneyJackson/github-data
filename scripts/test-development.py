#!/usr/bin/env python3
"""Development scripts for testing workflows with enhanced fixtures."""

import subprocess
import sys
import argparse
import os
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - Success")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ {description} - Failed")
        if result.stderr.strip():
            print(f"   Error: {result.stderr.strip()}")
        return False


def development_test_cycle():
    """Run the development test cycle (fast tests only)."""
    print("🚀 Starting Development Test Cycle")
    print("="*50)
    
    commands = [
        (["pytest", "-m", "not slow and not container", "-v", "--tb=short"], 
         "Running fast tests (unit + integration)"),
        (["pytest", "-m", "enhanced_fixtures and fast", "-v"], 
         "Validating enhanced fixture usage"),
        (["make", "lint"], 
         "Running code quality checks"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
            break
    
    if success:
        print("🎉 Development cycle completed successfully!")
    else:
        print("💥 Development cycle failed - fix issues before proceeding")
    
    return success


def comprehensive_test_suite():
    """Run the complete test suite including slow tests."""
    print("🔬 Starting Comprehensive Test Suite")
    print("="*50)
    
    commands = [
        (["pytest", "-m", "unit", "-v", "--cov=src"], 
         "Running unit tests with coverage"),
        (["pytest", "-m", "integration and not container", "-v", "--cov=src", "--cov-append"], 
         "Running integration tests"),
        (["pytest", "-m", "container", "-v", "--cov=src", "--cov-append"], 
         "Running container tests"),
        (["make", "lint"], 
         "Running linting"),
        (["make", "type-check"], 
         "Running type checking"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
            # Continue running other tests even if one fails
    
    if success:
        print("🏆 All tests passed successfully!")
    else:
        print("⚠️  Some tests failed - review results above")
    
    return success


def enhanced_fixture_validation():
    """Validate enhanced fixture functionality."""
    print("🔧 Validating Enhanced Fixture Infrastructure")
    print("="*50)
    
    commands = [
        (["pytest", "-m", "enhanced_fixtures", "-v", "--tb=short"], 
         "Testing enhanced fixture usage"),
        (["pytest", "-m", "data_builders", "-v"], 
         "Validating data builder patterns"),
        (["pytest", "-m", "error_simulation", "-v"], 
         "Testing error simulation fixtures"),
        (["pytest", "-m", "workflow_services", "-v"], 
         "Validating workflow service fixtures"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def performance_analysis():
    """Run performance analysis of fixtures and tests."""
    print("📊 Running Performance Analysis")
    print("="*50)
    
    commands = [
        (["pytest", "-m", "performance", "-v", "--benchmark-only"], 
         "Running performance benchmarks"),
        (["pytest", "-m", "fast", "-v", "--tb=no", "--quiet"], 
         "Validating fast test performance"),
        (["pytest", "-m", "enhanced_fixtures", "-vv", "--tb=no"], 
         "Analyzing enhanced fixture performance"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)  # Don't fail on performance tests


def fixture_usage_report():
    """Generate fixture usage report."""
    print("📈 Generating Fixture Usage Report")
    print("="*50)
    
    # Run tests with very verbose output to capture metrics
    cmd = ["pytest", "-vv", "--tb=no", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Fixture usage metrics will be displayed at the end of test runs.")
    print("Run tests with -vv flag to see detailed fixture usage statistics.")


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(description="Development testing workflows")
    parser.add_argument("workflow", choices=[
        "dev", "comprehensive", "enhanced", "performance", "usage-report"
    ], help="Choose testing workflow")
    
    args = parser.parse_args()
    
    workflows = {
        "dev": development_test_cycle,
        "comprehensive": comprehensive_test_suite,
        "enhanced": enhanced_fixture_validation,
        "performance": performance_analysis,
        "usage-report": fixture_usage_report,
    }
    
    success = workflows[args.workflow]()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
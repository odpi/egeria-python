#!/usr/bin/env python3
"""
Test runner script for EgeriaTech testing framework.

This script provides convenient commands for running different types of tests
and managing the testing environment.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description or cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests only."""
    cmd = "pytest tests/unit/ -m unit -v"
    return run_command(cmd, "Unit Tests (Mocked)")


def run_integration_tests():
    """Run integration tests with live Egeria."""
    cmd = "pytest tests/integration/ --live-egeria -m integration -v"
    return run_command(cmd, "Integration Tests (Live Egeria)")


def run_all_tests():
    """Run all tests."""
    cmd = "pytest tests/ -v"
    return run_command(cmd, "All Tests")


def run_live_tests():
    """Run all tests with live Egeria."""
    cmd = "pytest tests/ --live-egeria -v"
    return run_command(cmd, "All Tests with Live Egeria")


def run_format_set_tests():
    """Run format set tests only."""
    cmd = "pytest tests/ -m format_sets -v"
    return run_command(cmd, "Format Set Tests")


def run_mcp_tests():
    """Run MCP tests only."""
    cmd = "pytest tests/ -m mcp -v"
    return run_command(cmd, "MCP Tests")


def run_auth_tests():
    """Run authentication tests only."""
    cmd = "pytest tests/ -m auth -v"
    return run_command(cmd, "Authentication Tests")


def run_fast_tests():
    """Run fast tests (exclude slow tests)."""
    cmd = "pytest tests/ -m 'not slow' -v"
    return run_command(cmd, "Fast Tests (Excluding Slow)")


def run_coverage():
    """Run tests with coverage report."""
    cmd = "pytest tests/ --cov=pyegeria --cov-report=html --cov-report=term-missing"
    return run_command(cmd, "Tests with Coverage")


def run_lint():
    """Run linting checks."""
    cmd = "pytest tests/ --flake8 --mypy"
    return run_command(cmd, "Linting Checks")


def setup_test_environment():
    """Set up test environment."""
    print("Setting up test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print("✓ pytest is installed")
    except ImportError:
        print("✗ pytest is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
    
    # Check if required packages are installed
    required_packages = [
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "pytest-flake8",
        "pytest-mypy"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    print("Test environment setup complete!")


def check_live_egeria():
    """Check if live Egeria is available."""
    print("Checking live Egeria availability...")
    
    # Check environment variables
    env_vars = [
        "PYEG_SERVER_NAME",
        "PYEG_PLATFORM_URL", 
        "PYEG_USER_ID",
        "PYEG_USER_PWD"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var} is set: {value}")
        else:
            print(f"✗ {var} is not set")
    
    # Check if live flag is set
    live_flag = os.getenv("PYEG_LIVE_EGERIA")
    if live_flag:
        print(f"✓ PYEG_LIVE_EGERIA is set: {live_flag}")
    else:
        print("✗ PYEG_LIVE_EGERIA is not set")
    
    print("\nTo enable live Egeria testing:")
    print("  export PYEG_LIVE_EGERIA=1")
    print("  export PYEG_SERVER_NAME=your-server")
    print("  export PYEG_PLATFORM_URL=https://your-egeria.com:9443")
    print("  export PYEG_USER_ID=your-user")
    print("  export PYEG_USER_PWD=your-password")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="EgeriaTech Test Runner")
    parser.add_argument(
        "command",
        choices=[
            "unit", "integration", "all", "live", "format-sets", 
            "mcp", "auth", "fast", "coverage", "lint", "setup", "check-live"
        ],
        help="Test command to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = False
    
    if args.command == "unit":
        success = run_unit_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "live":
        success = run_live_tests()
    elif args.command == "format-sets":
        success = run_format_set_tests()
    elif args.command == "mcp":
        success = run_mcp_tests()
    elif args.command == "auth":
        success = run_auth_tests()
    elif args.command == "fast":
        success = run_fast_tests()
    elif args.command == "coverage":
        success = run_coverage()
    elif args.command == "lint":
        success = run_lint()
    elif args.command == "setup":
        setup_test_environment()
        success = True
    elif args.command == "check-live":
        check_live_egeria()
        success = True
    
    if success:
        print(f"\n{'='*60}")
        print("✓ Tests completed successfully!")
        print(f"{'='*60}")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("✗ Tests failed!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()



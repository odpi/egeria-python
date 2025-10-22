#!/usr/bin/env python3
"""
Comprehensive test runner for all pyegeria modules.

This script provides convenient commands for running unit tests for all modules
in the pyegeria package, organized by category.
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


def run_core_module_tests():
    """Run tests for core modules (_globals, _exceptions_new, _validators)."""
    cmd = "pytest tests/unit/test_core_modules.py -v"
    return run_command(cmd, "Core Modules Tests")


def run_utils_module_tests():
    """Run tests for utils module."""
    cmd = "pytest tests/unit/test_utils_module.py -v"
    return run_command(cmd, "Utils Module Tests")


def run_config_module_tests():
    """Run tests for config module."""
    cmd = "pytest tests/unit/test_config_module.py -v"
    return run_command(cmd, "Config Module Tests")


def run_models_module_tests():
    """Run tests for models module."""
    cmd = "pytest tests/unit/test_models_module.py -v"
    return run_command(cmd, "Models Module Tests")


def run_output_formats_module_tests():
    """Run tests for output formats module."""
    cmd = "pytest tests/unit/test_output_formats_module.py -v"
    return run_command(cmd, "Output Formats Module Tests")


def run_standalone_tests():
    """Run standalone tests that avoid psycopg2 import issues."""
    cmd = "pytest tests/unit/test_modules_standalone.py -v"
    return run_command(cmd, "Standalone Module Tests")


def run_all_unit_tests():
    """Run all unit tests."""
    cmd = "pytest tests/unit/ -v"
    return run_command(cmd, "All Unit Tests")


def run_specific_module_tests(module_name):
    """Run tests for a specific module."""
    test_file = f"tests/unit/test_{module_name}_module.py"
    if os.path.exists(test_file):
        cmd = f"pytest {test_file} -v"
        return run_command(cmd, f"{module_name.title()} Module Tests")
    else:
        print(f"Test file not found: {test_file}")
        return False


def run_tests_with_coverage():
    """Run tests with coverage report."""
    cmd = "pytest tests/unit/ --cov=pyegeria --cov-report=html --cov-report=term-missing"
    return run_command(cmd, "Unit Tests with Coverage")


def run_tests_by_category(category):
    """Run tests by category."""
    categories = {
        "core": ["test_core_modules.py"],
        "utils": ["test_utils_module.py"],
        "config": ["test_config_module.py"],
        "models": ["test_models_module.py"],
        "formats": ["test_output_formats_module.py"],
        "framework": ["test_framework_validation.py"],
        "all": [
            "test_core_modules.py",
            "test_utils_module.py", 
            "test_config_module.py",
            "test_models_module.py",
            "test_output_formats_module.py",
            "test_framework_validation.py"
        ]
    }
    
    if category not in categories:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return False
    
    test_files = categories[category]
    cmd = f"pytest {' '.join([f'tests/unit/{f}' for f in test_files])} -v"
    return run_command(cmd, f"{category.title()} Category Tests")


def list_available_tests():
    """List all available test files."""
    test_dir = Path("tests/unit")
    if not test_dir.exists():
        print("Tests directory not found: tests/unit")
        return
    
    test_files = list(test_dir.glob("test_*.py"))
    
    print("\nAvailable test files:")
    print("=" * 40)
    for test_file in sorted(test_files):
        print(f"  {test_file.name}")
    
    print(f"\nTotal: {len(test_files)} test files")


def check_test_environment():
    """Check test environment setup."""
    print("Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print("✓ pytest is installed")
    except ImportError:
        print("✗ pytest is not installed")
        return False
    
    # Check if test directory exists
    if not os.path.exists("tests/unit"):
        print("✗ tests/unit directory not found")
        return False
    else:
        print("✓ tests/unit directory exists")
    
    # Check for test files
    test_files = list(Path("tests/unit").glob("test_*.py"))
    if not test_files:
        print("✗ No test files found in tests/unit")
        return False
    else:
        print(f"✓ Found {len(test_files)} test files")
    
    # Check for required dependencies
    required_packages = [
        "pytest-asyncio",
        "pytest-mock",
        "httpx",
        "loguru",
        "pydantic",
        "pydantic-settings",
        "validators"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✓ Test environment is ready!")
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Pyegeria Module Test Runner")
    parser.add_argument(
        "command",
        nargs="?",
        choices=[
        "core", "utils", "config", "models", "formats", "framework", "standalone",
        "all", "coverage", "list", "check", "help"
        ],
        default="help",
        help="Test command to run"
    )
    parser.add_argument(
        "--module", "-m",
        help="Run tests for specific module (e.g., core, utils, config)"
    )
    parser.add_argument(
        "--category", "-c",
        help="Run tests by category"
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
    
    if args.command == "core":
        success = run_core_module_tests()
    elif args.command == "utils":
        success = run_utils_module_tests()
    elif args.command == "config":
        success = run_config_module_tests()
    elif args.command == "models":
        success = run_models_module_tests()
    elif args.command == "formats":
        success = run_output_formats_module_tests()
    elif args.command == "framework":
        success = run_framework_validation_tests()
    elif args.command == "standalone":
        success = run_standalone_tests()
    elif args.command == "all":
        success = run_all_unit_tests()
    elif args.command == "coverage":
        success = run_tests_with_coverage()
    elif args.command == "list":
        list_available_tests()
        success = True
    elif args.command == "check":
        success = check_test_environment()
    elif args.command == "help":
        print("Pyegeria Module Test Runner")
        print("=" * 40)
        print("\nAvailable commands:")
        print("  core      - Run core modules tests (_globals, _exceptions_new, _validators)")
        print("  utils     - Run utils module tests")
        print("  config    - Run config module tests")
        print("  models    - Run models module tests")
        print("  formats   - Run output formats module tests")
        print("  framework - Run framework validation tests")
        print("  standalone - Run standalone tests (avoids psycopg2 issues)")
        print("  all       - Run all unit tests")
        print("  coverage  - Run tests with coverage report")
        print("  list      - List available test files")
        print("  check     - Check test environment setup")
        print("  help      - Show this help message")
        print("\nExamples:")
        print("  python tests/run_module_tests.py core")
        print("  python tests/run_module_tests.py all")
        print("  python tests/run_module_tests.py coverage")
        print("  python tests/run_module_tests.py check")
        success = True
    
    # Handle module-specific tests
    if args.module:
        success = run_specific_module_tests(args.module)
    
    # Handle category-specific tests
    if args.category:
        success = run_tests_by_category(args.category)
    
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

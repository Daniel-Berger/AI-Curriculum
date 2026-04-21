"""
Module 08 Exercises: Modules, Packages, and Tooling
====================================================

12 exercises covering import patterns, package structure, __name__ guard,
pyproject.toml, ruff configuration, and project organization.

For Swift developers: these exercises bridge SPM -> uv/pip,
Package.swift -> pyproject.toml, SwiftLint -> ruff, and Swift module
access control -> Python conventions.

Instructions:
- Replace `pass` (or `...`) with your implementation
- Some exercises produce strings/dicts (for testing) rather than actual files
- Run this file with `python exercises.py` to check your work
"""

from __future__ import annotations

import importlib
import json
import sys
import textwrap
from pathlib import Path
from typing import Any


# ============================================================================
# WARM-UP: Import Patterns and Module Basics (Exercises 1-4)
# ============================================================================


def demonstrate_import_styles() -> dict[str, str]:
    """Exercise 1: Show different import styles.

    Return a dictionary with these keys and values:
    - "math_sqrt_25": the result of sqrt(25) as a string (use `import math`)
    - "path_home": str(Path.home()) (use `from pathlib import Path`)
    - "current_platform": sys.platform (use the already-imported sys)
    - "json_null": json.dumps(None) (use the already-imported json)

    This demonstrates that import, from...import, and aliased imports
    all provide access to the same functionality.

    Swift equivalent: `import Foundation` vs `import struct Foundation.URL`
    """
    pass


def check_module_attributes(module_name: str) -> dict[str, Any]:
    """Exercise 2: Inspect a module's attributes.

    Given a module name (as a string), import it dynamically and return
    a dictionary with:
    - "name": the module's __name__ attribute
    - "has_all": whether the module defines __all__ (bool)
    - "is_package": whether the module is a package (has __path__) (bool)
    - "doc_preview": first 80 chars of the module's __doc__, or "No docstring"
    - "public_count": count of public names (not starting with '_')

    Use importlib.import_module() to import the module dynamically.

    Example:
        check_module_attributes("json")
        -> {"name": "json", "has_all": True, "is_package": False,
            "doc_preview": "JSON (JavaScript Object Notation)...", "public_count": 15}
    """
    pass


def simulate_name_guard(is_main: bool) -> str:
    """Exercise 3: Simulate the __name__ == "__main__" pattern.

    In real code, __name__ is set by the Python runtime. Here, we simulate
    the behavior:

    If is_main is True, return "Running as main program"
    If is_main is False, return "Imported as module"

    This demonstrates the pattern:
        if __name__ == "__main__":
            main()

    Swift equivalent: @main attribute or top-level code in main.swift
    """
    pass


def organize_imports(import_lines: list[str]) -> list[str]:
    """Exercise 4: Sort import statements according to PEP 8 / isort rules.

    Given a list of import statement strings, return them sorted into
    three groups separated by empty strings:
    1. Standard library imports (alphabetical)
    2. Third-party imports (alphabetical)
    3. Local imports (alphabetical)

    Rules:
    - Standard library: os, sys, json, pathlib, datetime, typing, dataclasses,
      collections, math, re, csv, logging, tempfile, shutil, io, functools,
      itertools, contextlib, abc, enum, copy, hashlib, unittest, argparse
    - Third-party: anything not stdlib and not starting with "." or "myapp"
    - Local: imports starting with "myapp" or relative imports starting with "."

    Input may have "import X" or "from X import Y" style.
    Determine the group by the top-level module name.

    Example:
        organize_imports([
            "import requests",
            "import os",
            "from myapp import utils",
            "import sys",
            "from pathlib import Path",
            "import click",
        ])
        Returns:
        [
            "import os",
            "import sys",
            "from pathlib import Path",
            "",
            "import click",
            "import requests",
            "",
            "from myapp import utils",
        ]
    """
    pass


# ============================================================================
# CORE: Package Structure and Configuration (Exercises 5-8)
# ============================================================================


def generate_init_py(
    package_name: str,
    public_modules: list[str],
    public_names: dict[str, list[str]],
) -> str:
    """Exercise 5: Generate the content of an __init__.py file.

    Given:
    - package_name: the name of the package (e.g., "mypackage")
    - public_modules: list of module names to import from
    - public_names: dict mapping module names to list of names to import

    Generate a properly formatted __init__.py that:
    1. Has a module docstring: "{package_name} package."
    2. Imports all specified names from their modules
    3. Defines __all__ listing all imported names
    4. Defines __version__ = "0.1.0"

    Example:
        generate_init_py(
            "mypackage",
            ["models", "utils"],
            {"models": ["User", "Product"], "utils": ["format_name"]},
        )
        Returns a string like:
        '''\"\"\"mypackage package.\"\"\"

        from mypackage.models import Product, User
        from mypackage.utils import format_name

        __all__ = [
            "Product",
            "User",
            "format_name",
        ]

        __version__ = "0.1.0"
        '''

    Note: Imports should be sorted by module name, and names within each
    import should be sorted alphabetically.
    """
    pass


def generate_pyproject_toml(
    name: str,
    version: str,
    description: str,
    dependencies: list[str],
    dev_dependencies: list[str],
    python_version: str = "3.11",
    author_name: str = "Developer",
    author_email: str = "dev@example.com",
) -> str:
    """Exercise 6: Generate a pyproject.toml file content.

    Generate a complete pyproject.toml string with:
    - [build-system] using hatchling
    - [project] with name, version, description, requires-python, dependencies,
      authors
    - [project.optional-dependencies] with a "dev" group
    - [tool.ruff] with target-version and line-length=88
    - [tool.ruff.lint] with select = ["E", "F", "I", "UP"]
    - [tool.pytest.ini_options] with testpaths = ["tests"]

    Return the TOML as a string. You don't need to use a TOML library --
    just build the string manually with proper TOML formatting.

    Swift equivalent: generating a Package.swift file programmatically.
    """
    pass


def describe_package_structure(
    package_name: str,
    modules: list[str],
    sub_packages: dict[str, list[str]] | None = None,
    use_src_layout: bool = True,
) -> list[str]:
    """Exercise 7: Generate a file listing for a package structure.

    Return a sorted list of file paths (as strings) that would make up
    the package. Include:
    - pyproject.toml
    - README.md
    - tests/__init__.py
    - For each module: the module .py file
    - For each sub-package: __init__.py and its module files
    - All necessary __init__.py files

    If use_src_layout is True, put the package under src/.
    If False, put it at the root.

    Example:
        describe_package_structure(
            "myapp",
            ["cli", "config"],
            {"models": ["user", "product"]},
            use_src_layout=True,
        )
        Returns:
        [
            "README.md",
            "pyproject.toml",
            "src/myapp/__init__.py",
            "src/myapp/cli.py",
            "src/myapp/config.py",
            "src/myapp/models/__init__.py",
            "src/myapp/models/product.py",
            "src/myapp/models/user.py",
            "tests/__init__.py",
        ]
    """
    pass


def parse_ruff_config(toml_content: str) -> dict[str, Any]:
    """Exercise 8: Parse ruff configuration from a TOML-like string.

    Given a simplified TOML string containing ruff configuration, extract:
    - "target_version": the target Python version (str)
    - "line_length": the line length (int)
    - "selected_rules": list of selected rule prefixes (list[str])
    - "ignored_rules": list of ignored rule codes (list[str]), empty list if none

    The input will be a simplified format (not full TOML):
    ```
    [tool.ruff]
    target-version = "py311"
    line-length = 88

    [tool.ruff.lint]
    select = ["E", "F", "I"]
    ignore = ["E501"]
    ```

    Parse this manually (don't use a TOML library).
    Handle the case where "ignore" is not present (return empty list).

    Hint: split by lines, look for key = value patterns.
    """
    pass


# ============================================================================
# CHALLENGE: Building a Package (Exercises 9-10)
# ============================================================================


def create_package_files(base_dir: Path, package_name: str) -> dict[str, str]:
    """Exercise 9: Create a complete mini-package on disk.

    Create the following structure under base_dir:
        {base_dir}/
        ├── pyproject.toml
        └── src/
            └── {package_name}/
                ├── __init__.py
                ├── calculator.py
                └── validators.py

    File contents:

    pyproject.toml:
        A valid pyproject.toml with build-system (hatchling), project name,
        version "0.1.0", requires-python ">=3.11", and empty dependencies.

    __init__.py:
        Import Calculator from calculator module and validate_positive
        from validators module. Define __all__ and __version__.

    calculator.py:
        A Calculator class with methods:
        - add(a: float, b: float) -> float
        - subtract(a: float, b: float) -> float
        - multiply(a: float, b: float) -> float
        - divide(a: float, b: float) -> float (raise ValueError on zero)

    validators.py:
        - validate_positive(value: float) -> bool: return True if value > 0
        - validate_range(value: float, min_val: float, max_val: float) -> bool

    Return a dict mapping relative file paths to their contents.
    Also actually write the files to disk.
    """
    pass


def validate_package_structure(base_dir: Path) -> dict[str, Any]:
    """Exercise 10: Validate that a Python package has correct structure.

    Check the directory at base_dir and return a validation report:
    - "has_pyproject": bool -- does pyproject.toml exist?
    - "has_src_layout": bool -- is there a src/ directory with a package?
    - "has_tests": bool -- is there a tests/ directory?
    - "package_name": str or None -- name of the package found (first dir in src/)
    - "has_init": bool -- does the package have __init__.py?
    - "module_count": int -- number of .py files in the package (excluding __init__)
    - "issues": list[str] -- list of issues found (empty if everything is valid)

    Possible issues:
    - "Missing pyproject.toml"
    - "Missing src/ directory"
    - "Missing tests/ directory"
    - "Missing __init__.py in package"
    - "No Python modules found in package"

    Example:
        # For a well-structured project:
        validate_package_structure(project_dir)
        -> {
            "has_pyproject": True,
            "has_src_layout": True,
            "has_tests": True,
            "package_name": "myapp",
            "has_init": True,
            "module_count": 3,
            "issues": [],
        }
    """
    pass


# ============================================================================
# SWIFT BRIDGE: SPM vs Python Packaging (Exercises 11-12)
# ============================================================================


def swift_package_to_python(swift_config: dict[str, Any]) -> str:
    """Exercise 11: Convert a Swift Package.swift-like config to pyproject.toml.

    Given a dictionary representing a Swift package configuration:
    {
        "name": "MySwiftPackage",
        "platforms": [".macOS(.v13)"],
        "products": [
            {"type": "library", "name": "MyLib", "targets": ["MyLib"]},
            {"type": "executable", "name": "mycli", "targets": ["CLI"]},
        ],
        "dependencies": [
            {"url": "https://github.com/Alamofire/Alamofire.git", "from": "5.8.0"},
            {"url": "https://github.com/apple/swift-argument-parser.git", "from": "1.2.0"},
        ],
        "swift_version": "5.9",
    }

    Generate a pyproject.toml string with equivalent Python configuration:
    - name: convert to lowercase-with-hyphens (PascalCase -> kebab-case)
    - python version: map swift_version 5.9 -> ">=3.11", 5.8 -> ">=3.10"
    - dependencies: use just the repo name in lowercase as pypi package names
    - executable products: add [project.scripts] entries
    - Include standard [build-system], [tool.ruff], [tool.pytest.ini_options]

    This exercise helps you understand the mapping between Swift and Python
    packaging concepts.
    """
    pass


def compare_access_control() -> dict[str, dict[str, str]]:
    """Exercise 12: Document Python access control conventions vs Swift.

    Return a dictionary mapping access levels to their Swift and Python
    equivalents:

    {
        "public": {
            "swift": "public keyword -- accessible from any module",
            "python": "No prefix -- all names are public by default",
        },
        "internal": {
            "swift": "internal keyword (default) -- accessible within the module",
            "python": "No direct equivalent -- everything is accessible",
        },
        "private": {
            "swift": "private keyword -- accessible only within the enclosing declaration",
            "python": "Single underscore prefix (_name) -- convention only, not enforced",
        },
        "file_private": {
            "swift": "fileprivate keyword -- accessible within the source file",
            "python": "No equivalent -- Python has no file-level access control",
        },
        "name_mangled": {
            "swift": "No equivalent -- Swift uses access control keywords instead",
            "python": "Double underscore prefix (__name) -- name mangling makes access harder but not impossible",
        },
        "module_api": {
            "swift": "All public symbols are the module API",
            "python": "__all__ list in __init__.py defines the public API (advisory only)",
        },
    }
    """
    pass


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    import tempfile

    # ── Exercise 1: demonstrate_import_styles ──
    result = demonstrate_import_styles()
    assert result["math_sqrt_25"] == "5.0"
    assert "Users" in result["path_home"] or "/" in result["path_home"] or "\\" in result["path_home"]
    assert isinstance(result["current_platform"], str)
    assert result["json_null"] == "null"
    print("Exercise 1 passed: demonstrate_import_styles")

    # ── Exercise 2: check_module_attributes ──
    result = check_module_attributes("json")
    assert result["name"] == "json"
    assert result["has_all"] is True
    assert isinstance(result["public_count"], int)
    assert result["public_count"] > 0
    assert isinstance(result["doc_preview"], str)

    result = check_module_attributes("os")
    assert result["name"] == "os"
    print("Exercise 2 passed: check_module_attributes")

    # ── Exercise 3: simulate_name_guard ──
    assert simulate_name_guard(True) == "Running as main program"
    assert simulate_name_guard(False) == "Imported as module"
    print("Exercise 3 passed: simulate_name_guard")

    # ── Exercise 4: organize_imports ──
    test_imports = [
        "import requests",
        "import os",
        "from myapp import utils",
        "import sys",
        "from pathlib import Path",
        "import click",
    ]
    result = organize_imports(test_imports)
    # Find the separator positions
    sep_positions = [i for i, line in enumerate(result) if line == ""]
    assert len(sep_positions) == 2, f"Expected 2 separators, got {sep_positions}"

    # Stdlib group
    stdlib_group = result[:sep_positions[0]]
    assert "import os" in stdlib_group
    assert "import sys" in stdlib_group
    assert "from pathlib import Path" in stdlib_group

    # Third-party group
    third_party_group = result[sep_positions[0]+1:sep_positions[1]]
    assert "import click" in third_party_group
    assert "import requests" in third_party_group

    # Local group
    local_group = result[sep_positions[1]+1:]
    assert "from myapp import utils" in local_group
    print("Exercise 4 passed: organize_imports")

    # ── Exercise 5: generate_init_py ──
    init_content = generate_init_py(
        "mypackage",
        ["models", "utils"],
        {"models": ["User", "Product"], "utils": ["format_name"]},
    )
    assert '"""mypackage package."""' in init_content
    assert "from mypackage.models import Product, User" in init_content
    assert "from mypackage.utils import format_name" in init_content
    assert "__all__" in init_content
    assert '"User"' in init_content
    assert '__version__ = "0.1.0"' in init_content
    print("Exercise 5 passed: generate_init_py")

    # ── Exercise 6: generate_pyproject_toml ──
    toml_content = generate_pyproject_toml(
        name="my-tool",
        version="1.0.0",
        description="A useful tool",
        dependencies=["requests>=2.31", "click>=8.1"],
        dev_dependencies=["pytest>=7.0", "ruff>=0.3.0"],
    )
    assert "[build-system]" in toml_content
    assert 'name = "my-tool"' in toml_content
    assert 'version = "1.0.0"' in toml_content
    assert "hatchling" in toml_content
    assert "requests>=2.31" in toml_content
    assert "[tool.ruff]" in toml_content
    assert "[tool.pytest.ini_options]" in toml_content
    print("Exercise 6 passed: generate_pyproject_toml")

    # ── Exercise 7: describe_package_structure ──
    result = describe_package_structure(
        "myapp",
        ["cli", "config"],
        {"models": ["user", "product"]},
        use_src_layout=True,
    )
    assert "pyproject.toml" in result
    assert "README.md" in result
    assert "src/myapp/__init__.py" in result
    assert "src/myapp/cli.py" in result
    assert "src/myapp/models/__init__.py" in result
    assert "src/myapp/models/user.py" in result
    assert "tests/__init__.py" in result

    # Test flat layout
    result_flat = describe_package_structure(
        "myapp",
        ["cli"],
        use_src_layout=False,
    )
    assert "myapp/__init__.py" in result_flat
    assert "myapp/cli.py" in result_flat
    assert "src/myapp/__init__.py" not in result_flat
    print("Exercise 7 passed: describe_package_structure")

    # ── Exercise 8: parse_ruff_config ──
    ruff_toml = textwrap.dedent("""\
        [tool.ruff]
        target-version = "py311"
        line-length = 88

        [tool.ruff.lint]
        select = ["E", "F", "I"]
        ignore = ["E501"]
    """)
    result = parse_ruff_config(ruff_toml)
    assert result["target_version"] == "py311"
    assert result["line_length"] == 88
    assert result["selected_rules"] == ["E", "F", "I"]
    assert result["ignored_rules"] == ["E501"]

    # Test without ignore
    ruff_toml_no_ignore = textwrap.dedent("""\
        [tool.ruff]
        target-version = "py312"
        line-length = 100

        [tool.ruff.lint]
        select = ["E", "F"]
    """)
    result = parse_ruff_config(ruff_toml_no_ignore)
    assert result["target_version"] == "py312"
    assert result["line_length"] == 100
    assert result["selected_rules"] == ["E", "F"]
    assert result["ignored_rules"] == []
    print("Exercise 8 passed: parse_ruff_config")

    # ── Exercise 9: create_package_files ──
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        files = create_package_files(base, "mathtools")

        # Check files were created
        assert (base / "pyproject.toml").exists()
        assert (base / "src" / "mathtools" / "__init__.py").exists()
        assert (base / "src" / "mathtools" / "calculator.py").exists()
        assert (base / "src" / "mathtools" / "validators.py").exists()

        # Check content
        calc_content = (base / "src" / "mathtools" / "calculator.py").read_text()
        assert "class Calculator" in calc_content
        assert "def add" in calc_content
        assert "def divide" in calc_content

        validators_content = (base / "src" / "mathtools" / "validators.py").read_text()
        assert "def validate_positive" in validators_content

        init_content = (base / "src" / "mathtools" / "__init__.py").read_text()
        assert "Calculator" in init_content
        assert "__all__" in init_content

    print("Exercise 9 passed: create_package_files")

    # ── Exercise 10: validate_package_structure ──
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        # Create a valid package
        create_package_files(base, "testpkg")
        (base / "tests").mkdir(exist_ok=True)
        (base / "tests" / "__init__.py").write_text("")

        result = validate_package_structure(base)
        assert result["has_pyproject"] is True
        assert result["has_src_layout"] is True
        assert result["has_tests"] is True
        assert result["package_name"] == "testpkg"
        assert result["has_init"] is True
        assert result["module_count"] == 2  # calculator.py, validators.py
        assert result["issues"] == []

    # Test with empty directory
    with tempfile.TemporaryDirectory() as tmpdir:
        result = validate_package_structure(Path(tmpdir))
        assert result["has_pyproject"] is False
        assert len(result["issues"]) > 0
        assert "Missing pyproject.toml" in result["issues"]

    print("Exercise 10 passed: validate_package_structure")

    # ── Exercise 11: swift_package_to_python ──
    swift_config = {
        "name": "MySwiftPackage",
        "platforms": [".macOS(.v13)"],
        "products": [
            {"type": "library", "name": "MyLib", "targets": ["MyLib"]},
            {"type": "executable", "name": "mycli", "targets": ["CLI"]},
        ],
        "dependencies": [
            {"url": "https://github.com/Alamofire/Alamofire.git", "from": "5.8.0"},
            {"url": "https://github.com/apple/swift-argument-parser.git", "from": "1.2.0"},
        ],
        "swift_version": "5.9",
    }
    toml_output = swift_package_to_python(swift_config)
    assert 'name = "my-swift-package"' in toml_output
    assert ">=3.11" in toml_output
    assert "alamofire" in toml_output.lower()
    assert "[project.scripts]" in toml_output
    assert "mycli" in toml_output
    print("Exercise 11 passed: swift_package_to_python")

    # ── Exercise 12: compare_access_control ──
    result = compare_access_control()
    assert "public" in result
    assert "private" in result
    assert "internal" in result
    assert "file_private" in result
    assert "name_mangled" in result
    assert "module_api" in result
    for key in result:
        assert "swift" in result[key]
        assert "python" in result[key]
    print("Exercise 12 passed: compare_access_control")

    print("\n" + "=" * 60)
    print("All 12 exercises passed!")
    print("=" * 60)

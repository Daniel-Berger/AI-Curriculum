"""
Module 08 Solutions: Modules, Packages, and Tooling
====================================================

Complete solutions for all 12 exercises.
"""

from __future__ import annotations

import importlib
import json
import math
import re
import sys
import textwrap
from pathlib import Path
from typing import Any


# ============================================================================
# WARM-UP: Import Patterns and Module Basics (Exercises 1-4)
# ============================================================================


def demonstrate_import_styles() -> dict[str, str]:
    """Exercise 1: Show different import styles."""
    import math
    from pathlib import Path

    return {
        "math_sqrt_25": str(math.sqrt(25)),
        "path_home": str(Path.home()),
        "current_platform": sys.platform,
        "json_null": json.dumps(None),
    }


def check_module_attributes(module_name: str) -> dict[str, Any]:
    """Exercise 2: Inspect a module's attributes."""
    mod = importlib.import_module(module_name)

    doc = getattr(mod, "__doc__", None)
    if doc:
        doc_preview = doc.strip()[:80]
    else:
        doc_preview = "No docstring"

    all_names = dir(mod)
    public_names = [name for name in all_names if not name.startswith("_")]

    return {
        "name": mod.__name__,
        "has_all": hasattr(mod, "__all__"),
        "is_package": hasattr(mod, "__path__"),
        "doc_preview": doc_preview,
        "public_count": len(public_names),
    }


def simulate_name_guard(is_main: bool) -> str:
    """Exercise 3: Simulate the __name__ == "__main__" pattern."""
    if is_main:
        return "Running as main program"
    return "Imported as module"


def organize_imports(import_lines: list[str]) -> list[str]:
    """Exercise 4: Sort import statements according to PEP 8 / isort rules."""
    STDLIB_MODULES = {
        "os", "sys", "json", "pathlib", "datetime", "typing", "dataclasses",
        "collections", "math", "re", "csv", "logging", "tempfile", "shutil",
        "io", "functools", "itertools", "contextlib", "abc", "enum", "copy",
        "hashlib", "unittest", "argparse",
    }

    stdlib = []
    third_party = []
    local = []

    for line in import_lines:
        # Extract the top-level module name
        stripped = line.strip()
        if stripped.startswith("from "):
            # "from X.Y import Z" -> module is "X"
            parts = stripped.split()
            module_path = parts[1]  # "X.Y" or ".X"
            top_module = module_path.split(".")[0] if not module_path.startswith(".") else ""
        elif stripped.startswith("import "):
            parts = stripped.split()
            module_path = parts[1]
            top_module = module_path.split(".")[0]
        else:
            continue

        # Classify
        if module_path.startswith(".") or module_path.startswith("myapp"):
            local.append(stripped)
        elif top_module in STDLIB_MODULES:
            stdlib.append(stripped)
        else:
            third_party.append(stripped)

    # Sort each group alphabetically
    stdlib.sort()
    third_party.sort()
    local.sort()

    # Combine with separators
    result = []
    if stdlib:
        result.extend(stdlib)
    if third_party:
        if result:
            result.append("")
        result.extend(third_party)
    if local:
        if result:
            result.append("")
        result.extend(local)

    return result


# ============================================================================
# CORE: Package Structure and Configuration (Exercises 5-8)
# ============================================================================


def generate_init_py(
    package_name: str,
    public_modules: list[str],
    public_names: dict[str, list[str]],
) -> str:
    """Exercise 5: Generate the content of an __init__.py file."""
    lines = []

    # Docstring
    lines.append(f'"""{package_name} package."""')
    lines.append("")

    # Import statements (sorted by module name)
    all_names = []
    for module in sorted(public_modules):
        if module in public_names:
            names = sorted(public_names[module])
            all_names.extend(names)
            names_str = ", ".join(names)
            lines.append(f"from {package_name}.{module} import {names_str}")

    lines.append("")

    # __all__
    lines.append("__all__ = [")
    for name in sorted(all_names):
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")

    # __version__
    lines.append('__version__ = "0.1.0"')
    lines.append("")

    return "\n".join(lines)


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
    """Exercise 6: Generate a pyproject.toml file content."""
    # Build dependencies list
    deps_str = ", ".join(f'"{d}"' for d in dependencies)
    dev_deps_str = ", ".join(f'"{d}"' for d in dev_dependencies)

    toml = textwrap.dedent(f"""\
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.api"

        [project]
        name = "{name}"
        version = "{version}"
        description = "{description}"
        requires-python = ">={python_version}"
        authors = [
            {{ name = "{author_name}", email = "{author_email}" }},
        ]
        dependencies = [
            {deps_str},
        ]

        [project.optional-dependencies]
        dev = [
            {dev_deps_str},
        ]

        [tool.ruff]
        target-version = "py{python_version.replace('.', '')}"
        line-length = 88

        [tool.ruff.lint]
        select = ["E", "F", "I", "UP"]

        [tool.pytest.ini_options]
        testpaths = ["tests"]
    """)
    return toml

    # Note: the f-string double-brace {{ }} produces literal { } in the output.


def describe_package_structure(
    package_name: str,
    modules: list[str],
    sub_packages: dict[str, list[str]] | None = None,
    use_src_layout: bool = True,
) -> list[str]:
    """Exercise 7: Generate a file listing for a package structure."""
    if sub_packages is None:
        sub_packages = {}

    files = []

    # Root files
    files.append("pyproject.toml")
    files.append("README.md")

    # Package directory prefix
    if use_src_layout:
        pkg_prefix = f"src/{package_name}"
    else:
        pkg_prefix = package_name

    # Package __init__.py
    files.append(f"{pkg_prefix}/__init__.py")

    # Modules
    for module in modules:
        files.append(f"{pkg_prefix}/{module}.py")

    # Sub-packages
    for sub_pkg, sub_modules in sub_packages.items():
        files.append(f"{pkg_prefix}/{sub_pkg}/__init__.py")
        for sub_module in sub_modules:
            files.append(f"{pkg_prefix}/{sub_pkg}/{sub_module}.py")

    # Tests
    files.append("tests/__init__.py")

    return sorted(files)


def parse_ruff_config(toml_content: str) -> dict[str, Any]:
    """Exercise 8: Parse ruff configuration from a TOML-like string."""
    result = {
        "target_version": "",
        "line_length": 0,
        "selected_rules": [],
        "ignored_rules": [],
    }

    for line in toml_content.strip().split("\n"):
        line = line.strip()

        # Parse key = value patterns
        if "=" in line and not line.startswith("["):
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "target-version":
                result["target_version"] = value.strip('"')
            elif key == "line-length":
                result["line_length"] = int(value)
            elif key == "select":
                # Parse ["E", "F", "I"] format
                result["selected_rules"] = _parse_string_list(value)
            elif key == "ignore":
                result["ignored_rules"] = _parse_string_list(value)

    return result


def _parse_string_list(value: str) -> list[str]:
    """Parse a TOML-like string list: ["a", "b", "c"] -> ["a", "b", "c"]."""
    # Remove brackets and split
    inner = value.strip("[]").strip()
    if not inner:
        return []
    items = []
    for item in inner.split(","):
        item = item.strip().strip('"').strip("'")
        if item:
            items.append(item)
    return items


# ============================================================================
# CHALLENGE: Building a Package (Exercises 9-10)
# ============================================================================


def create_package_files(base_dir: Path, package_name: str) -> dict[str, str]:
    """Exercise 9: Create a complete mini-package on disk."""
    files = {}

    # pyproject.toml
    pyproject = textwrap.dedent(f"""\
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.api"

        [project]
        name = "{package_name}"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []
    """)
    files["pyproject.toml"] = pyproject

    # __init__.py
    init_py = textwrap.dedent(f"""\
        \"""{package_name} package.\"""

        from {package_name}.calculator import Calculator
        from {package_name}.validators import validate_positive

        __all__ = ["Calculator", "validate_positive"]

        __version__ = "0.1.0"
    """)
    files[f"src/{package_name}/__init__.py"] = init_py

    # calculator.py
    calculator_py = textwrap.dedent("""\
        \"\"\"Calculator module.\"\"\"


        class Calculator:
            \"\"\"A simple calculator.\"\"\"

            def add(self, a: float, b: float) -> float:
                \"\"\"Add two numbers.\"\"\"
                return a + b

            def subtract(self, a: float, b: float) -> float:
                \"\"\"Subtract b from a.\"\"\"
                return a - b

            def multiply(self, a: float, b: float) -> float:
                \"\"\"Multiply two numbers.\"\"\"
                return a * b

            def divide(self, a: float, b: float) -> float:
                \"\"\"Divide a by b. Raises ValueError if b is zero.\"\"\"
                if b == 0:
                    raise ValueError("Cannot divide by zero")
                return a / b
    """)
    files[f"src/{package_name}/calculator.py"] = calculator_py

    # validators.py
    validators_py = textwrap.dedent("""\
        \"\"\"Validation utilities.\"\"\"


        def validate_positive(value: float) -> bool:
            \"\"\"Return True if value is positive.\"\"\"
            return value > 0


        def validate_range(value: float, min_val: float, max_val: float) -> bool:
            \"\"\"Return True if value is within [min_val, max_val].\"\"\"
            return min_val <= value <= max_val
    """)
    files[f"src/{package_name}/validators.py"] = validators_py

    # Write files to disk
    for rel_path, content in files.items():
        full_path = base_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    return files


def validate_package_structure(base_dir: Path) -> dict[str, Any]:
    """Exercise 10: Validate that a Python package has correct structure."""
    result: dict[str, Any] = {
        "has_pyproject": False,
        "has_src_layout": False,
        "has_tests": False,
        "package_name": None,
        "has_init": False,
        "module_count": 0,
        "issues": [],
    }

    # Check pyproject.toml
    if (base_dir / "pyproject.toml").exists():
        result["has_pyproject"] = True
    else:
        result["issues"].append("Missing pyproject.toml")

    # Check src layout
    src_dir = base_dir / "src"
    if src_dir.exists() and src_dir.is_dir():
        # Find the package directory (first subdirectory of src/)
        packages = [
            d for d in src_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if packages:
            result["has_src_layout"] = True
            pkg_dir = packages[0]
            result["package_name"] = pkg_dir.name

            # Check __init__.py
            if (pkg_dir / "__init__.py").exists():
                result["has_init"] = True
            else:
                result["issues"].append("Missing __init__.py in package")

            # Count modules
            py_files = [
                f for f in pkg_dir.glob("*.py")
                if f.name != "__init__.py"
            ]
            result["module_count"] = len(py_files)
            if not py_files:
                result["issues"].append("No Python modules found in package")
        else:
            result["issues"].append("Missing src/ directory")
    else:
        result["issues"].append("Missing src/ directory")

    # Check tests
    if (base_dir / "tests").exists():
        result["has_tests"] = True
    else:
        result["issues"].append("Missing tests/ directory")

    return result


# ============================================================================
# SWIFT BRIDGE: SPM vs Python Packaging (Exercises 11-12)
# ============================================================================


def swift_package_to_python(swift_config: dict[str, Any]) -> str:
    """Exercise 11: Convert a Swift Package.swift-like config to pyproject.toml."""
    # Convert PascalCase name to kebab-case
    name = swift_config["name"]
    # Insert hyphens before uppercase letters (except the first)
    kebab_name = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()

    # Map Swift version to Python version
    swift_version = swift_config.get("swift_version", "5.9")
    python_version_map = {
        "5.7": "3.9",
        "5.8": "3.10",
        "5.9": "3.11",
        "5.10": "3.12",
        "6.0": "3.12",
    }
    py_version = python_version_map.get(swift_version, "3.11")

    # Extract dependency names from URLs
    dependencies = []
    for dep in swift_config.get("dependencies", []):
        url = dep["url"]
        # Extract repo name from URL: last path component without .git
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        version = dep.get("from", "")
        dep_str = f"{repo_name.lower()}>={version}" if version else repo_name.lower()
        dependencies.append(dep_str)

    deps_str = "\n".join(f'    "{d}",' for d in dependencies)

    # Extract executable products for scripts
    scripts_entries = []
    package_module = kebab_name.replace("-", "_")
    for product in swift_config.get("products", []):
        if product["type"] == "executable":
            script_name = product["name"].lower()
            scripts_entries.append(f'{script_name} = "{package_module}.cli:main"')

    scripts_section = ""
    if scripts_entries:
        entries = "\n".join(scripts_entries)
        scripts_section = f"\n[project.scripts]\n{entries}\n"

    toml = textwrap.dedent(f"""\
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.api"

        [project]
        name = "{kebab_name}"
        version = "0.1.0"
        requires-python = ">={py_version}"
        dependencies = [
        {deps_str}
        ]
        {scripts_section}
        [tool.ruff]
        target-version = "py{py_version.replace('.', '')}"
        line-length = 88

        [tool.ruff.lint]
        select = ["E", "F", "I", "UP"]

        [tool.pytest.ini_options]
        testpaths = ["tests"]
    """)
    return toml


def compare_access_control() -> dict[str, dict[str, str]]:
    """Exercise 12: Document Python access control conventions vs Swift."""
    return {
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
    sep_positions = [i for i, line in enumerate(result) if line == ""]
    assert len(sep_positions) == 2

    stdlib_group = result[:sep_positions[0]]
    assert "import os" in stdlib_group
    assert "import sys" in stdlib_group
    assert "from pathlib import Path" in stdlib_group

    third_party_group = result[sep_positions[0]+1:sep_positions[1]]
    assert "import click" in third_party_group
    assert "import requests" in third_party_group

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

        assert (base / "pyproject.toml").exists()
        assert (base / "src" / "mathtools" / "__init__.py").exists()
        assert (base / "src" / "mathtools" / "calculator.py").exists()
        assert (base / "src" / "mathtools" / "validators.py").exists()

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
        create_package_files(base, "testpkg")
        (base / "tests").mkdir(exist_ok=True)
        (base / "tests" / "__init__.py").write_text("")

        result = validate_package_structure(base)
        assert result["has_pyproject"] is True
        assert result["has_src_layout"] is True
        assert result["has_tests"] is True
        assert result["package_name"] == "testpkg"
        assert result["has_init"] is True
        assert result["module_count"] == 2
        assert result["issues"] == []

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

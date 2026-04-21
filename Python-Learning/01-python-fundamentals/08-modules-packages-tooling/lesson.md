# Module 08: Modules, Packages, and Tooling

## Overview

This module covers Python's import system, package structure, and the modern tooling
ecosystem. As a Swift/iOS developer, you already understand modules (Swift modules),
package managers (SPM), and linters (SwiftLint). This module maps those concepts to their
Python equivalents: the import system, `uv` (package manager), `ruff` (linter/formatter),
and `pyproject.toml` (the Python equivalent of `Package.swift`).

---

## Table of Contents

1. [The Import System](#1-the-import-system)
2. [Packages and \_\_init\_\_.py](#2-packages-and-__init__py)
3. [\_\_name\_\_ == "\_\_main\_\_"](#3-__name__--__main__)
4. [Module Search Path](#4-module-search-path)
5. [Creating Packages](#5-creating-packages)
6. [pyproject.toml In Depth](#6-pyprojecttoml-in-depth)
7. [uv Package Manager](#7-uv-package-manager)
8. [Virtual Environments](#8-virtual-environments)
9. [ruff: Linting and Formatting](#9-ruff-linting-and-formatting)
10. [PEP 8 Style Guide](#10-pep-8-style-guide)
11. [Pre-commit Hooks](#11-pre-commit-hooks)
12. [Project Layout Conventions](#12-project-layout-conventions)
13. [\_\_all\_\_ and Public API](#13-__all__-and-public-api)
14. [Practical Project Setup Walkthrough](#14-practical-project-setup-walkthrough)

---

## 1. The Import System

Python's import system loads code from other modules (files) and packages (directories).
It is conceptually similar to Swift's `import` statement, but with important differences.

### Basic import

```python
# Import an entire module
import math
print(math.sqrt(16))  # 4.0
print(math.pi)        # 3.141592653589793

# Import is roughly equivalent to:
# Swift: import Foundation
# The module name becomes a namespace.
```

### from ... import

```python
# Import specific names from a module
from math import sqrt, pi
print(sqrt(16))  # 4.0 -- no prefix needed
print(pi)        # 3.141592653589793

# Import everything (avoid this -- pollutes namespace)
from math import *  # Bad practice in production code
```

### import ... as (aliasing)

```python
# Alias a module to a shorter name
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# These aliases are universal conventions in the Python ecosystem.
# Everyone uses np, pd, plt -- do not use different aliases.

# Alias a specific import
from datetime import datetime as dt
now = dt.now()
```

### Relative Imports

Relative imports use dots to refer to the current package:

```python
# Inside mypackage/submodule/helpers.py

# Import from parent package
from .. import utils            # mypackage/utils.py
from ..models import User       # mypackage/models.py -> User class

# Import from sibling module
from . import constants          # mypackage/submodule/constants.py
from .validators import check    # mypackage/submodule/validators.py -> check

# One dot = current package
# Two dots = parent package
# Three dots = grandparent package (rare, usually a design smell)
```

> **Important**: Relative imports only work inside packages (directories with
> `__init__.py`). They do not work in standalone scripts.

### How Imports Actually Work

When you write `import foo`, Python:

1. Checks `sys.modules` (cache of already-imported modules)
2. If not cached, searches `sys.path` for a module named `foo`
3. Creates a new module object
4. Executes the module's code (top-level statements run once)
5. Stores the module in `sys.modules`
6. Binds the name `foo` in the importing module's namespace

```python
import sys

# See what's already imported
print(list(sys.modules.keys())[:10])

# Modules are cached -- importing twice does NOT re-execute
import mymodule  # First import: executes module code
import mymodule  # Second import: returns cached module (no re-execution)
```

### Import Best Practices

```python
# GOOD: imports at the top of the file, organized in groups
import os                          # 1. Standard library
import sys
from pathlib import Path

import requests                    # 2. Third-party packages
from pydantic import BaseModel

from myapp.models import User      # 3. Local application imports
from myapp.utils import format_date

# GOOD: absolute imports (preferred)
from myapp.database import get_connection

# OK: relative imports within a package
from . import helpers

# BAD: wildcard imports
from os import *

# BAD: imports in the middle of a function (unless for lazy loading)
def process():
    import heavy_library  # Only OK for expensive optional dependencies
```

### Conditional and Lazy Imports

```python
# Conditional import (for optional dependencies)
try:
    import ujson as json  # Faster JSON library
except ImportError:
    import json           # Fall back to standard library

# Type-checking-only imports (avoid circular imports)
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.models import User  # Only imported for type checkers

def process_user(user: "User") -> None:
    ...
```

### Comparison with Swift

```swift
// Swift: module-level import
import Foundation        // Import entire framework
import UIKit

// Swift: specific symbol import
import struct Foundation.URL
import class UIKit.UIViewController

// Swift: no relative imports -- modules are flat namespaces
```

```python
# Python: module-level import
import os
import json

# Python: specific symbol import
from pathlib import Path
from dataclasses import dataclass

# Python: relative imports within packages
from . import utils
from ..models import User
```

---

## 2. Packages and \_\_init\_\_.py

A **package** in Python is a directory that contains Python modules. The `__init__.py` file
marks a directory as a Python package and is executed when the package is imported.

### Basic Package Structure

```
mypackage/
├── __init__.py      # Makes this directory a package
├── core.py          # A module in the package
├── utils.py         # Another module
└── models/          # A sub-package
    ├── __init__.py
    ├── user.py
    └── product.py
```

### \_\_init\_\_.py

The `__init__.py` file can be:

1. **Empty** -- just marks the directory as a package
2. **Contains initialization code** -- runs when the package is imported
3. **Defines the public API** -- re-exports from submodules

```python
# mypackage/__init__.py

# Option 1: Empty (just a marker)

# Option 2: Package-level initialization
print("mypackage is being imported")
_internal_state = {}

# Option 3: Re-export for convenient access
from mypackage.core import App
from mypackage.models.user import User
from mypackage.models.product import Product

# This lets users write:
#   from mypackage import App, User
# Instead of:
#   from mypackage.core import App
#   from mypackage.models.user import User
```

### Namespace Packages (No \_\_init\_\_.py)

Since Python 3.3, directories without `__init__.py` are treated as **namespace packages**.
These are primarily used for splitting a single logical package across multiple directories
or distributions. For normal development, always include `__init__.py`.

### Sub-package \_\_init\_\_.py

```python
# mypackage/models/__init__.py

# Re-export model classes for convenient access
from mypackage.models.user import User
from mypackage.models.product import Product

# Allows: from mypackage.models import User
# Instead of: from mypackage.models.user import User
```

### Swift Comparison

In Swift, a module is defined by a target in `Package.swift` or an Xcode target. Everything
marked `public` is automatically part of the module's API. Python has no access control --
everything is public unless you use conventions (leading underscore) or `__all__`.

```swift
// Swift: everything in the target is one module
// Public API is defined by access control keywords
public struct User { ... }
internal class Database { ... }  // Not visible outside module
private func helper() { ... }
```

```python
# Python: __init__.py defines what's "public"
# mypackage/__init__.py
from mypackage.models import User       # Explicitly exposed
# Database and helper are accessible but not advertised
```

---

## 3. \_\_name\_\_ == "\_\_main\_\_"

Every Python module has a `__name__` attribute. When a module is run as a script, `__name__`
is set to `"__main__"`. When it is imported, `__name__` is set to the module's qualified name.

```python
# mymodule.py

def main():
    print("Running as main program")

def helper():
    print("Helper function")

# This block only runs when the file is executed directly
if __name__ == "__main__":
    main()
```

```
$ python mymodule.py         # __name__ == "__main__"  -> main() runs
$ python -c "import mymodule"  # __name__ == "mymodule" -> main() does NOT run
```

### Why This Matters

Without the guard, importing the module would execute the script's logic:

```python
# BAD: no guard -- this runs on import
def process_data():
    ...

data = load_data()  # Runs when imported!
process_data()      # Runs when imported!

# GOOD: with guard
def process_data():
    ...

if __name__ == "__main__":
    data = load_data()   # Only runs when script is executed directly
    process_data()
```

### The \_\_main\_\_.py File

Packages can also be made executable. If a package contains a `__main__.py` file, it can
be run with `python -m packagename`:

```
mypackage/
├── __init__.py
├── __main__.py    # Entry point for `python -m mypackage`
├── core.py
└── cli.py
```

```python
# mypackage/__main__.py
from mypackage.cli import main

if __name__ == "__main__":
    main()
```

```bash
# Run the package as a script
python -m mypackage
```

### Swift Comparison

Swift uses the `@main` attribute to designate the entry point:

```swift
// Swift
@main
struct MyApp {
    static func main() {
        print("Hello from Swift")
    }
}
```

```python
# Python
def main():
    print("Hello from Python")

if __name__ == "__main__":
    main()
```

---

## 4. Module Search Path

When Python encounters `import foo`, it searches for `foo` in a specific order:

```python
import sys

# The module search path
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")
```

The search order is:

1. **The directory containing the script** (or current directory if interactive)
2. **PYTHONPATH** environment variable (if set)
3. **Standard library** directories
4. **Site-packages** (where pip/uv install third-party packages)

### Modifying sys.path

```python
import sys
from pathlib import Path

# Add a directory to the search path (not recommended for production)
sys.path.insert(0, str(Path.home() / "my_libs"))

# Now Python can find modules in ~/my_libs
import my_custom_module
```

> **Warning**: Modifying `sys.path` at runtime is a code smell. Use proper package
> installation (via `uv pip install -e .`) instead.

### Common Import Errors

```python
# ModuleNotFoundError: the module is not installed or not on sys.path
import nonexistent_module
# ModuleNotFoundError: No module named 'nonexistent_module'

# ImportError: the module exists but the name doesn't
from math import nonexistent_function
# ImportError: cannot import name 'nonexistent_function' from 'math'

# Circular import: two modules import each other
# a.py: from b import foo
# b.py: from a import bar
# Solution: restructure code, use lazy imports, or import at function level
```

---

## 5. Creating Packages

### Minimal Package

```
my_utils/
├── __init__.py
├── strings.py
└── numbers.py
```

```python
# my_utils/__init__.py
"""My utility package."""
from my_utils.strings import slugify, truncate
from my_utils.numbers import clamp, percentage

# my_utils/strings.py
def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    return text.lower().replace(" ", "-")

def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

# my_utils/numbers.py
def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value between minimum and maximum."""
    return max(minimum, min(maximum, value))

def percentage(part: float, whole: float) -> float:
    """Calculate percentage."""
    if whole == 0:
        return 0.0
    return (part / whole) * 100
```

```python
# Usage
from my_utils import slugify, clamp
print(slugify("Hello World"))  # "hello-world"
print(clamp(150, 0, 100))     # 100
```

### Package with Sub-packages

```
myapp/
├── __init__.py
├── config.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── product.py
├── services/
│   ├── __init__.py
│   ├── auth.py
│   └── payment.py
└── utils/
    ├── __init__.py
    ├── formatting.py
    └── validation.py
```

---

## 6. pyproject.toml In Depth

`pyproject.toml` is Python's unified project configuration file. It is the equivalent of
Swift's `Package.swift` -- it defines metadata, dependencies, build settings, and tool
configurations, all in one file.

### Anatomy of pyproject.toml

```toml
# ── Build System ───────────────────────────────────────────────────────────
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.api"

# ── Project Metadata ──────────────────────────────────────────────────────
[project]
name = "my-awesome-project"
version = "0.1.0"
description = "A brief description of the project"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Daniel Berger", email = "daniel@example.com" },
]
keywords = ["utility", "tools"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

# ── Dependencies ──────────────────────────────────────────────────────────
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0",
    "click>=8.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.3.0",
    "mypy>=1.8",
    "pre-commit>=3.6",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.5",
]
all = [
    "my-awesome-project[dev]",
    "my-awesome-project[docs]",
]

# ── Entry Points ──────────────────────────────────────────────────────────
[project.scripts]
# Creates a CLI command: `myapp` -> calls myapp.cli:main
myapp = "myapp.cli:main"

# ── URLs ──────────────────────────────────────────────────────────────────
[project.urls]
Homepage = "https://github.com/user/my-awesome-project"
Repository = "https://github.com/user/my-awesome-project"
Issues = "https://github.com/user/my-awesome-project/issues"

# ── Tool Configurations ──────────────────────────────────────────────────

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### Dependency Specifiers

```toml
dependencies = [
    "requests",              # Any version
    "requests>=2.31",        # Minimum version
    "requests>=2.31,<3.0",   # Version range
    "requests~=2.31",        # Compatible release (>=2.31, <3.0)
    "requests==2.31.0",      # Exact version (avoid in libraries)
]
```

### Optional Dependencies (Extras)

Optional dependencies let users install only what they need:

```toml
[project.optional-dependencies]
# Groups of optional dependencies
postgres = ["psycopg2>=2.9"]
redis = ["redis>=5.0"]
dev = [
    "pytest>=7.0",
    "ruff>=0.3.0",
]
```

```bash
# Install with specific extras
uv pip install -e ".[dev]"
uv pip install -e ".[postgres,redis]"
```

### Comparison with Package.swift

```swift
// Package.swift
let package = Package(
    name: "MyPackage",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "MyPackage", targets: ["MyPackage"]),
        .executable(name: "myapp", targets: ["CLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    ],
    targets: [
        .target(name: "MyPackage", dependencies: ["Alamofire"]),
        .target(name: "CLI", dependencies: ["MyPackage"]),
        .testTarget(name: "MyPackageTests", dependencies: ["MyPackage"]),
    ]
)
```

```toml
# pyproject.toml (equivalent)
[project]
name = "my-package"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
myapp = "my_package.cli:main"
```

---

## 7. uv Package Manager

`uv` is a modern Python package manager written in Rust by Astral (the same team behind
`ruff`). It replaces `pip`, `pip-tools`, `virtualenv`, and `pipx` with a single,
blazingly fast tool.

### Why uv?

| Feature | pip | uv |
|---------|-----|-----|
| Speed | Slow | 10-100x faster |
| Lock files | No (needs pip-tools) | Built-in (`uv lock`) |
| Virtual envs | Separate tool (venv) | Built-in (`uv venv`) |
| Dependency resolution | Basic | Advanced (like Cargo/SPM) |
| Python management | No | Built-in (`uv python install`) |

### Core uv Commands

```bash
# ── Virtual Environment ───────────────────────────────────────────────────
uv venv                    # Create .venv in current directory
uv venv --python 3.12      # Create venv with specific Python version
source .venv/bin/activate   # Activate (macOS/Linux)

# ── Package Management ────────────────────────────────────────────────────
uv pip install requests     # Install a package
uv pip install -e "."       # Install current project in editable mode
uv pip install -e ".[dev]"  # Install with optional dependencies

uv add requests             # Add dependency to pyproject.toml AND install
uv add --dev pytest         # Add as dev dependency
uv remove requests          # Remove dependency

# ── Dependency Locking ────────────────────────────────────────────────────
uv lock                     # Generate/update uv.lock
uv sync                     # Install exact versions from lock file

# ── Running Commands ──────────────────────────────────────────────────────
uv run python script.py     # Run with the project's dependencies
uv run pytest               # Run pytest within the project environment
uv run ruff check .         # Run ruff within the project environment

# ── Python Management ────────────────────────────────────────────────────
uv python install 3.12      # Install Python 3.12
uv python list              # List available Python versions
```

### uv Workflow

```bash
# Starting a new project
mkdir my-project && cd my-project
uv init                        # Creates pyproject.toml, .python-version, etc.
uv add requests pydantic       # Add dependencies
uv add --dev pytest ruff       # Add dev dependencies
uv lock                        # Generate lock file
uv sync                        # Install everything

# Daily workflow
uv run pytest                  # Run tests
uv run ruff check .            # Lint
uv run python -m myapp         # Run your app

# Adding a new dependency
uv add httpx                   # Adds to pyproject.toml and installs
uv lock                        # Update lock file
```

### Comparison with SPM

| Concept | SPM | uv |
|---------|-----|-----|
| Config file | `Package.swift` | `pyproject.toml` |
| Lock file | `Package.resolved` | `uv.lock` |
| Add dependency | Edit `Package.swift` | `uv add <package>` |
| Resolve | `swift package resolve` | `uv lock` |
| Install | `swift build` (automatic) | `uv sync` |
| Run | `swift run` | `uv run` |
| Update | `swift package update` | `uv lock --upgrade` |

---

## 8. Virtual Environments

A **virtual environment** is an isolated Python installation. It is how Python solves the
dependency isolation problem. Without virtual environments, all projects share the same
global Python installation, leading to version conflicts.

### Why Virtual Environments?

```
# Problem: global installation
Project A needs requests==2.25
Project B needs requests==2.31
# Both can't be satisfied simultaneously!

# Solution: virtual environments
project-a/.venv/ -> has requests==2.25
project-b/.venv/ -> has requests==2.31
# Each project has its own isolated packages
```

### Creating and Using Virtual Environments

```bash
# Create with uv (recommended)
uv venv
# Creates .venv/ directory

# Activate
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Your prompt changes to show the active environment
(.venv) $ python --version
(.venv) $ which python  # Points to .venv/bin/python

# Deactivate
deactivate
```

### How Virtual Environments Work

A virtual environment is just a directory containing:

```
.venv/
├── bin/                  # (Scripts/ on Windows)
│   ├── python           # Symlink to system Python
│   ├── pip              # Package installer
│   └── activate         # Activation script
├── lib/
│   └── python3.12/
│       └── site-packages/   # Installed packages go here
└── pyvenv.cfg            # Configuration
```

When activated, the shell's `PATH` is modified so that `.venv/bin/python` takes precedence
over the system Python.

### Swift Comparison

Swift/Xcode does not have virtual environments because SPM resolves dependencies per-project
automatically. Each project's `.build/` directory is already isolated. Python's virtual
environments serve the same purpose but require explicit setup.

---

## 9. ruff: Linting and Formatting

`ruff` is an extremely fast Python linter and formatter written in Rust. It replaces
`flake8`, `isort`, `black`, `pyflakes`, and many other tools. It is the Python equivalent
of `SwiftLint` + `swift-format` combined.

### Basic Usage

```bash
# Check for lint errors
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code (like black)
ruff format .

# Check formatting without modifying
ruff format --check .
```

### Configuration in pyproject.toml

```toml
[tool.ruff]
# Target Python version
target-version = "py311"

# Maximum line length
line-length = 88

# Directories to exclude
exclude = [
    ".venv",
    "__pycache__",
    "migrations",
]

[tool.ruff.lint]
# Rule selection
# E = pycodestyle errors
# F = pyflakes
# I = isort (import sorting)
# N = pep8-naming
# W = pycodestyle warnings
# UP = pyupgrade (modernize syntax)
# B = flake8-bugbear (common bugs)
# SIM = flake8-simplify
# RUF = ruff-specific rules
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "RUF"]

# Rules to ignore
ignore = [
    "E501",  # Line too long (formatter handles this)
]

# Allow autofix for all enabled rules
fixable = ["ALL"]

[tool.ruff.lint.per-file-ignores]
# Ignore unused imports in __init__.py (they're re-exports)
"__init__.py" = ["F401"]
# Ignore naming conventions in tests
"tests/**" = ["N802", "N803"]

[tool.ruff.lint.isort]
# Import sorting configuration
known-first-party = ["myapp"]

[tool.ruff.format]
# Formatting options
quote-style = "double"
indent-style = "space"
docstring-code-format = true
```

### Common Ruff Rules

| Code | Rule | Example |
|------|------|---------|
| F401 | Unused import | `import os` when os is never used |
| F841 | Unused variable | `x = 5` when x is never used |
| E711 | Comparison to None | `if x == None` -> `if x is None` |
| E712 | Comparison to bool | `if x == True` -> `if x` |
| I001 | Unsorted imports | import os after import requests |
| UP006 | Use `list` instead of `List` | `List[int]` -> `list[int]` |
| UP007 | Use `X \| Y` instead of `Union` | `Union[int, str]` -> `int \| str` |
| B006 | Mutable default argument | `def f(x=[])` |
| SIM108 | Use ternary operator | if/else that can be a ternary |

### Comparison with SwiftLint

| Feature | SwiftLint | ruff |
|---------|-----------|------|
| Language | Swift | Rust |
| Config file | `.swiftlint.yml` | `pyproject.toml` [tool.ruff] |
| Speed | Fast | Extremely fast (10-100x faster than alternatives) |
| Auto-fix | Yes | Yes |
| Formatting | No (use swift-format) | Yes (built-in formatter) |
| Import sorting | No | Yes (replaces isort) |
| Rules | ~200 | ~800 |

---

## 10. PEP 8 Style Guide

PEP 8 is Python's official style guide. It is roughly equivalent to Swift's API Design
Guidelines. `ruff` enforces PEP 8 automatically, but knowing the key points helps you
write idiomatic Python.

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables | `snake_case` | `user_name` |
| Functions | `snake_case` | `calculate_total()` |
| Classes | `PascalCase` | `UserProfile` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Modules | `snake_case` | `data_processing.py` |
| Packages | `lowercase` (no underscores preferred) | `mypackage` |
| Private | `_leading_underscore` | `_internal_helper()` |
| Name-mangled | `__double_leading` | `__private_attr` |
| Dunder/Magic | `__double_both__` | `__init__()` |

### Comparison with Swift

| Aspect | Swift | Python |
|--------|-------|--------|
| Variables | `camelCase` | `snake_case` |
| Functions | `camelCase` | `snake_case` |
| Types | `PascalCase` | `PascalCase` |
| Constants | `camelCase` or `PascalCase` | `UPPER_SNAKE_CASE` |
| Enum cases | `camelCase` | `UPPER_SNAKE_CASE` (if using enum module) |
| Protocols | `PascalCase` (often ~able) | `PascalCase` (ABCs) |

### Key PEP 8 Rules

```python
# Indentation: 4 spaces (not tabs, not 2 spaces)
def my_function():
    if True:
        return 42

# Maximum line length: 79-88 characters (79 is PEP 8, 88 is Black/Ruff default)

# Blank lines:
# - 2 blank lines before top-level functions/classes
# - 1 blank line between methods
# - 0 blank lines around single-line class body

class MyClass:

    def method_one(self):
        pass

    def method_two(self):
        pass


def top_level_function():
    pass


def another_function():
    pass

# Imports: one per line, grouped (stdlib, third-party, local)
import os
import sys

import requests

from myapp import utils

# Whitespace:
x = 1              # Yes
x=1                # No
x = x + 1          # Yes
x = x+1            # Discouraged
list[0]            # Yes
list [0]           # No
func(arg)          # Yes
func( arg )        # No
dict["key"]        # Yes
dict ["key"]       # No

# Trailing commas (encouraged in multi-line structures):
my_list = [
    "item1",
    "item2",
    "item3",        # Trailing comma -- makes diffs cleaner
]
```

---

## 11. Pre-commit Hooks

Pre-commit hooks run automated checks before each git commit. The `pre-commit` framework
manages these hooks. This is similar to Xcode build phases or git hooks in iOS projects.

### Setup

```bash
# Install pre-commit
uv add --dev pre-commit

# Or install globally
uv tool install pre-commit
```

Create a `.pre-commit-config.yaml` in your project root:

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff -- linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff          # Linting
        args: [--fix]
      - id: ruff-format   # Formatting

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: check-merge-conflict

  # Type checking (optional, can be slow)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

```bash
# Install the git hooks
pre-commit install

# Now pre-commit runs automatically on `git commit`
# To run manually on all files:
pre-commit run --all-files
```

### How It Works

1. You run `git commit`
2. Pre-commit intercepts and runs all configured hooks
3. If any hook fails, the commit is blocked
4. Fix the issues, `git add` the fixes, and commit again

---

## 12. Project Layout Conventions

Python projects use two common layouts: **flat layout** and **src layout**.

### Flat Layout

```
my-project/
├── pyproject.toml
├── README.md
├── mypackage/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
└── tests/
    ├── __init__.py
    ├── test_core.py
    └── test_utils.py
```

- Simple and common
- Package directory is at the project root
- Risk: tests might accidentally import from the local directory instead of the installed package

### Src Layout (Recommended)

```
my-project/
├── pyproject.toml
├── README.md
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_core.py
    └── test_utils.py
```

- Package is inside `src/`
- Forces you to install the package (`uv pip install -e .`) before tests can import it
- Prevents accidental imports from the project root
- Recommended by the Python Packaging Authority (PyPA)

### Full Professional Project Structure

```
my-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .pre-commit-config.yaml
├── .gitignore
├── .env.example
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── auth.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_models.py
│   └── integration/
│       ├── __init__.py
│       └── test_services.py
└── docs/
    └── index.md
```

### Swift Comparison

```
# Swift/SPM project structure
MySwiftPackage/
├── Package.swift          # pyproject.toml
├── Package.resolved       # uv.lock
├── Sources/
│   └── MyPackage/         # src/mypackage/
│       ├── MyPackage.swift
│       └── Models/
│           └── User.swift
└── Tests/
    └── MyPackageTests/    # tests/
        └── UserTests.swift
```

---

## 13. \_\_all\_\_ and Public API

`__all__` is a list that explicitly declares the public API of a module. It controls what
is exported when a user writes `from module import *`.

### Defining \_\_all\_\_

```python
# mypackage/utils.py

__all__ = ["format_name", "validate_email"]

def format_name(first: str, last: str) -> str:
    """Public function -- listed in __all__."""
    return f"{first} {last}"

def validate_email(email: str) -> bool:
    """Public function -- listed in __all__."""
    return "@" in email

def _normalize(text: str) -> str:
    """Private by convention (leading underscore)."""
    return text.strip().lower()

def internal_helper() -> None:
    """Not in __all__, so not exported by wildcard import."""
    pass
```

```python
# These are the effects of __all__:

from mypackage.utils import *
# Only format_name and validate_email are imported

from mypackage.utils import internal_helper
# This still works! __all__ only affects wildcard imports.
# Python has no true access control.
```

### \_\_all\_\_ in \_\_init\_\_.py

```python
# mypackage/__init__.py

from mypackage.models import User, Product
from mypackage.utils import format_name, validate_email

__all__ = [
    "User",
    "Product",
    "format_name",
    "validate_email",
]
```

### Comparison with Swift Access Control

| Mechanism | Swift | Python |
|-----------|-------|--------|
| Public API | `public` keyword (enforced) | `__all__` list (advisory) |
| Internal | `internal` (default, module-scoped) | No equivalent |
| Private | `private` / `fileprivate` (enforced) | `_prefix` (convention only) |
| Name mangling | N/A | `__double_prefix` (makes access harder) |
| Module exports | All `public` symbols | `__all__` or explicit imports in `__init__.py` |

Key difference: Swift's access control is **enforced by the compiler**. Python's is
**purely conventional** -- nothing prevents accessing `_private` attributes. The community
respects the convention, but the language does not enforce it.

---

## 14. Practical Project Setup Walkthrough

Here is a complete walkthrough of setting up a new Python project from scratch using
modern tooling.

### Step 1: Create the Project

```bash
# Create project directory
mkdir my-data-tool && cd my-data-tool

# Initialize with uv
uv init

# This creates:
# pyproject.toml
# .python-version
# README.md
# src/my_data_tool/__init__.py
# .gitignore
```

### Step 2: Configure pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.api"

[project]
name = "my-data-tool"
version = "0.1.0"
description = "A tool for processing data files"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.3.0",
    "pre-commit>=3.6",
]

[project.scripts]
datatool = "my_data_tool.cli:main"

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.ruff.lint.isort]
known-first-party = ["my_data_tool"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Step 3: Create Package Structure

```bash
# Create directory structure
mkdir -p src/my_data_tool tests
```

```python
# src/my_data_tool/__init__.py
"""My Data Tool -- a CLI for processing data files."""

__version__ = "0.1.0"

# src/my_data_tool/cli.py
"""Command-line interface."""

import click

from my_data_tool.processor import process_file


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file path")
def main(filepath: str, output: str | None) -> None:
    """Process a data file."""
    result = process_file(filepath, output)
    click.echo(f"Processed {result.lines} lines")


# src/my_data_tool/processor.py
"""Core data processing logic."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessResult:
    """Result of processing a file."""
    lines: int
    output_path: Path


def process_file(filepath: str, output: str | None = None) -> ProcessResult:
    """Process a data file and return results."""
    input_path = Path(filepath)
    content = input_path.read_text()
    lines = content.strip().split("\n")

    output_path = Path(output) if output else input_path.with_suffix(".out")
    processed = "\n".join(line.strip() for line in lines)
    output_path.write_text(processed)

    return ProcessResult(lines=len(lines), output_path=output_path)
```

### Step 4: Set Up Development Environment

```bash
# Create virtual environment
uv venv

# Install project with dev dependencies
uv pip install -e ".[dev]"

# Set up pre-commit
pre-commit install
```

### Step 5: Add Tests

```python
# tests/__init__.py
# (empty)

# tests/test_processor.py
"""Tests for the data processor."""

import tempfile
from pathlib import Path

from my_data_tool.processor import process_file


def test_process_file_basic():
    """Test basic file processing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.txt"
        output_path = Path(tmpdir) / "output.txt"
        input_path.write_text("  hello  \n  world  \n")

        result = process_file(str(input_path), str(output_path))

        assert result.lines == 2
        assert output_path.read_text() == "hello\nworld"
```

### Step 6: Run Everything

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run your CLI
uv run datatool sample.txt --output result.txt
```

---

## Key Takeaways

1. **Use absolute imports** -- except within packages where relative imports are appropriate.
2. **Always include `__init__.py`** -- in package directories.
3. **Use the `if __name__ == "__main__":` guard** -- in any file that could be both
   imported and run as a script.
4. **Use `pyproject.toml`** -- for all project configuration. It is the single source of
   truth, like `Package.swift`.
5. **Use `uv`** -- for package management. It is fast, modern, and replaces multiple tools.
6. **Use `ruff`** -- for linting and formatting. Configure it in `pyproject.toml`.
7. **Use virtual environments** -- always. Never install packages globally.
8. **Use the src layout** -- for professional projects. It prevents subtle import issues.
9. **Define `__all__`** -- in modules and packages to declare the public API.
10. **Follow PEP 8** -- especially `snake_case` naming. Let `ruff` enforce it.
11. **Set up pre-commit hooks** -- to catch issues before they reach version control.
12. **Group imports** -- standard library, third-party, local -- separated by blank lines.

# Swift vs Python: Modules, Packages, and Tooling

## Overview

Both Swift and Python have module systems, package managers, and linting tools, but they
differ significantly in philosophy and implementation. Swift favors compile-time safety
with explicit access control and strongly-typed package manifests. Python favors convention
over enforcement, runtime flexibility, and configuration-file-driven tooling.

---

## Package Manager: SPM vs uv/pip

| Feature | SPM (Swift Package Manager) | uv (Python) |
|---------|----------------------------|-------------|
| Written in | Swift | Rust |
| Config file | `Package.swift` (executable Swift code) | `pyproject.toml` (static TOML) |
| Lock file | `Package.resolved` | `uv.lock` |
| Registry | Swift Package Index (community) | PyPI (central, official) |
| Install deps | `swift build` (automatic) | `uv sync` or `uv pip install` |
| Add dependency | Edit `Package.swift` manually | `uv add <package>` |
| Remove dependency | Edit `Package.swift` manually | `uv remove <package>` |
| Update deps | `swift package update` | `uv lock --upgrade` |
| Run project | `swift run` | `uv run python -m myapp` |
| Build | `swift build` | N/A (Python is interpreted) |
| Test | `swift test` | `uv run pytest` |
| Isolation | Per-project `.build/` directory | Virtual environments (`.venv/`) |
| Version mgmt | Xcode / swiftenv | `uv python install 3.12` |

### SPM Workflow
```bash
# Create new package
swift package init --name MyPackage --type library

# Edit Package.swift to add dependencies
# Then:
swift build
swift test
swift run MyExecutable
```

### uv Workflow
```bash
# Create new project
uv init my-package

# Add dependencies
uv add requests pydantic
uv add --dev pytest ruff

# Install and run
uv sync
uv run pytest
uv run python -m my_package
```

---

## Configuration: Package.swift vs pyproject.toml

### Swift (Package.swift)
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyApp",
    platforms: [.macOS(.v13), .iOS(.v16)],
    products: [
        .library(name: "MyLib", targets: ["MyLib"]),
        .executable(name: "myapp", targets: ["CLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
        .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.2.0"),
    ],
    targets: [
        .target(
            name: "MyLib",
            dependencies: ["Alamofire"]
        ),
        .executableTarget(
            name: "CLI",
            dependencies: [
                "MyLib",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
            ]
        ),
        .testTarget(
            name: "MyLibTests",
            dependencies: ["MyLib"]
        ),
    ]
)
```

### Python (pyproject.toml)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.api"

[project]
name = "my-app"
version = "1.0.0"
description = "My application"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.3.0",
]

[project.scripts]
myapp = "my_app.cli:main"

[tool.ruff]
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Key Differences

| Aspect | Package.swift | pyproject.toml |
|--------|---------------|----------------|
| Format | Executable Swift code | Static TOML data |
| Type safety | Compile-time checked | No type checking |
| Targets | Explicit target graph | Single package (usually) |
| Platform spec | `platforms: [.macOS(.v13)]` | `requires-python = ">=3.11"` |
| Tool config | Separate files | Unified in `[tool.*]` sections |
| Dependency source | Git URLs | PyPI package names |
| Version pinning | `.exact("1.2.3")`, `.upToNextMajor` | `==1.2.3`, `>=1.2,<2.0` |

---

## Import System

| Feature | Swift | Python |
|---------|-------|--------|
| Import module | `import Foundation` | `import os` |
| Import specific | `import struct Foundation.URL` | `from os import path` |
| Alias | N/A (no built-in aliasing) | `import numpy as np` |
| Relative imports | N/A | `from . import utils` |
| Conditional import | `#if canImport(UIKit)` | `try: import X except: import Y` |
| Import location | Top of file (convention) | Top of file (PEP 8 rule) |
| Import grouping | Not standardized | stdlib / third-party / local |
| Circular imports | Handled by compiler | Runtime error (must restructure) |
| Re-exports | `@_exported import` (unofficial) | `from mod import X` in `__init__.py` |

### Swift
```swift
import Foundation
import UIKit
import Alamofire

// Specific type import
import struct Foundation.URL
import class UIKit.UIViewController

// Conditional import
#if canImport(SwiftUI)
import SwiftUI
#endif
```

### Python
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import requests
from pydantic import BaseModel

# Local
from myapp.models import User
from . import utils  # Relative import
```

---

## Access Control

| Level | Swift | Python |
|-------|-------|--------|
| **Public** | `public` -- accessible from any module | No prefix -- everything is public |
| **Internal** | `internal` (default) -- accessible within the module | No equivalent |
| **File-private** | `fileprivate` -- accessible within the source file | No equivalent |
| **Private** | `private` -- accessible within the enclosing declaration | `_single_underscore` (convention) |
| **Name-mangled** | N/A | `__double_underscore` (name mangling) |
| **Module API** | All `public` symbols | `__all__` list (advisory) |

### Swift: Compiler-Enforced
```swift
public class UserService {
    public var name: String               // Accessible from anywhere
    internal var cache: [String: User]    // Accessible within the module
    fileprivate var config: Config        // Accessible within this file
    private var apiKey: String            // Accessible within this class

    public init(name: String) {           // Public initializer
        // ...
    }

    private func refreshToken() {         // Private method
        // ...
    }
}

// Compiler ERROR if you try to access .apiKey from outside the class
```

### Python: Convention-Based
```python
class UserService:
    def __init__(self, name: str):
        self.name = name                  # Public (no prefix)
        self._cache: dict[str, User] = {} # "Private" by convention
        self.__api_key = "secret"         # Name-mangled (harder to access)

    def get_user(self, id: str) -> User:  # Public method
        return self._cache.get(id)

    def _refresh_token(self) -> None:     # "Private" by convention
        pass

# Python does NOT prevent access:
service = UserService("test")
print(service._cache)          # Works (convention violation, not error)
print(service._UserService__api_key)  # Works (name mangling, not true privacy)
```

### Defining Public API

```swift
// Swift: public keyword defines the API
// Only public symbols are visible outside the module
public struct User { ... }
internal struct InternalHelper { ... }  // Not visible outside
```

```python
# Python: __all__ defines the API (advisory only)
# mypackage/__init__.py
from mypackage.user import User
from mypackage._helpers import InternalHelper

__all__ = ["User"]  # Only User is part of the public API
# InternalHelper is still accessible, just not advertised
```

---

## Linting and Formatting: SwiftLint vs ruff

| Feature | SwiftLint | ruff |
|---------|-----------|------|
| Language | Swift | Rust |
| Config file | `.swiftlint.yml` | `pyproject.toml` `[tool.ruff]` |
| Speed | Fast | Extremely fast (10-100x vs Python alternatives) |
| Auto-fix | `swiftlint --fix` | `ruff check --fix` |
| Formatting | No (use swift-format) | Yes (built-in: `ruff format`) |
| Import sorting | No | Yes (replaces isort) |
| Integration | Xcode build phase | Pre-commit hook / CI |
| Rules | ~200 rules | ~800 rules |
| Custom rules | Yes (regex-based) | No (but extensive built-in rules) |
| Editor integration | Xcode plugin | VS Code extension |

### SwiftLint Configuration
```yaml
# .swiftlint.yml
disabled_rules:
  - trailing_whitespace
  - line_length

opt_in_rules:
  - empty_count
  - closure_spacing

excluded:
  - Pods
  - .build

line_length:
  warning: 120
  error: 150
```

### ruff Configuration
```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
exclude = [".venv", "__pycache__"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__
"tests/**" = ["N802"]      # Allow non-PEP8 function names in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## Project Structure

### Swift (SPM)
```
MySwiftPackage/
├── Package.swift                  # Package manifest
├── Package.resolved               # Lock file
├── Sources/
│   ├── MyLib/                     # Library target
│   │   ├── Models/
│   │   │   └── User.swift
│   │   ├── Services/
│   │   │   └── AuthService.swift
│   │   └── MyLib.swift
│   └── CLI/                       # Executable target
│       └── main.swift
├── Tests/
│   └── MyLibTests/
│       └── UserTests.swift
└── .swiftlint.yml
```

### Python (src layout)
```
my-python-package/
├── pyproject.toml                 # Package manifest + tool config
├── uv.lock                        # Lock file
├── src/
│   └── my_package/                # Package directory
│       ├── __init__.py            # Package marker + public API
│       ├── __main__.py            # Entry point for python -m
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── auth.py
│       └── cli.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Shared test fixtures
│   └── test_user.py
└── .pre-commit-config.yaml
```

### Structure Mapping

| Swift | Python | Purpose |
|-------|--------|---------|
| `Package.swift` | `pyproject.toml` | Package configuration |
| `Package.resolved` | `uv.lock` | Dependency lock file |
| `Sources/` | `src/` | Source code root |
| `Sources/MyLib/` | `src/my_package/` | Main package |
| `main.swift` | `__main__.py` | Entry point |
| `Tests/` | `tests/` | Test directory |
| `Tests/MyLibTests/` | `tests/` | Test files (flat in Python) |
| `.swiftlint.yml` | `[tool.ruff]` in pyproject.toml | Linter config |
| `.gitignore` | `.gitignore` | Git ignore rules |

---

## Naming Conventions

| Element | Swift | Python |
|---------|-------|--------|
| Variables | `camelCase` | `snake_case` |
| Functions | `camelCase` | `snake_case` |
| Types/Classes | `PascalCase` | `PascalCase` |
| Protocols/ABCs | `PascalCase` (often `-able`) | `PascalCase` |
| Constants | `camelCase` or `PascalCase` | `UPPER_SNAKE_CASE` |
| Enum cases | `camelCase` | `UPPER_SNAKE_CASE` (enum module) |
| Modules | `PascalCase` | `snake_case` |
| Packages | `PascalCase` (SPM) | `lowercase` or `snake_case` |
| Files | `PascalCase.swift` | `snake_case.py` |
| Private | `private` keyword | `_leading_underscore` |
| Test functions | `testSomething()` | `test_something()` |

### Examples

```swift
// Swift naming
let userName = "Alice"           // camelCase variable
func calculateTotal() -> Double  // camelCase function
struct UserProfile { }           // PascalCase type
protocol Displayable { }        // PascalCase protocol
let maxRetries = 3               // camelCase constant
enum Direction { case north }    // camelCase enum case
```

```python
# Python naming
user_name = "Alice"               # snake_case variable
def calculate_total() -> float:   # snake_case function
class UserProfile: ...            # PascalCase class
class Displayable(ABC): ...       # PascalCase ABC
MAX_RETRIES = 3                   # UPPER_SNAKE_CASE constant
class Direction(Enum):
    NORTH = "north"               # UPPER_SNAKE_CASE enum member
```

---

## Quick Reference: Tool Equivalents

| Task | Swift | Python |
|------|-------|--------|
| Package manager | SPM | uv (or pip) |
| Config file | Package.swift | pyproject.toml |
| Lock file | Package.resolved | uv.lock |
| Linter | SwiftLint | ruff |
| Formatter | swift-format | ruff format |
| Type checker | Swift compiler | mypy / pyright |
| Test framework | XCTest | pytest |
| Documentation | DocC / Jazzy | Sphinx / MkDocs |
| CI/CD | GitHub Actions / Xcode Cloud | GitHub Actions |
| REPL | `swift` command | `python` / `ipython` |
| Run script | `swift script.swift` | `python script.py` |
| Build | `swift build` | N/A (interpreted) |
| Dependency isolation | Automatic per-project | Virtual environments |
| Code coverage | Xcode / `swift test --enable-code-coverage` | `pytest --cov` |

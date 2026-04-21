# Swift vs Python: Error Handling and I/O

## Overview

Error handling is one of the areas where Swift and Python diverge most significantly.
Swift uses a compile-time checked system with `throws`, `try`, and `do/catch`. Python
uses a runtime exception model where any function can raise any exception at any time.
Understanding these differences is critical for writing robust Python code.

---

## Error Model Comparison

| Aspect | Swift | Python |
|--------|-------|--------|
| Error type | `Error` protocol (usually enums) | `Exception` class (class hierarchy) |
| Declaring errors | `throws` in function signature | Nothing -- any function can raise |
| Throwing | `throw MyError.case` | `raise MyError("message")` |
| Catching | `do { try ... } catch { }` | `try: ... except: ...` |
| Typed errors | `throws(MyError)` (Swift 6) | No equivalent -- catch by class |
| Forced try | `try!` (crashes on error) | No equivalent |
| Optional try | `try?` (returns nil on error) | Pattern: `try/except` returning None |
| Exhaustive matching | Compiler enforced with enums | Not enforced -- rely on hierarchy |
| Cleanup | `defer { }` | `finally:` block |
| Error propagation | Explicit: must use `try` | Implicit: exceptions propagate automatically |

---

## Error Declaration and Throwing

### Swift
```swift
// Errors are enums conforming to Error protocol
enum NetworkError: Error {
    case timeout(duration: TimeInterval)
    case badResponse(statusCode: Int)
    case noConnection
}

// Must declare throws in signature
func fetchData(from url: URL) throws -> Data {
    guard isConnected else {
        throw NetworkError.noConnection
    }
    // ...
}
```

### Python
```python
# Errors are classes inheriting from Exception
class NetworkError(Exception):
    """Base network error."""

class TimeoutError(NetworkError):
    def __init__(self, duration: float) -> None:
        self.duration = duration
        super().__init__(f"Timeout after {duration}s")

class BadResponseError(NetworkError):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Bad response: {status_code}")

class NoConnectionError(NetworkError):
    pass

# Nothing in the signature indicates this can raise
def fetch_data(url: str) -> bytes:
    if not is_connected():
        raise NoConnectionError("No network connection")
    # ...
```

---

## Catching Errors

### Swift
```swift
do {
    let data = try fetchData(from: url)
    let user = try JSONDecoder().decode(User.self, from: data)
    display(user)
} catch NetworkError.timeout(let duration) {
    print("Timed out after \(duration)s")
} catch NetworkError.badResponse(let code) where code == 404 {
    showNotFound()
} catch NetworkError.noConnection {
    showOfflineUI()
} catch {
    // Must handle all cases -- 'error' is implicit
    print("Unknown error: \(error)")
}
```

### Python
```python
try:
    data = fetch_data(url)
    user = parse_user(data)
    display(user)
except TimeoutError as e:
    print(f"Timed out after {e.duration}s")
except BadResponseError as e:
    if e.status_code == 404:
        show_not_found()
    else:
        raise  # Re-raise for other status codes
except NoConnectionError:
    show_offline_ui()
except NetworkError as e:
    # Catches any NetworkError subclass not caught above
    print(f"Network error: {e}")
```

---

## try? / try! Equivalents

### Swift
```swift
// try? -- returns nil on error
let data = try? fetchData(from: url)

// try! -- crashes on error (force unwrap)
let data = try! fetchData(from: url)
```

### Python
```python
# try? equivalent -- return None on error
def try_fetch(url: str) -> bytes | None:
    try:
        return fetch_data(url)
    except Exception:
        return None

data = try_fetch(url)

# try! equivalent -- no equivalent needed, just call it
# Python functions raise exceptions that propagate automatically
data = fetch_data(url)  # Crashes if exception is raised
```

---

## defer vs finally

### Swift
```swift
func processFile(at path: String) throws -> String {
    let handle = try FileHandle(forReadingAtPath: path)
    defer {
        handle.closeFile()  // Always runs, even on throw
    }

    let data = handle.readDataToEndOfFile()
    return String(data: data, encoding: .utf8)!
}
```

### Python
```python
def process_file(path: str) -> str:
    handle = open(path)
    try:
        data = handle.read()
        return data
    finally:
        handle.close()  # Always runs, even on exception

# Pythonic: use context managers instead of finally
def process_file(path: str) -> str:
    with open(path) as handle:  # Automatically closes
        return handle.read()
```

---

## The else Clause (Python-only)

Python's `try/except/else` has no Swift equivalent. The `else` block runs only when no
exception was raised in the `try` block.

### Python
```python
try:
    value = int(user_input)
except ValueError:
    print("Invalid number")
else:
    # Only runs if int() succeeded
    # Exceptions here are NOT caught by the except above
    result = compute(value)
    save(result)
finally:
    cleanup()
```

### Swift (closest approximation)
```swift
// No direct equivalent -- you'd use a flag or restructure:
var parsedValue: Int?
do {
    parsedValue = try parseInt(userInput)
} catch {
    print("Invalid number")
}

if let value = parsedValue {
    let result = compute(value)
    save(result)
}
```

---

## Error Hierarchies: Enums vs Classes

| Feature | Swift Enums | Python Classes |
|---------|-------------|----------------|
| Pattern | Flat enum with cases | Class hierarchy with inheritance |
| Associated data | Enum associated values | Instance attributes |
| Matching | switch/case (exhaustive) | except clauses (not exhaustive) |
| Extensibility | Closed (cannot add cases externally) | Open (can subclass externally) |
| Grouping | One enum = one group | Inheritance = grouping |

### Swift
```swift
enum AppError: Error {
    case network(NetworkError)
    case validation(field: String, message: String)
    case notFound(resource: String)
}

// Matching is exhaustive
switch error {
case .network(let netError):
    handle(netError)
case .validation(let field, let message):
    showFieldError(field, message)
case .notFound(let resource):
    show404(resource)
}
```

### Python
```python
class AppError(Exception): pass
class NetworkError(AppError): pass
class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
class NotFoundError(AppError):
    def __init__(self, resource: str) -> None:
        self.resource = resource

# Matching is NOT exhaustive -- no compiler warning for missing cases
try:
    do_something()
except NetworkError as e:
    handle_network(e)
except ValidationError as e:
    show_field_error(e.field, e.message)
except NotFoundError as e:
    show_404(e.resource)
# If a new AppError subclass is added, this silently misses it
```

---

## File System: FileManager vs pathlib

| Operation | Swift (FileManager) | Python (pathlib) |
|-----------|---------------------|------------------|
| Home directory | `FileManager.default.homeDirectoryForCurrentUser` | `Path.home()` |
| Current directory | `FileManager.default.currentDirectoryPath` | `Path.cwd()` |
| Join paths | `url.appendingPathComponent("file")` | `path / "file"` |
| File exists | `FileManager.default.fileExists(atPath:)` | `path.exists()` |
| Is directory | via `isDirectory` out param | `path.is_dir()` |
| Read file | `String(contentsOf: url)` | `path.read_text()` |
| Write file | `string.write(to: url, atomically: true)` | `path.write_text(s)` |
| Create directory | `createDirectory(at:withIntermediateDirectories:)` | `path.mkdir(parents=True)` |
| List contents | `contentsOfDirectory(at:)` | `path.iterdir()` |
| Delete file | `removeItem(at:)` | `path.unlink()` |
| Delete directory | `removeItem(at:)` | `shutil.rmtree(path)` |
| Copy file | `copyItem(at:to:)` | `shutil.copy2(src, dst)` |
| Move file | `moveItem(at:to:)` | `path.rename(new)` |
| Glob | N/A (use `contentsOfDirectory` + filter) | `path.glob("*.txt")` |
| File extension | `url.pathExtension` | `path.suffix` |
| File name | `url.lastPathComponent` | `path.name` |
| Parent directory | `url.deletingLastPathComponent()` | `path.parent` |

### Swift
```swift
let fm = FileManager.default
let home = fm.homeDirectoryForCurrentUser
let dataDir = home.appendingPathComponent("Documents").appendingPathComponent("data")

// Create directory
try fm.createDirectory(at: dataDir, withIntermediateDirectories: true)

// Write file
let content = "Hello, World!"
try content.write(to: dataDir.appendingPathComponent("hello.txt"),
                  atomically: true, encoding: .utf8)

// Read file
let text = try String(contentsOf: dataDir.appendingPathComponent("hello.txt"))

// List files
let items = try fm.contentsOfDirectory(at: dataDir, includingPropertiesForKeys: nil)
for item in items {
    print(item.lastPathComponent)
}
```

### Python
```python
from pathlib import Path

home = Path.home()
data_dir = home / "Documents" / "data"

# Create directory
data_dir.mkdir(parents=True, exist_ok=True)

# Write file
(data_dir / "hello.txt").write_text("Hello, World!")

# Read file
text = (data_dir / "hello.txt").read_text()

# List files
for item in data_dir.iterdir():
    print(item.name)
```

---

## JSON: Codable vs json Module

| Feature | Swift (Codable) | Python (json) |
|---------|-----------------|---------------|
| Decode | `JSONDecoder().decode(T.self, from: data)` | `json.loads(string)` |
| Encode | `JSONEncoder().encode(object)` | `json.dumps(object)` |
| Type safety | Compile-time via Codable conformance | Runtime -- returns dicts/lists |
| Custom keys | `CodingKeys` enum | Manual dict construction |
| Nested decoding | Automatic with nested Codable types | Manual navigation or object_hook |
| Date handling | `.dateDecodingStrategy` | Manual with `datetime.fromisoformat()` |
| Pretty printing | `encoder.outputFormatting = .prettyPrinted` | `json.dumps(data, indent=2)` |
| File I/O | `JSONDecoder().decode(T.self, from: data)` | `json.load(file)` / `json.dump(data, file)` |

### Swift
```swift
struct User: Codable {
    let name: String
    let email: String
    let age: Int
}

// Decode
let data = jsonString.data(using: .utf8)!
let user = try JSONDecoder().decode(User.self, from: data)

// Encode
let encoded = try JSONEncoder().encode(user)
let jsonString = String(data: encoded, encoding: .utf8)!
```

### Python
```python
import json
from dataclasses import dataclass, asdict

@dataclass
class User:
    name: str
    email: str
    age: int

# Decode -- returns a plain dict, not a User object
data = json.loads(json_string)
user = User(**data)  # Unpack dict into constructor

# Encode -- dataclasses need manual conversion
json_string = json.dumps(asdict(user))
```

### Key Difference

Swift's `Codable` gives you type-safe serialization at compile time. Python's `json` module
works with plain dicts and lists -- there is no automatic mapping to/from typed objects.
Libraries like `pydantic` (covered in Phase 5) add Swift-Codable-like type safety to Python.

---

## Logging: os_log / Logger vs logging

| Feature | Swift (os_log / Logger) | Python (logging) |
|---------|-------------------------|------------------|
| Import | `import os` (OSLog framework) | `import logging` |
| Create logger | `Logger(subsystem:category:)` | `logging.getLogger(__name__)` |
| Log levels | `.debug`, `.info`, `.notice`, `.error`, `.fault` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| Privacy | `\(value, privacy: .private)` | No built-in privacy controls |
| Output destination | System console / Console.app | Configurable handlers (console, file, etc.) |
| Formatting | System-controlled | Fully customizable `Formatter` |
| Structured data | Built-in with type-safe interpolation | `extra={}` dict or structured logging libs |
| Performance | Lazy formatting by default | Lazy with `%s` style, eager with f-strings |

### Swift
```swift
import os

let logger = Logger(subsystem: "com.myapp", category: "network")

logger.debug("Fetching URL: \(url)")
logger.info("Request completed in \(duration)ms")
logger.error("Request failed: \(error.localizedDescription)")
```

### Python
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Fetching URL: %s", url)
logger.info("Request completed in %dms", duration)
logger.error("Request failed: %s", error)
```

---

## EAFP vs LBYL: A Cultural Difference

| Philosophy | Swift | Python |
|-----------|-------|--------|
| Default approach | LBYL (guard, if let, optional chaining) | EAFP (try/except) |
| Nil/None handling | Optionals with compile-time safety | try/except or explicit None checks |
| Key lookup | `dict[key]` returns optional | `dict[key]` raises KeyError |
| Safe access | `array[safe: index]` (custom) | `try: array[index]` |
| Type checks | Compiler enforced | Runtime duck typing |

### Swift (LBYL)
```swift
// Guard against nil
guard let value = dictionary["key"] else {
    return defaultValue
}

// Optional chaining
let name = user?.profile?.name ?? "Unknown"

// Optional binding
if let data = try? loadData() {
    process(data)
}
```

### Python (EAFP)
```python
# Try and handle failure
try:
    value = dictionary["key"]
except KeyError:
    value = default_value

# Or use .get() for dicts specifically
value = dictionary.get("key", default_value)

# Try the operation, handle failure
try:
    data = load_data()
except FileNotFoundError:
    data = default_data
else:
    process(data)
```

---

## Environment Variables

| Feature | Swift / Xcode | Python |
|---------|---------------|--------|
| Read env var | `ProcessInfo.processInfo.environment["KEY"]` | `os.environ.get("KEY")` |
| Set env var | Xcode scheme settings | `os.environ["KEY"] = "value"` |
| Config files | `.xcconfig` files | `.env` files with `python-dotenv` |
| Build configs | Debug/Release schemes | No built-in equivalent |
| Secrets | Keychain / Xcode secrets | `.env` file (not committed) |

---

## Quick Reference: Pattern Translation

| Swift Pattern | Python Equivalent |
|---------------|-------------------|
| `do { try f() } catch { }` | `try: f() except: ...` |
| `try?` | `try/except` returning `None` |
| `try!` | Just call the function (crash on error) |
| `throws` | No annotation needed |
| `throw` | `raise` |
| `defer { cleanup() }` | `finally: cleanup()` or context manager |
| `guard let x = ... else { return }` | `try: x = ... except: return` |
| `Error` protocol | `Exception` base class |
| `localizedDescription` | `str(error)` or `error.args` |
| `NSError.domain` / `.code` | Custom exception attributes |
| `Result<T, Error>` | Return tuple or raise exception |

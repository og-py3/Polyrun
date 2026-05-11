# Polyrun

**By Haripriyan**


> **Run Java, Node.js, JavaScript, C, C++, Rust, and Go — all from Python.**

`polyrun` is a zero-dependency Python library that lets you execute code in multiple programming languages, pass data between them, and chain them together in multi-language pipelines — all from a clean, Pythonic API.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/PyPI-polyrun-orange?logo=pypi)](https://pypi.org/project/polyrun/)
[![Languages](https://img.shields.io/badge/Languages-7-green)](#supported-languages)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

---

## Table of Contents

- [Features](#features)
- [Supported Languages](#supported-languages)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Running Code](#running-code)
  - [RunResult](#runresult)
  - [Passing Input Data](#passing-input-data)
  - [Pipeline — Chain Languages Together](#pipeline--chain-languages-together)
  - [Bridge — Exchange JSON Between Python and Other Languages](#bridge--exchange-json-between-python-and-other-languages)
  - [Detect Available Languages](#detect-available-languages)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Publishing to PyPI](#publishing-to-pypi)
- [License](#license)

---

## Features

- **Run any of 7 languages from Python** with a single `.run()` call
- **Pass data via stdin/stdout** — any string or serialized JSON
- **Pipeline** — chain languages so each step feeds the next
- **Bridge** — structured JSON exchange between Python and any language
- **Graceful error handling** — typed exceptions for compilation failures, runtime errors, and missing toolchains
- **Zero external Python dependencies** — uses only the standard library

---

## Supported Languages

| Language | Import | Requires |
|---|---|---|
| Node.js | `Node` | `node` on PATH |
| JavaScript | `JS` | `node` on PATH (alias for Node) |
| Java | `Java` | `javac` + `java` on PATH |
| C | `C` | `gcc` on PATH |
| C++ | `Cpp` | `g++` on PATH |
| Rust | `Rust` | `rustc` on PATH |
| Go | `Go` | `go` on PATH |

---

## Installation

**From PyPI:**

```bash
pip install polyrun
```

**From source:**

```bash
git clone https://github.com/your-username/polyrun
cd polyrun
pip install -e .
```

> **Prerequisites:** Install the language runtimes you want to use and ensure they are on your system `PATH`. The library will raise a clear error if a runtime is missing.

---

## Quick Start

```python
from polyrun import Node, C, Cpp, Rust, Go, Java

# ── Node.js ────────────────────────────────────────────────────────────────
result = Node.run("console.log('Hello from Node.js!')")
print(result.text())  # Hello from Node.js!

# ── C ──────────────────────────────────────────────────────────────────────
result = C.run("""
#include <stdio.h>
int main() {
    printf("Hello from C!\\n");
    return 0;
}
""")
print(result.text())  # Hello from C!

# ── C++ ────────────────────────────────────────────────────────────────────
result = Cpp.run("""
#include <iostream>
int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}
""")
print(result.text())  # Hello from C++!

# ── Rust ───────────────────────────────────────────────────────────────────
result = Rust.run("""
fn main() {
    println!("Hello from Rust!");
}
""")
print(result.text())  # Hello from Rust!

# ── Go ─────────────────────────────────────────────────────────────────────
result = Go.run("""
package main
import "fmt"
func main() { fmt.Println("Hello from Go!") }
""")
print(result.text())  # Hello from Go!

# ── Java ───────────────────────────────────────────────────────────────────
result = Java.run("""
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
""")
print(result.text())  # Hello from Java!
```

---

## API Reference

### Running Code

Every runner exposes a `.run()` method:

```python
runner.run(code, input_data=None, timeout=30)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | The source code to execute |
| `input_data` | `str \| None` | `None` | String piped to the program's stdin |
| `timeout` | `int` | `30` | Max seconds to wait (60 for Rust due to compilation) |

Returns a [`RunResult`](#runresult) object.

---

### RunResult

Every `.run()` call returns a `RunResult` with these properties and methods:

| Member | Type | Description |
|---|---|---|
| `.text()` | `str` | stdout trimmed to a string |
| `.lines()` | `list[str]` | stdout split into a list of lines |
| `.json()` | `Any` | stdout parsed as JSON |
| `.stdout` | `str` | raw stdout string |
| `.stderr` | `str` | raw stderr string |
| `.returncode` | `int` | process exit code |
| `.language` | `str` | name of the language that produced this result |

```python
result = Node.run("console.log(JSON.stringify([1,2,3]))")
print(result.text())      # [1,2,3]
print(result.json())      # [1, 2, 3]
print(result.lines())     # ['[1,2,3]']
print(result.returncode)  # 0
```

---

### Passing Input Data

Use `input_data` to pipe a string to the program's stdin:

```python
import json
from polyrun import Node

code = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let raw = '';
rl.on('line', l => raw += l);
rl.on('close', () => {
    const data = JSON.parse(raw);
    console.log(JSON.stringify(data.map(x => x * 2)));
});
"""

result = Node.run(code, input_data=json.dumps([1, 2, 3, 4, 5]))
print(result.json())  # [2, 4, 6, 8, 10]
```

**Tip:** Use `json.dumps()` on the Python side and `JSON.parse(stdin)` (or equivalent) on the language side for structured data exchange.

---

### Pipeline — Chain Languages Together

`Pipeline` passes the stdout of each step as stdin to the next:

```python
from polyrun import Node, Rust
from polyrun.pipeline import Pipeline

js_double = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let d = '';
rl.on('line', l => d += l);
rl.on('close', () => console.log(parseInt(d.trim()) * 2));
"""

rust_increment = """
use std::io::{self, BufRead};
fn main() {
    let stdin = io::stdin();
    let line = stdin.lock().lines().next().unwrap().unwrap();
    let n: i64 = line.trim().parse().unwrap();
    println!("Result: {}", n + 1);
}
"""

result = (
    Pipeline()
    .then(Node, js_double)       # 21 → 42
    .then(Rust, rust_increment)  # 42 → "Result: 43"
    .run(initial_input="21")
)

print(result.text())  # Result: 43
```

**Pipeline API:**

| Method | Description |
|---|---|
| `.then(runner, code)` | Add a step to the pipeline |
| `.run(initial_input=None, timeout=30)` | Execute all steps and return the final `RunResult` |

---

### Bridge — Exchange JSON Between Python and Other Languages

`Bridge` wraps stdin/stdout with automatic JSON serialization:

```python
from polyrun import Node
from polyrun.pipeline import Bridge

js_code = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let raw = '';
rl.on('line', l => raw += l);
rl.on('close', () => {
    const data = JSON.parse(raw);
    const sorted = [...data].sort((a, b) => a - b);
    process.stdout.write(JSON.stringify(sorted));
});
"""

# Python list → JSON → stdin → Node.js → stdout → JSON → Python list
result = Bridge.send(Node, js_code, data=[5, 3, 1, 4, 2])
output = Bridge.recv(result)
print(output)  # [1, 2, 3, 4, 5]
```

**Bridge API:**

| Method | Description |
|---|---|
| `Bridge.send(runner, code, data=None)` | Serialize `data` as JSON and run the code |
| `Bridge.recv(result)` | Deserialize stdout from the `RunResult` back to Python |

---

### Detect Available Languages

```python
from polyrun.detect import check, available

# Human-readable report
check()

# Machine-readable dict
status = available()
# {'Node.js / JavaScript': True, 'Java': True, 'C': True, ...}
```

---

## Error Handling

Three exception types cover all failure modes:

```python
from polyrun import Rust
from polyrun.exceptions import (
    CompilationError,
    RuntimeError,
    LanguageNotFoundError,
)

try:
    result = Rust.run("fn main() { this_wont_compile }")

except CompilationError as e:
    # Raised when the compiler exits with an error
    print(f"Compiler said: {e.stderr}")

except RuntimeError as e:
    # Raised when the compiled/interpreted program exits non-zero
    print(f"Program crashed (exit {e.returncode}): {e.stderr}")

except LanguageNotFoundError as e:
    # Raised when the required binary is not on PATH
    print(f"Install {e.binary} to use {e.language}")
```

**Exception Reference:**

| Exception | When raised | Key attributes |
|---|---|---|
| `CompilationError` | Compiler exits non-zero | `.language`, `.stderr` |
| `RuntimeError` | Program exits non-zero | `.language`, `.stderr`, `.returncode` |
| `LanguageNotFoundError` | Binary not found on PATH | `.language`, `.binary` |

---

## Examples

Run the included examples:

```bash
# Hello world in every language
python3 polyrun/examples/hello_world.py

# Multi-language pipelines
python3 polyrun/examples/pipeline_demo.py

# JSON data exchange between Python and other languages
python3 polyrun/examples/data_passing.py

# Full test suite (148 tests, all languages)
python3 polyrun/tests/test_suite.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Your Python code                  │
│                                                      │
│  from polyrun import Node, Rust, C                  │
│  result = Node.run(js_code, input_data="hello")     │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                    polyrun library                   │
│                                                      │
│  BaseRunner (.run / _check_binary / _run_subprocess) │
│       │                                              │
│   ┌───┴──────────────────────────────────────────┐  │
│   │  NodeRunner  JavaRunner  CRunner  CppRunner   │  │
│   │  RustRunner  GoRunner                        │  │
│   └───────────────────────────────────────────────┘ │
│                                                      │
│  Pipeline  ──  chains runners, passes stdout→stdin   │
│  Bridge    ──  JSON encode/decode around any runner  │
│  detect    ──  shutil.which checks per language      │
│  exceptions ── CompilationError / RuntimeError /     │
│                LanguageNotFoundError                 │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              subprocess + tempfiles                   │
│                                                      │
│  1. Write code to a temp file                        │
│  2. Compile (if needed): javac, gcc, g++, rustc      │
│  3. Run binary / interpreter with subprocess         │
│  4. Capture stdout + stderr → RunResult              │
│  5. Clean up temp directory                          │
└─────────────────────────────────────────────────────┘
```

**Key design decisions:**

| Decision | Reason |
|---|---|
| Subprocess + tempfiles | Universal — no JNI/FFI complexity, works for all 7 languages |
| stdin/stdout for data | Language-agnostic — every language can read stdin and write stdout |
| JSON as data format | Structured, self-describing, natively supported by all target languages |
| Temp dir per run | Isolation — no state leaks between runs |
| `shutil.which` checks | Clear error before any subprocess is launched |
| Typed exceptions | Callers can distinguish compile, runtime, and missing-tool failures |

---

## Project Structure

```
polyrun/
├── polyrun/
│   ├── __init__.py          # Public API: Node, JS, C, Cpp, Rust, Go, Java
│   ├── base.py              # BaseRunner + RunResult
│   ├── pipeline.py          # Pipeline and Bridge
│   ├── detect.py            # Language availability checks
│   ├── exceptions.py        # CompilationError, RuntimeError, LanguageNotFoundError
│   ├── runners/
│   │   ├── __init__.py
│   │   ├── node.py          # Node.js / JavaScript runner
│   │   ├── java.py          # Java runner (javac + java)
│   │   ├── c.py             # C runner (gcc)
│   │   ├── cpp.py           # C++ runner (g++)
│   │   ├── rust.py          # Rust runner (rustc)
│   │   └── go.py            # Go runner (go run)
│   ├── examples/
│   │   ├── hello_world.py   # Basic usage for every language
│   │   ├── pipeline_demo.py # Multi-language pipeline examples
│   │   └── data_passing.py  # JSON data exchange examples
│   └── tests/
│       └── test_suite.py    # 148 automated tests, all languages
├── demo.py                  # Minimal usage demo
├── pyproject.toml           # Modern PyPI build config
├── setup.py                 # Legacy pip install support
├── README.md                # This file
└── LICENSE                  # MIT License
```

---

## Publishing to PyPI

1. **Build the distribution:**
   ```bash
   pip install build twine
   python -m build
   ```

2. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

3. **Users install with:**
   ```bash
   pip install polyrun
   ```

4. **Users import with:**
   ```python
   from polyrun import Node, Rust, Go, C, Cpp, Java, JS
   ```

> Before uploading, update your name, email, and GitHub URL in `pyproject.toml` and `setup.py`.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

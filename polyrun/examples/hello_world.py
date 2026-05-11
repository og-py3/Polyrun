"""
Basic hello-world examples for every supported language.
Run:  python polyrun/examples/hello_world.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from polyrun import Java, Node, JS, C, Cpp, Rust, Go
from polyrun.detect import check

check()

examples = [
    (
        "Node.js",
        Node,
        "console.log('Hello from Node.js!');",
    ),
    (
        "JavaScript (alias)",
        JS,
        "console.log('Hello from JavaScript!');",
    ),
    (
        "C",
        C,
        '#include <stdio.h>\nint main() { printf("Hello from C!\\n"); return 0; }',
    ),
    (
        "C++",
        Cpp,
        '#include <iostream>\nint main() { std::cout << "Hello from C++!" << std::endl; return 0; }',
    ),
    (
        "Rust",
        Rust,
        'fn main() { println!("Hello from Rust!"); }',
    ),
    (
        "Go",
        Go,
        'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello from Go!") }',
    ),
    (
        "Java",
        Java,
        'public class Main { public static void main(String[] args) { System.out.println("Hello from Java!"); } }',
    ),
]

for name, runner, code in examples:
    try:
        result = runner.run(code)
        print(f"[{name}] {result.text()}")
    except Exception as e:
        print(f"[{name}] SKIPPED — {e}")

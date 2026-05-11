"""
Pipeline demo — pass data through Node.js → Go → Rust.
Run:  python polyrun/examples/pipeline_demo.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from polyrun import Node, Go, Rust, C, Cpp
from polyrun.pipeline import Pipeline, Bridge

print("=== Pipeline: Node.js -> Rust ===")
js_code = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let lines = [];
rl.on('line', l => lines.push(l));
rl.on('close', () => {
    const num = parseInt(lines[0], 10);
    console.log(num * 2);
});
"""
rust_code = """
use std::io::{self, BufRead};
fn main() {
    let stdin = io::stdin();
    let line = stdin.lock().lines().next().unwrap().unwrap();
    let n: i64 = line.trim().parse().unwrap();
    println!("Rust doubled it again: {}", n * 2);
}
"""

try:
    result = (
        Pipeline()
        .then(Node, js_code)
        .then(Rust, rust_code)
        .run(initial_input="21")
    )
    print("Final output:", result.text())
except Exception as e:
    print(f"Pipeline skipped: {e}")

print()
print("=== Bridge: Python -> Node.js -> Python ===")
js_bridge = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let raw = '';
rl.on('line', l => raw += l);
rl.on('close', () => {
    const data = JSON.parse(raw);
    const result = { ...data, processed: true, length: data.message.length };
    process.stdout.write(JSON.stringify(result));
});
"""

try:
    result = Bridge.send(Node, js_bridge, data={"message": "hello from Python"})
    parsed = Bridge.recv(result)
    print("Bridge result:", parsed)
except Exception as e:
    print(f"Bridge skipped: {e}")

print()
print("=== C and C++ interop ===")
c_code = """
#include <stdio.h>
int main() {
    int a = 6, b = 7;
    printf("C says: %d * %d = %d\\n", a, b, a * b);
    return 0;
}
"""
cpp_code = """
#include <iostream>
#include <string>
int main() {
    std::string msg = "C++ says: ";
    int result = 6 * 7;
    std::cout << msg << result << std::endl;
    return 0;
}
"""
try:
    c_result = C.run(c_code)
    print(c_result.text())
    cpp_result = Cpp.run(cpp_code)
    print(cpp_result.text())
except Exception as e:
    print(f"C/C++ skipped: {e}")

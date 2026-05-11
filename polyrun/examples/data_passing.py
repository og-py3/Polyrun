"""
Data passing demo — exchange JSON between Python and other languages.
Run:  python polyrun/examples/data_passing.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import json
from polyrun import Node, Go, Rust

print("=== JSON round-trip: Python -> Node.js -> Python ===")
records = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 82},
    {"name": "Carol", "score": 78},
]

js_code = """
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
let raw = '';
rl.on('line', l => raw += l);
rl.on('close', () => {
    const data = JSON.parse(raw);
    const sorted = data.sort((a, b) => b.score - a.score);
    const result = sorted.map((r, i) => ({ ...r, rank: i + 1 }));
    process.stdout.write(JSON.stringify(result));
});
"""

try:
    result = Node.run(js_code, input_data=json.dumps(records))
    ranked = result.json()
    print("Ranked by Node.js:")
    for r in ranked:
        print(f"  #{r['rank']} {r['name']} — {r['score']}")
except Exception as e:
    print(f"Node.js skipped: {e}")

print()
print("=== Python -> Go: compute stats ===")
numbers = list(range(1, 11))

go_code = """
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
)

func main() {
    scanner := bufio.NewScanner(os.Stdin)
    scanner.Scan()
    var nums []float64
    json.Unmarshal([]byte(scanner.Text()), &nums)

    sum := 0.0
    for _, n := range nums { sum += n }
    avg := sum / float64(len(nums))
    result := map[string]float64{"sum": sum, "avg": avg, "count": float64(len(nums))}
    out, _ := json.Marshal(result)
    fmt.Println(string(out))
}
"""

try:
    result = Go.run(go_code, input_data=json.dumps(numbers))
    stats = result.json()
    print(f"Go computed: sum={stats['sum']}, avg={stats['avg']}, count={int(stats['count'])}")
except Exception as e:
    print(f"Go skipped: {e}")

print()
print("=== Python -> Rust: string processing ===")
words = ["polyglot", "python", "rust", "interop"]

rust_code = """
use std::io::{self, BufRead};

fn main() {
    let stdin = io::stdin();
    let line = stdin.lock().lines().next().unwrap().unwrap();
    let words: Vec<String> = serde_json::from_str(&line).unwrap_or_else(|_| {
        line.split_whitespace().map(String::from).collect()
    });
    let result: Vec<String> = words.iter().map(|w| {
        let mut c = w.chars();
        match c.next() {
            None => String::new(),
            Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
        }
    }).collect();
    println!("{}", result.join(", "));
}
"""

try:
    result = Rust.run(rust_code, input_data=json.dumps(words))
    print(f"Rust capitalized: {result.text()}")
except Exception as e:
    print(f"Rust skipped (serde_json not available in simple rustc mode): {e}")
    simple_rust = """
use std::io::{self, Read};
fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let cleaned = input.trim().trim_matches('[').trim_matches(']');
    let words: Vec<&str> = cleaned.split(',').map(|s| s.trim().trim_matches('"')).collect();
    let result: Vec<String> = words.iter().map(|w| {
        let mut c = w.chars();
        match c.next() {
            None => String::new(),
            Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
        }
    }).collect();
    println!("{}", result.join(", "));
}
"""
    try:
        import json as j
        result = Rust.run(simple_rust, input_data=j.dumps(words))
        print(f"Rust capitalized: {result.text()}")
    except Exception as e2:
        print(f"Rust skipped: {e2}")

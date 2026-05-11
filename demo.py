from polyrun import Node, C, Cpp, Rust

# --- C code written as a string inside Python ---
c_result = C.run("""
#include <stdio.h>
int main() {
    int numbers[] = {10, 20, 30, 40, 50};
    int sum = 0;
    for (int i = 0; i < 5; i++) sum += numbers[i];
    printf("C computed sum: %d\\n", sum);
    return 0;
}
""")
print(c_result.text())

# --- Rust code written as a string inside Python ---
rust_result = Rust.run("""
fn main() {
    let words = vec!["polyrun", "is", "cool"];
    let sentence = words.join(" ");
    println!("Rust says: {}", sentence);
}
""")
print(rust_result.text())

# --- C++ code written as a string inside Python ---
cpp_result = Cpp.run("""
#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> v = {5, 3, 1, 4, 2};
    std::sort(v.begin(), v.end());
    std::cout << "C++ sorted: ";
    for (int x : v) std::cout << x << " ";
    std::cout << std::endl;
    return 0;
}
""")
print(cpp_result.text())

# --- Node.js code written as a string inside Python ---
js_result = Node.run("""
const msg = ["Node.js", "running", "inside", "Python"].join(" ");
console.log(msg);
""")
print(js_result.text())

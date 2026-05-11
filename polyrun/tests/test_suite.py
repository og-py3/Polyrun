"""
Comprehensive test suite for polyrun.
Runs each language runner and feature multiple times to stress-test correctness.

Run:  python3 polyrun/tests/test_suite.py
"""
import sys
import os
import json
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from polyrun import Node, JS, C, Cpp, Rust, Go, Java
from polyrun.pipeline import Pipeline, Bridge
from polyrun.detect import available
from polyrun.exceptions import CompilationError, LanguageNotFoundError
from polyrun.base import RunResult


# ── helpers ────────────────────────────────────────────────────────────────────

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []
counts = {"pass": 0, "fail": 0, "skip": 0}

def record(name, status, detail=""):
    results.append((name, status, detail))
    counts[status.lower()] += 1
    marker = {"PASS": "✓", "FAIL": "✗", "SKIP": "○"}[status]
    print(f"  {marker} [{status}] {name}" + (f"  ({detail})" if detail else ""))

def run_test(name, fn, *, repeat=1):
    for i in range(repeat):
        label = name if repeat == 1 else f"{name} #{i+1}"
        try:
            fn()
            record(label, PASS)
        except LanguageNotFoundError as e:
            record(label, SKIP, str(e).split(".")[0])
            return
        except AssertionError as e:
            record(label, FAIL, str(e))
        except Exception as e:
            record(label, FAIL, f"{type(e).__name__}: {e}")

langs = available()

def lang_available(key):
    return langs.get(key, False)

# ── Node.js / JavaScript ───────────────────────────────────────────────────────

print("\n── Node.js / JavaScript ─────────────────────────────────────")

def test_node_hello():
    r = Node.run("console.log('hello world')")
    assert r.text() == "hello world", f"got {r.text()!r}"

def test_node_math():
    r = Node.run("console.log(6 * 7)")
    assert r.text() == "42", f"got {r.text()!r}"

def test_node_json_out():
    r = Node.run("process.stdout.write(JSON.stringify({a:1,b:2}))")
    assert r.json() == {"a": 1, "b": 2}

def test_node_stdin():
    r = Node.run(
        "process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(d.trim().toUpperCase()))",
        input_data="hello"
    )
    assert r.text() == "HELLO", f"got {r.text()!r}"

def test_node_multiline():
    code = """
const arr = [1,2,3,4,5];
const sum = arr.reduce((a,b)=>a+b,0);
console.log(sum);
"""
    r = Node.run(code)
    assert r.text() == "15", f"got {r.text()!r}"

def test_node_json_roundtrip():
    code = """
const readline = require('readline');
const rl = readline.createInterface({input:process.stdin});
let raw='';
rl.on('line',l=>raw+=l);
rl.on('close',()=>{
    const d=JSON.parse(raw);
    process.stdout.write(JSON.stringify(d.map(x=>x*2)));
});
"""
    r = Node.run(code, input_data=json.dumps([1,2,3]))
    assert r.json() == [2, 4, 6], f"got {r.json()!r}"

def test_js_alias():
    r = JS.run("console.log('js alias')")
    assert r.text() == "js alias"

def test_node_returnresult():
    r = Node.run("console.log('done')")
    assert isinstance(r, RunResult)
    assert r.returncode == 0

def test_node_lines():
    r = Node.run("console.log('a');\nconsole.log('b');\nconsole.log('c');")
    assert r.lines() == ["a", "b", "c"], f"got {r.lines()!r}"

def test_node_fibonacci():
    code = """
function fib(n){return n<=1?n:fib(n-1)+fib(n-2);}
console.log(fib(10));
"""
    r = Node.run(code)
    assert r.text() == "55", f"got {r.text()!r}"

run_test("Node.js hello world", test_node_hello, repeat=5)
run_test("Node.js arithmetic", test_node_math, repeat=5)
run_test("Node.js JSON output", test_node_json_out, repeat=3)
run_test("Node.js stdin", test_node_stdin, repeat=3)
run_test("Node.js multiline", test_node_multiline, repeat=3)
run_test("Node.js JSON round-trip", test_node_json_roundtrip, repeat=3)
run_test("JS alias", test_js_alias, repeat=2)
run_test("Node.js RunResult type", test_node_returnresult, repeat=2)
run_test("Node.js .lines()", test_node_lines, repeat=2)
run_test("Node.js fibonacci", test_node_fibonacci, repeat=3)

# ── C ─────────────────────────────────────────────────────────────────────────

print("\n── C ────────────────────────────────────────────────────────")

def test_c_hello():
    r = C.run('#include<stdio.h>\nint main(){printf("hello c\\n");return 0;}')
    assert r.text() == "hello c"

def test_c_math():
    r = C.run('#include<stdio.h>\nint main(){printf("%d\\n",6*7);return 0;}')
    assert r.text() == "42"

def test_c_stdin():
    r = C.run(
        '#include<stdio.h>\nint main(){char buf[256];scanf("%s",buf);printf("got:%s\\n",buf);return 0;}',
        input_data="polyglot"
    )
    assert r.text() == "got:polyglot"

def test_c_loop():
    code = """
#include<stdio.h>
int main(){
    int s=0;
    for(int i=1;i<=100;i++) s+=i;
    printf("%d\\n",s);
    return 0;
}
"""
    r = C.run(code)
    assert r.text() == "5050"

def test_c_string():
    code = """
#include<stdio.h>
#include<string.h>
int main(){
    char s[]="polyglot";
    printf("%zu\\n",strlen(s));
    return 0;
}
"""
    r = C.run(code)
    assert r.text() == "8"

def test_c_returncode():
    r = C.run('#include<stdio.h>\nint main(){return 0;}')
    assert r.returncode == 0

run_test("C hello world", test_c_hello, repeat=5)
run_test("C arithmetic", test_c_math, repeat=5)
run_test("C stdin", test_c_stdin, repeat=3)
run_test("C loop sum 1..100", test_c_loop, repeat=3)
run_test("C string length", test_c_string, repeat=2)
run_test("C returncode", test_c_returncode, repeat=2)

# ── C++ ───────────────────────────────────────────────────────────────────────

print("\n── C++ ──────────────────────────────────────────────────────")

def test_cpp_hello():
    r = Cpp.run('#include<iostream>\nint main(){std::cout<<"hello cpp"<<std::endl;return 0;}')
    assert r.text() == "hello cpp"

def test_cpp_math():
    r = Cpp.run('#include<iostream>\nint main(){std::cout<<6*7<<std::endl;return 0;}')
    assert r.text() == "42"

def test_cpp_vector():
    code = """
#include<iostream>
#include<vector>
#include<numeric>
int main(){
    std::vector<int> v={1,2,3,4,5};
    std::cout<<std::accumulate(v.begin(),v.end(),0)<<std::endl;
    return 0;
}
"""
    r = Cpp.run(code)
    assert r.text() == "15"

def test_cpp_string():
    code = """
#include<iostream>
#include<string>
int main(){
    std::string s="polyglot";
    std::cout<<s.length()<<std::endl;
    return 0;
}
"""
    r = Cpp.run(code)
    assert r.text() == "8"

def test_cpp_class():
    code = """
#include<iostream>
class Greeter{
    std::string name;
public:
    Greeter(std::string n):name(n){}
    void greet(){std::cout<<"Hello, "<<name<<"!"<<std::endl;}
};
int main(){Greeter g("Polyglot");g.greet();return 0;}
"""
    r = Cpp.run(code)
    assert r.text() == "Hello, Polyglot!"

def test_cpp_stdin():
    code = """
#include<iostream>
#include<string>
int main(){std::string s;std::cin>>s;std::cout<<s<<" from cpp"<<std::endl;return 0;}
"""
    r = Cpp.run(code, input_data="hello")
    assert r.text() == "hello from cpp"

run_test("C++ hello world", test_cpp_hello, repeat=5)
run_test("C++ arithmetic", test_cpp_math, repeat=5)
run_test("C++ vector accumulate", test_cpp_vector, repeat=3)
run_test("C++ string length", test_cpp_string, repeat=2)
run_test("C++ class", test_cpp_class, repeat=2)
run_test("C++ stdin", test_cpp_stdin, repeat=3)

# ── Rust ──────────────────────────────────────────────────────────────────────

print("\n── Rust ─────────────────────────────────────────────────────")

def test_rust_hello():
    r = Rust.run('fn main(){println!("hello rust");}')
    assert r.text() == "hello rust"

def test_rust_math():
    r = Rust.run('fn main(){println!("{}",6*7);}')
    assert r.text() == "42"

def test_rust_loop():
    code = """
fn main(){
    let s:i32=(1..=100).sum();
    println!("{}",s);
}
"""
    r = Rust.run(code)
    assert r.text() == "5050"

def test_rust_string():
    code = """
fn main(){
    let s="polyglot";
    println!("{}",s.len());
}
"""
    r = Rust.run(code)
    assert r.text() == "8"

def test_rust_vec():
    code = """
fn main(){
    let v=vec![1,2,3,4,5];
    let s:i32=v.iter().sum();
    println!("{}",s);
}
"""
    r = Rust.run(code)
    assert r.text() == "15"

def test_rust_stdin():
    code = """
use std::io::{self,BufRead};
fn main(){
    let stdin=io::stdin();
    let line=stdin.lock().lines().next().unwrap().unwrap();
    println!("got:{}",line.trim());
}
"""
    r = Rust.run(code, input_data="polyglot")
    assert r.text() == "got:polyglot"

def test_rust_fibonacci():
    code = """
fn fib(n:u64)->u64{if n<=1{n}else{fib(n-1)+fib(n-2)}}
fn main(){println!("{}",fib(10));}
"""
    r = Rust.run(code)
    assert r.text() == "55"

run_test("Rust hello world", test_rust_hello, repeat=5)
run_test("Rust arithmetic", test_rust_math, repeat=5)
run_test("Rust loop sum 1..100", test_rust_loop, repeat=3)
run_test("Rust string length", test_rust_string, repeat=2)
run_test("Rust vec sum", test_rust_vec, repeat=3)
run_test("Rust stdin", test_rust_stdin, repeat=3)
run_test("Rust fibonacci", test_rust_fibonacci, repeat=3)

# ── Go ────────────────────────────────────────────────────────────────────────

print("\n── Go ───────────────────────────────────────────────────────")

def test_go_hello():
    r = Go.run('package main\nimport "fmt"\nfunc main(){fmt.Println("hello go")}')
    assert r.text() == "hello go"

def test_go_math():
    r = Go.run('package main\nimport "fmt"\nfunc main(){fmt.Println(6*7)}')
    assert r.text() == "42"

def test_go_loop():
    code = """
package main
import "fmt"
func main(){
    s:=0
    for i:=1;i<=100;i++{s+=i}
    fmt.Println(s)
}
"""
    r = Go.run(code)
    assert r.text() == "5050"

def test_go_stdin():
    code = """
package main
import("bufio";"fmt";"os")
func main(){
    s:=bufio.NewScanner(os.Stdin)
    s.Scan()
    fmt.Println("got:"+s.Text())
}
"""
    r = Go.run(code, input_data="polyglot")
    assert r.text() == "got:polyglot"

def test_go_slice():
    code = """
package main
import "fmt"
func main(){
    v:=[]int{1,2,3,4,5}
    s:=0
    for _,x:=range v{s+=x}
    fmt.Println(s)
}
"""
    r = Go.run(code)
    assert r.text() == "15"

run_test("Go hello world", test_go_hello, repeat=5)
run_test("Go arithmetic", test_go_math, repeat=5)
run_test("Go loop sum 1..100", test_go_loop, repeat=3)
run_test("Go stdin", test_go_stdin, repeat=3)
run_test("Go slice sum", test_go_slice, repeat=2)

# ── Java ──────────────────────────────────────────────────────────────────────

print("\n── Java ─────────────────────────────────────────────────────")

def test_java_hello():
    r = Java.run('public class Main{public static void main(String[] a){System.out.println("hello java");}}')
    assert r.text() == "hello java"

def test_java_math():
    r = Java.run('public class Main{public static void main(String[] a){System.out.println(6*7);}}')
    assert r.text() == "42"

def test_java_loop():
    code = """
public class Main{
    public static void main(String[] args){
        int s=0;
        for(int i=1;i<=100;i++)s+=i;
        System.out.println(s);
    }
}
"""
    r = Java.run(code)
    assert r.text() == "5050"

run_test("Java hello world", test_java_hello, repeat=3)
run_test("Java arithmetic", test_java_math, repeat=3)
run_test("Java loop sum 1..100", test_java_loop, repeat=2)

# ── Pipeline ──────────────────────────────────────────────────────────────────

print("\n── Pipeline ─────────────────────────────────────────────────")

node_double = """
const readline=require('readline');
const rl=readline.createInterface({input:process.stdin});
let d='';rl.on('line',l=>d+=l);
rl.on('close',()=>console.log(parseInt(d.trim())*2));
"""

rust_add1 = """
use std::io::{self,BufRead};
fn main(){
    let stdin=io::stdin();
    let line=stdin.lock().lines().next().unwrap().unwrap();
    let n:i64=line.trim().parse().unwrap();
    println!("{}",n+1);
}
"""

cpp_triple = """
#include<iostream>
int main(){int n;std::cin>>n;std::cout<<n*3<<std::endl;return 0;}
"""

def test_pipeline_node_rust():
    r = (Pipeline().then(Node, node_double).then(Rust, rust_add1).run("10"))
    assert r.text() == "21", f"got {r.text()!r}"

def test_pipeline_node_cpp():
    r = (Pipeline().then(Node, node_double).then(Cpp, cpp_triple).run("5"))
    assert r.text() == "30", f"got {r.text()!r}"

def test_pipeline_three():
    r = (Pipeline()
        .then(Node, node_double)
        .then(Rust, rust_add1)
        .then(Cpp, cpp_triple)
        .run("3"))
    assert r.text() == "21", f"got {r.text()!r}"

run_test("Pipeline Node→Rust", test_pipeline_node_rust, repeat=3)
run_test("Pipeline Node→C++", test_pipeline_node_cpp, repeat=3)
run_test("Pipeline Node→Rust→C++", test_pipeline_three, repeat=2)

# ── Bridge ────────────────────────────────────────────────────────────────────

print("\n── Bridge ───────────────────────────────────────────────────")

js_echo_bridge = """
const readline=require('readline');
const rl=readline.createInterface({input:process.stdin});
let raw='';rl.on('line',l=>raw+=l);
rl.on('close',()=>{
    const d=JSON.parse(raw);
    process.stdout.write(JSON.stringify({...d,processed:true}));
});
"""

js_sort_bridge = """
const readline=require('readline');
const rl=readline.createInterface({input:process.stdin});
let raw='';rl.on('line',l=>raw+=l);
rl.on('close',()=>{
    const arr=JSON.parse(raw);
    process.stdout.write(JSON.stringify(arr.sort((a,b)=>a-b)));
});
"""

def test_bridge_echo():
    r = Bridge.send(Node, js_echo_bridge, data={"x": 42})
    parsed = Bridge.recv(r)
    assert parsed.get("x") == 42
    assert parsed.get("processed") is True

def test_bridge_sort():
    r = Bridge.send(Node, js_sort_bridge, data=[5,3,1,4,2])
    assert Bridge.recv(r) == [1,2,3,4,5]

def test_bridge_strings():
    js = """
const readline=require('readline');
const rl=readline.createInterface({input:process.stdin});
let raw='';rl.on('line',l=>raw+=l);
rl.on('close',()=>{
    const words=JSON.parse(raw);
    process.stdout.write(JSON.stringify(words.map(w=>w.toUpperCase())));
});
"""
    r = Bridge.send(Node, js, data=["hello", "world"])
    assert Bridge.recv(r) == ["HELLO", "WORLD"]

run_test("Bridge echo with flag", test_bridge_echo, repeat=3)
run_test("Bridge sort array", test_bridge_sort, repeat=3)
run_test("Bridge string transform", test_bridge_strings, repeat=3)

# ── Error handling ─────────────────────────────────────────────────────────────

print("\n── Error Handling ───────────────────────────────────────────")

def test_compile_error_rust():
    try:
        Rust.run("fn main(){ this_wont_compile }")
        assert False, "should have raised"
    except CompilationError:
        pass

def test_compile_error_c():
    try:
        C.run("int main(){ this_wont_compile }")
        assert False, "should have raised"
    except CompilationError:
        pass

def test_compile_error_cpp():
    try:
        Cpp.run("int main(){ this_wont_compile }")
        assert False, "should have raised"
    except CompilationError:
        pass

def test_runtime_error_node():
    from polyrun.exceptions import RuntimeError as PolyRE
    try:
        Node.run("process.exit(1)")
        assert False, "should have raised"
    except PolyRE:
        pass

def test_not_found_error():
    class FakeRunner(type(Node)):
        language = "Fake"
    runner = FakeRunner()
    try:
        runner._check_binary("this_binary_does_not_exist_polyrun")
        assert False, "should have raised"
    except LanguageNotFoundError:
        pass

run_test("CompilationError from Rust", test_compile_error_rust, repeat=2)
run_test("CompilationError from C", test_compile_error_c, repeat=2)
run_test("CompilationError from C++", test_compile_error_cpp, repeat=2)
run_test("RuntimeError from Node.js", test_runtime_error_node, repeat=2)
run_test("LanguageNotFoundError", test_not_found_error, repeat=2)

# ── Summary ───────────────────────────────────────────────────────────────────

print()
print("=" * 56)
total = counts["pass"] + counts["fail"] + counts["skip"]
print(f"  Results: {total} tests  |  "
      f"✓ {counts['pass']} passed  |  "
      f"✗ {counts['fail']} failed  |  "
      f"○ {counts['skip']} skipped")
print("=" * 56)

if counts["fail"]:
    print("\nFailed tests:")
    for name, status, detail in results:
        if status == "FAIL":
            print(f"  ✗ {name}: {detail}")

sys.exit(1 if counts["fail"] else 0)

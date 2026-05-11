from .runners.java import JavaRunner
from .runners.node import NodeRunner
from .runners.c import CRunner
from .runners.cpp import CppRunner
from .runners.rust import RustRunner
from .runners.go import GoRunner

Java = JavaRunner()
Node = NodeRunner()
JS = NodeRunner()
C = CRunner()
Cpp = CppRunner()
Rust = RustRunner()
Go = GoRunner()

__all__ = ["Java", "Node", "JS", "C", "Cpp", "Rust", "Go"]
__version__ = "0.1.0"

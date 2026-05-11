from setuptools import setup, find_packages

setup(
    name="polyrun",
    version="0.1.0",
    description="Run and combine Java, Node.js, C, C++, Rust, Go, and JavaScript — all from Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="https://github.com/your-username/polyrun",
    python_requires=">=3.8",
    packages=find_packages(include=["polyrun", "polyrun.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    keywords="polyglot runner java node nodejs javascript c cpp rust go multiplatform",
)

import shutil


LANGUAGES = {
    "Node.js / JavaScript": ["node"],
    "Java": ["javac", "java"],
    "C": ["gcc"],
    "C++": ["g++"],
    "Rust": ["rustc"],
    "Go": ["go"],
}


def available():
    """Return a dict of language names to availability status."""
    status = {}
    for lang, binaries in LANGUAGES.items():
        status[lang] = all(shutil.which(b) is not None for b in binaries)
    return status


def check():
    """Print a human-readable availability report."""
    status = available()
    print("Polyglot — language availability")
    print("-" * 36)
    for lang, ok in status.items():
        marker = "OK" if ok else "MISSING"
        print(f"  {'[OK]' if ok else '[--]'}  {lang}")
    print()
    missing = [lang for lang, ok in status.items() if not ok]
    if missing:
        print(f"  Not available: {', '.join(missing)}")
        print("  Install the required toolchain and make sure it is on your PATH.")
    else:
        print("  All languages are available!")

class PolyglotError(Exception):
    pass

class CompilationError(PolyglotError):
    def __init__(self, language, stderr):
        self.language = language
        self.stderr = stderr
        super().__init__(f"[{language}] Compilation error:\n{stderr}")

class RuntimeError(PolyglotError):
    def __init__(self, language, stderr, returncode):
        self.language = language
        self.stderr = stderr
        self.returncode = returncode
        super().__init__(f"[{language}] Runtime error (exit {returncode}):\n{stderr}")

class LanguageNotFoundError(PolyglotError):
    def __init__(self, language, binary):
        self.language = language
        self.binary = binary
        super().__init__(
            f"[{language}] Required tool '{binary}' not found. "
            f"Please install it and make sure it is on your PATH."
        )

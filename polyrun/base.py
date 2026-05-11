import subprocess
import tempfile
import os
import shutil
import json
from .exceptions import CompilationError, RuntimeError, LanguageNotFoundError


class RunResult:
    def __init__(self, stdout, stderr, returncode, language):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.language = language

    def json(self):
        return json.loads(self.stdout)

    def text(self):
        return self.stdout.strip()

    def lines(self):
        return self.stdout.strip().splitlines()

    def __str__(self):
        return self.stdout.strip()

    def __repr__(self):
        return f"RunResult(language={self.language!r}, returncode={self.returncode}, stdout={self.stdout!r})"


class BaseRunner:
    language = "unknown"

    def _check_binary(self, binary):
        if shutil.which(binary) is None:
            raise LanguageNotFoundError(self.language, binary)

    def _run_subprocess(self, cmd, cwd=None, input_data=None, timeout=30):
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                input=input_data,
                timeout=timeout,
            )
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError(self.language, "Process timed out", -1)
        except FileNotFoundError as e:
            raise LanguageNotFoundError(self.language, cmd[0]) from e

    def _make_tempdir(self):
        return tempfile.mkdtemp(prefix=f"polyglot_{self.language}_")

    def run(self, code, input_data=None, timeout=30, env=None):
        raise NotImplementedError

    def call(self, code, args=None, input_data=None, timeout=30):
        raise NotImplementedError

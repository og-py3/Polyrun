import os
import shutil
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class GoRunner(BaseRunner):
    language = "Go"

    def run(self, code, input_data=None, timeout=30, env=None):
        self._check_binary("go")
        tmpdir = self._make_tempdir()
        try:
            src_path = os.path.join(tmpdir, "main.go")
            with open(src_path, "w") as f:
                f.write(code)

            run_result = self._run_subprocess(
                ["go", "run", "main.go"],
                cwd=tmpdir,
                input_data=input_data,
                timeout=timeout,
            )
            if run_result.returncode != 0:
                raise PolyRuntimeError(self.language, run_result.stderr, run_result.returncode)
            return RunResult(run_result.stdout, run_result.stderr, run_result.returncode, self.language)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def call(self, code, args=None, input_data=None, timeout=30):
        args_str = ", ".join(str(a) for a in (args or []))
        wrapper = f"""
package main

import "fmt"

{code}

func main() {{
    result := __polyCall({args_str})
    fmt.Println(result)
}}
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout)

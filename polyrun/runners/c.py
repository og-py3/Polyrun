import os
import shutil
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class CRunner(BaseRunner):
    language = "C"

    def run(self, code, input_data=None, timeout=30, env=None, flags=None):
        self._check_binary("gcc")
        tmpdir = self._make_tempdir()
        try:
            src_path = os.path.join(tmpdir, "program.c")
            out_path = os.path.join(tmpdir, "program")
            with open(src_path, "w") as f:
                f.write(code)

            compile_cmd = ["gcc", "program.c", "-o", "program"] + (flags or [])
            compile_result = self._run_subprocess(compile_cmd, cwd=tmpdir, timeout=timeout)
            if compile_result.returncode != 0:
                raise CompilationError(self.language, compile_result.stderr)

            run_result = self._run_subprocess(
                [out_path],
                cwd=tmpdir,
                input_data=input_data,
                timeout=timeout,
            )
            if run_result.returncode != 0:
                raise PolyRuntimeError(self.language, run_result.stderr, run_result.returncode)
            return RunResult(run_result.stdout, run_result.stderr, run_result.returncode, self.language)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def call(self, code, args=None, input_data=None, timeout=30, flags=None):
        args_str = ", ".join(str(a) for a in (args or []))
        wrapper = f"""
#include <stdio.h>
{code}

int main() {{
    printf("%s\\n", __poly_call({args_str}));
    return 0;
}}
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout, flags=flags)

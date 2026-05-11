import os
import shutil
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class CppRunner(BaseRunner):
    language = "C++"

    def run(self, code, input_data=None, timeout=30, env=None, flags=None, std="c++17"):
        self._check_binary("g++")
        tmpdir = self._make_tempdir()
        try:
            src_path = os.path.join(tmpdir, "program.cpp")
            out_path = os.path.join(tmpdir, "program")
            with open(src_path, "w") as f:
                f.write(code)

            compile_cmd = ["g++", f"-std={std}", "program.cpp", "-o", "program"] + (flags or [])
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

    def call(self, code, args=None, input_data=None, timeout=30, flags=None, std="c++17"):
        args_str = ", ".join(str(a) for a in (args or []))
        wrapper = f"""
#include <iostream>
{code}

int main() {{
    std::cout << __poly_call({args_str}) << std::endl;
    return 0;
}}
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout, flags=flags, std=std)

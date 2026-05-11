import os
import shutil
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class RustRunner(BaseRunner):
    language = "Rust"

    def run(self, code, input_data=None, timeout=60, env=None):
        self._check_binary("rustc")
        tmpdir = self._make_tempdir()
        try:
            src_path = os.path.join(tmpdir, "main.rs")
            out_path = os.path.join(tmpdir, "main")
            with open(src_path, "w") as f:
                f.write(code)

            compile_result = self._run_subprocess(
                ["rustc", "main.rs", "-o", "main"],
                cwd=tmpdir,
                timeout=timeout,
            )
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

    def call(self, code, args=None, input_data=None, timeout=60):
        args_str = ", ".join(str(a) for a in (args or []))
        wrapper = f"""
{code}

fn main() {{
    let result = __poly_call({args_str});
    println!("{{}}", result);
}}
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout)

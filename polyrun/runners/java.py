import os
import re
import json
import shutil
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class JavaRunner(BaseRunner):
    language = "Java"

    def _extract_class_name(self, code):
        match = re.search(r"public\s+class\s+(\w+)", code)
        if match:
            return match.group(1)
        match = re.search(r"class\s+(\w+)", code)
        if match:
            return match.group(1)
        return "Main"

    def run(self, code, input_data=None, timeout=30, env=None):
        self._check_binary("javac")
        self._check_binary("java")
        tmpdir = self._make_tempdir()
        try:
            class_name = self._extract_class_name(code)
            src_path = os.path.join(tmpdir, f"{class_name}.java")
            with open(src_path, "w") as f:
                f.write(code)

            compile_result = self._run_subprocess(
                ["javac", f"{class_name}.java"],
                cwd=tmpdir,
                timeout=timeout,
            )
            if compile_result.returncode != 0:
                raise CompilationError(self.language, compile_result.stderr)

            run_result = self._run_subprocess(
                ["java", class_name],
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
        args_str = ", ".join(json.dumps(a) for a in (args or []))
        wrapper = f"""
public class PolyMain {{
    public static void main(String[] args) {{
        Object result = run({args_str});
        if (result != null) System.out.println(result);
    }}
    {code}
}}
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout)

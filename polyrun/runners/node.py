import os
import json
from ..base import BaseRunner, RunResult
from ..exceptions import CompilationError, RuntimeError as PolyRuntimeError


class NodeRunner(BaseRunner):
    language = "Node.js"

    def run(self, code, input_data=None, timeout=30, env=None):
        self._check_binary("node")
        tmpdir = self._make_tempdir()
        try:
            script_path = os.path.join(tmpdir, "script.js")
            with open(script_path, "w") as f:
                f.write(code)
            result = self._run_subprocess(
                ["node", script_path],
                cwd=tmpdir,
                input_data=input_data,
                timeout=timeout,
            )
            if result.returncode != 0:
                raise PolyRuntimeError(self.language, result.stderr, result.returncode)
            return RunResult(result.stdout, result.stderr, result.returncode, self.language)
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)

    def call(self, code, args=None, input_data=None, timeout=30):
        args_json = json.dumps(args if args is not None else [])
        wrapper = f"""
const __args = {args_json};
const __result = (function() {{
{code}
}})(...__args);
if (__result !== undefined) process.stdout.write(JSON.stringify(__result));
"""
        return self.run(wrapper, input_data=input_data, timeout=timeout)

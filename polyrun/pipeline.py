import json
from .base import RunResult


class Pipeline:
    """
    Chain multiple language runners together, passing output from one
    as input to the next.

    Example:
        result = (
            Pipeline()
            .then(Node, "process.stdin.resume(); let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>console.log(d.trim().toUpperCase()))")
            .then(Go, 'package main\\nimport ("fmt";"os";"bufio")\\nfunc main(){s:=bufio.NewScanner(os.Stdin);s.Scan();fmt.Println("Go got:", s.Text())}')
            .run("hello world")
        )
    """

    def __init__(self):
        self._steps = []

    def then(self, runner, code):
        self._steps.append((runner, code))
        return self

    def run(self, initial_input=None, timeout=30):
        if not self._steps:
            raise ValueError("Pipeline has no steps. Add steps with .then(runner, code).")

        current_input = initial_input
        last_result = None

        for runner, code in self._steps:
            result = runner.run(code, input_data=current_input, timeout=timeout)
            current_input = result.stdout
            last_result = result

        return last_result


class Bridge:
    """
    Pass data between two languages using JSON serialization.

    Example:
        result = Bridge.send(Node, js_code, data={"key": "value"})
        python_dict = result.json()
    """

    @staticmethod
    def send(runner, code, data=None, timeout=30):
        input_data = json.dumps(data) if data is not None else None
        return runner.run(code, input_data=input_data, timeout=timeout)

    @staticmethod
    def recv(result):
        return result.json()

"""Runs an arbitrary python script as a subprocess on a background thread and
streams its output into a queue the main window polls. Deliberately shells
out instead of importing the target script -- run_sim.py/gen_variations.py/
mutate_variations.py's functions are entangled with docker/argparse/sys.exit
side effects, so a subprocess boundary is the only clean way to reuse them
from the GUI. One shared instance runs whichever of Run/Generate/Combine is
active -- they're mutually exclusive anyway (same materialized schematic,
same JSONL logs, one docker container)."""
import queue
import subprocess
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_SIM = PROJECT_ROOT / "tools" / "run_sim.py"
# mutate_variations.py does `from tools.run_sim import ...` etc, so unlike
# RUN_SIM (self-contained, no internal package imports) it must be launched
# with `-m` -- a direct file-path invocation can't resolve the `tools`
# package (same reason gen_variations.py's own docstring documents `-m`
# usage). See App._generate_from_selected/_combine_selected for the argv
# this module name is used to build.
MUTATE_VARIATIONS_MODULE = "tools.mutate_variations"


class RunTrigger:
    def __init__(self, on_line, on_done):
        self.on_line = on_line
        self.on_done = on_done
        self._queue = queue.Queue()
        self._process = None
        self._thread = None

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self, argv):
        """argv: full command list, e.g. [sys.executable, str(RUN_SIM), "--force"]."""
        if self.running:
            return
        self._thread = threading.Thread(target=self._run, args=(argv,), daemon=True)
        self._thread.start()

    def cancel(self):
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()

    def _run(self, args):
        self._process = subprocess.Popen(
            args, cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for line in self._process.stdout:
            self._queue.put(line.rstrip("\n"))
        returncode = self._process.wait()
        self._queue.put(None)  # sentinel: process finished
        self._queue.put(returncode)

    def poll(self):
        """Call periodically (e.g. via Tk.after) from the main thread. Drains
        available output lines and detects completion."""
        finished = False
        returncode = None
        try:
            while True:
                item = self._queue.get_nowait()
                if item is None:
                    finished = True
                    returncode = self._queue.get_nowait()
                    continue
                if finished:
                    continue
                self.on_line(item)
        except queue.Empty:
            pass
        if finished:
            self._process = None
            self._thread = None
            self.on_done(returncode)

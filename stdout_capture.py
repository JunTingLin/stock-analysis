import sys
import io
from contextlib import redirect_stdout

class StdoutCapture:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stringio = io.StringIO()
        sys.stdout = self._stringio
        return self._stringio

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._stdout

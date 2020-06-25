from typing import List
from io import TextIOWrapper


class FastCSVWriter:
    def __init__(self, stream: TextIOWrapper, max_batch_size: int = 10000):
        super().__init__()
        self.stream: TextIOWrapper = stream
        self.max_batch_size = max_batch_size
        self._batch = []

    @classmethod
    def to_csv_line(cls, cols: List[str]):
        return ",".join([str(v) for v in cols]) + "\n"

    def write_lines(self, lines: List[str]):
        self.stream.writelines(lines)
        self.stream.write("\n")

    def write_cols(self, cols):
        self._batch.append(cols)
        if len(self._batch) >= self.max_batch_size:
            self.flush()

    def flush(self):
        self.write_lines([self.to_csv_line(cols) for cols in self._batch])
        self.stream.flush()
        self._batch.clear()

    def close(self):
        self.stream.close()

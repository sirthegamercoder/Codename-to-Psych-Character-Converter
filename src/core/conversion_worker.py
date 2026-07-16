import json
import os
from typing import Dict, Optional, Any

from PySide6.QtCore import QThread, Signal

from core.converters.codename_converter import CodenameConverter
from core.converters.vslice_converter import VSliceConverter


class ConversionWorker(QThread):
    finished = Signal(dict, str)
    error = Signal(str, str)
    progress = Signal(str, str)

    def __init__(
        self,
        content: str,
        input_path: str,
        output_path: str = None,
        file_type: str = "xml",
    ):
        super().__init__()
        self.content = content
        self.input_path = input_path
        self.output_path = output_path
        self.file_type = file_type

    def run(self):
        try:
            self.progress.emit(f"Parsing file...", self.input_path)

            if self.file_type == "xml":
                converter = CodenameConverter()
                result = converter.convert(self.content)
            else:
                converter = VSliceConverter()
                result = converter.convert(self.content)

            if result:
                if self.output_path:
                    self.progress.emit(
                        f"Saving to {self.output_path}...", self.input_path
                    )
                    with open(self.output_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    self.progress.emit(
                        f"Completed: {os.path.basename(self.input_path)}",
                        self.input_path,
                    )
                self.finished.emit(result, self.output_path)
            else:
                self.error.emit(
                    f"Failed to convert {self.file_type.upper()} to Psych format",
                    self.input_path,
                )
        except Exception as e:
            self.error.emit(f"Conversion error: {str(e)}", self.input_path)

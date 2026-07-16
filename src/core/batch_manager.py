import os
from typing import List, Tuple

from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker

from core.conversion_worker import ConversionWorker


class BatchConversionManager(QThread):
    progress_updated = Signal(int, int, str)
    file_completed = Signal(str, bool, str)
    batch_finished = Signal(int, int)
    log_message = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.files_to_process = []
        self.output_directory = ""
        self.is_running = False
        self.mutex = QMutex()

    def setup_batch(self, files: List[Tuple[str, str, str]], output_dir: str):
        self.files_to_process = files
        self.output_directory = output_dir
        self.is_running = True

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_running = False

    def run(self):
        success_count = 0
        fail_count = 0
        total = len(self.files_to_process)

        for idx, (input_path, output_path, file_type) in enumerate(
            self.files_to_process
        ):
            if not self.is_running:
                self.log_message.emit("Batch processing stopped by user", "warning")
                break

            self.progress_updated.emit(idx + 1, total, os.path.basename(input_path))
            self.log_message.emit(
                f"Processing: {os.path.basename(input_path)} ({file_type.upper()})",
                "info",
            )

            try:
                with open(input_path, "r", encoding="utf-8") as f:
                    content = f.read()

                worker = ConversionWorker(content, input_path, output_path, file_type)

                worker_finished = False
                worker_success = False
                worker_error_msg = ""

                def on_finished(result, out_path):
                    nonlocal worker_finished, worker_success
                    worker_finished = True
                    worker_success = True

                def on_error(error_msg, in_path):
                    nonlocal worker_finished, worker_success, worker_error_msg
                    worker_finished = True
                    worker_success = False
                    worker_error_msg = error_msg

                worker.finished.connect(on_finished)
                worker.error.connect(on_error)

                worker.run()

                while not worker_finished and self.is_running:
                    self.msleep(10)

                if worker_success:
                    success_count += 1
                    self.file_completed.emit(input_path, True, "Successfully converted")
                    self.log_message.emit(
                        f"Success: {os.path.basename(input_path)}", "success"
                    )
                else:
                    fail_count += 1
                    self.file_completed.emit(input_path, False, worker_error_msg)
                    self.log_message.emit(
                        f"Failed: {os.path.basename(input_path)} - {worker_error_msg}",
                        "error",
                    )

            except Exception as e:
                fail_count += 1
                error_msg = str(e)
                self.file_completed.emit(input_path, False, error_msg)
                self.log_message.emit(
                    f"Error: {os.path.basename(input_path)} - {error_msg}", "error"
                )

            if not self.is_running:
                break

        self.batch_finished.emit(success_count, fail_count)
        self.log_message.emit(
            f"Batch processing completed: {success_count} succeeded, {fail_count} failed",
            "success" if fail_count == 0 else "warning",
        )

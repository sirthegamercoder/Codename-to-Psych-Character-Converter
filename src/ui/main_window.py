import os
from typing import Dict

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QGroupBox,
    QProgressBar,
    QSplitter,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction
from qtawesome import icon as qta_icon
import webbrowser

from core import ConversionWorker, BatchConversionManager
from ui.theme import apply_theme


class CharacterConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.current_json_path = None
        self.current_content = None
        self.current_file_type = None
        self.batch_files = []
        self.batch_manager = None
        self.output_dir = None
        self.init_ui()
        apply_theme(self)

    def init_ui(self):
        self.setMinimumSize(950, 700)
        self.resize(950, 700)
        self.center()
        self.create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Character Converter Toolbox")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)

        single_group = QGroupBox("Single File Conversion")
        single_layout = QVBoxLayout(single_group)

        file_layout = QHBoxLayout()
        self.input_path_label = QLabel("No file selected")
        self.input_path_label.setWordWrap(True)
        self.input_path_label.setStyleSheet("color: #888888;")

        file_buttons_layout = QVBoxLayout()
        file_buttons_layout.setSpacing(3)

        self.select_xml_btn = QPushButton("Select XML")
        self.select_xml_btn.clicked.connect(lambda: self.select_file("xml"))
        self.select_xml_btn.setIcon(qta_icon("fa6s.file", color="white"))
        self.select_xml_btn.setMaximumWidth(120)

        self.select_json_btn = QPushButton("Select JSON")
        self.select_json_btn.clicked.connect(lambda: self.select_file("json"))
        self.select_json_btn.setIcon(qta_icon("fa6s.file", color="white"))
        self.select_json_btn.setMaximumWidth(120)

        file_buttons_layout.addWidget(self.select_xml_btn)
        file_buttons_layout.addWidget(self.select_json_btn)

        file_layout.addLayout(file_buttons_layout)
        file_layout.addWidget(self.input_path_label, 1)
        single_layout.addLayout(file_layout)

        self.file_type_label = QLabel("No file loaded")
        self.file_type_label.setStyleSheet("color: #888888; font-style: italic;")
        single_layout.addWidget(self.file_type_label)

        output_file_layout = QHBoxLayout()
        self.output_path_label = QLabel("No output path selected")
        self.output_path_label.setWordWrap(True)
        self.output_path_label.setStyleSheet("color: #888888;")

        self.select_output_btn = QPushButton("Select Output Path")
        self.select_output_btn.clicked.connect(self.select_output_path)
        self.select_output_btn.setIcon(qta_icon("fa6s.folder-open", color="white"))

        output_file_layout.addWidget(self.select_output_btn)
        output_file_layout.addWidget(self.output_path_label, 1)
        single_layout.addLayout(output_file_layout)

        self.convert_btn = QPushButton("Convert to Psych JSON")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.clicked.connect(self.start_conversion)
        convert_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.convert_btn.setFont(convert_font)
        self.convert_btn.setIcon(qta_icon("fa6s.arrow-right", color="white"))

        single_layout.addWidget(self.convert_btn)

        left_layout.addWidget(single_group)
        left_layout.addStretch()

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)

        batch_group = QGroupBox("Batch Conversion")
        batch_layout = QVBoxLayout(batch_group)

        batch_controls = QHBoxLayout()
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_batch_files)
        self.add_files_btn.setIcon(qta_icon("fa6s.plus", color="white"))

        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_batch_folder)
        self.add_folder_btn.setIcon(qta_icon("fa6s.folder-plus", color="white"))

        self.clear_files_btn = QPushButton("Clear All")
        self.clear_files_btn.clicked.connect(self.clear_batch_files)
        self.clear_files_btn.setIcon(qta_icon("fa6s.delete-left", color="white"))

        batch_controls.addWidget(self.add_files_btn)
        batch_controls.addWidget(self.add_folder_btn)
        batch_controls.addWidget(self.clear_files_btn)
        batch_controls.addStretch()
        batch_layout.addLayout(batch_controls)

        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("No output directory selected")
        self.output_dir_label.setWordWrap(True)
        self.output_dir_label.setStyleSheet("color: #888888;")

        self.select_output_dir_btn = QPushButton("Select Output Directory")
        self.select_output_dir_btn.clicked.connect(self.select_output_directory)
        self.select_output_dir_btn.setIcon(qta_icon("fa6s.folder-open", color="white"))

        output_dir_layout.addWidget(self.select_output_dir_btn)
        output_dir_layout.addWidget(self.output_dir_label, 1)
        batch_layout.addLayout(output_dir_layout)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self.file_list_widget.setAlternatingRowColors(True)
        batch_layout.addWidget(QLabel("Files to convert:"))
        batch_layout.addWidget(self.file_list_widget)

        batch_action_layout = QHBoxLayout()
        self.remove_selected_btn = QPushButton("Remove Selected")
        self.remove_selected_btn.clicked.connect(self.remove_selected_files)
        self.remove_selected_btn.setIcon(qta_icon("fa6s.trash", color="white"))

        self.batch_convert_btn = QPushButton("Start Batch Conversion")
        self.batch_convert_btn.setMinimumHeight(35)
        self.batch_convert_btn.clicked.connect(self.start_batch_conversion)
        batch_convert_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        self.batch_convert_btn.setFont(batch_convert_font)
        self.batch_convert_btn.setIcon(qta_icon("fa6s.play", color="white"))

        batch_action_layout.addWidget(self.remove_selected_btn)
        batch_action_layout.addStretch()
        batch_action_layout.addWidget(self.batch_convert_btn)
        batch_layout.addLayout(batch_action_layout)

        right_layout.addWidget(batch_group)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 550])

        main_layout.addWidget(splitter)

        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setVisible(False)
        status_layout.addWidget(self.batch_progress_bar)

        self.current_file_label = QLabel("")
        self.current_file_label.setVisible(False)
        self.current_file_label.setStyleSheet("color: #FFA500; font-style: italic;")
        status_layout.addWidget(self.current_file_label)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #4CAF50;")
        status_layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setPlaceholderText("Conversion log will appear here...")
        status_layout.addWidget(QLabel("Log:"))
        status_layout.addWidget(self.log_text)

        main_layout.addWidget(status_group)

        self.single_progress_bar = QProgressBar()
        self.single_progress_bar.setVisible(False)
        main_layout.insertWidget(3, self.single_progress_bar)

        self.stop_batch_btn = QPushButton("Stop Batch")
        self.stop_batch_btn.setVisible(False)
        self.stop_batch_btn.clicked.connect(self.stop_batch_conversion)
        self.stop_batch_btn.setStyleSheet("background-color: #f44336;")
        self.stop_batch_btn.setIcon(qta_icon("fa6s.stop", color="white"))
        batch_action_layout.addWidget(self.stop_batch_btn)

    def create_toolbar(self):
        toolbar = self.addToolBar("Navigation")
        toolbar.setMovable(False)

        web_action = QAction("Try web version", self)
        web_action.setIcon(qta_icon("fa6s.globe", color="white"))
        web_action.triggered.connect(self.open_website)
        toolbar.addAction(web_action)

        bug_report = QAction("Report bug in GitHub", self)
        bug_report.setIcon(qta_icon("fa6s.bug", color="white"))
        bug_report.triggered.connect(self.report_bug)
        toolbar.addAction(bug_report)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

    def open_website(self):
        webbrowser.open(
            "https://sirthegamercoder.github.io/Character-Converter-Toolbox/"
        )

    def report_bug(self):
        webbrowser.open(
            "https://github.com/sirthegamercoder/Character-Converter-Toolbox/issues"
        )

    def center(self):
        frame_geo = self.frameGeometry()
        screen = QApplication.primaryScreen()
        available_geo = screen.availableGeometry()
        center_point = available_geo.center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

    def add_log_message(self, message: str, msg_type: str = "info"):
        colors = {
            "info": "#FFFFFF",
            "success": "#4CAF50",
            "error": "#f44336",
            "warning": "#FFA500",
        }
        color = colors.get(msg_type, "#FFFFFF")
        self.log_text.append(f'<span style="color:{color};">{message}</span>')
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def select_file(self, file_type: str):
        if file_type == "xml":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select XML Character File",
                "",
                "XML Files (*.xml);;All Files (*.*)",
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select V-Slice JSON Character File",
                "",
                "JSON Files (*.json);;All Files (*.*)",
            )

        if file_path:
            self.current_file_path = file_path
            self.current_file_type = file_type
            self.input_path_label.setText(file_path)
            self.input_path_label.setStyleSheet("color: #4CAF50;")

            file_type_display = (
                "XML (Codename Engine)" if file_type == "xml" else "JSON (V-Slice)"
            )
            self.file_type_label.setText(f"Loaded: {file_type_display}")
            self.file_type_label.setStyleSheet("color: #4CAF50;")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.current_content = content
                    self.status_label.setText(
                        f"Loaded {file_type_display} file: {os.path.basename(file_path)}"
                    )
                    self.status_label.setStyleSheet("color: #4CAF50;")
                    self.add_log_message(
                        f"Loaded {file_type_display} file: {file_path}", "success"
                    )

                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_dir = os.path.dirname(file_path)
                    self.current_json_path = os.path.join(
                        output_dir, f"{base_name}.json"
                    )
                    self.output_path_label.setText(self.current_json_path)
                    self.output_path_label.setStyleSheet("color: #4CAF50;")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
                self.add_log_message(f"Failed to load file: {str(e)}", "error")

    def select_output_path(self):
        start_dir = ""
        output_name = "character.json"
        if self.current_file_path:
            start_dir = os.path.dirname(self.current_file_path)
            base_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
            output_name = f"{base_name}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Psych JSON Character File",
            os.path.join(start_dir, output_name),
            "JSON Files (*.json);;All Files (*.*)",
        )

        if file_path:
            self.current_json_path = file_path
            self.output_path_label.setText(file_path)
            self.output_path_label.setStyleSheet("color: #4CAF50;")

    def start_conversion(self):
        if not self.current_content or not self.current_content.strip():
            QMessageBox.warning(self, "Warning", "Please load a file first.")
            return

        if not self.current_json_path:
            self.select_output_path()
            if not self.current_json_path:
                return

        self.convert_btn.setEnabled(False)
        self.select_xml_btn.setEnabled(False)
        self.select_json_btn.setEnabled(False)
        self.select_output_btn.setEnabled(False)
        self.single_progress_bar.setVisible(True)
        self.single_progress_bar.setRange(0, 0)

        content = self.current_content
        output_path = self.current_json_path
        file_type = self.current_file_type

        self.worker = ConversionWorker(
            content, self.current_file_path, output_path, file_type
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)
        self.worker.start()

    def update_progress(self, message: str, input_path: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #FFA500;")

    def on_conversion_finished(self, result: Dict, output_path: str):
        self.convert_btn.setEnabled(True)
        self.select_xml_btn.setEnabled(True)
        self.select_json_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.single_progress_bar.setVisible(False)

        if output_path:
            QMessageBox.information(
                self,
                "Success",
                f"Character converted and saved to:\n{output_path}",
            )
            self.add_log_message(f"Successfully converted to: {output_path}", "success")

        self.status_label.setText("Conversion completed successfully!")
        self.status_label.setStyleSheet("color: #4CAF50;")

    def on_conversion_error(self, error_msg: str, input_path: str):
        self.convert_btn.setEnabled(True)
        self.select_xml_btn.setEnabled(True)
        self.select_json_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.single_progress_bar.setVisible(False)

        QMessageBox.critical(self, "Conversion Error", error_msg)
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #f44336;")
        self.add_log_message(f"Conversion error: {error_msg}", "error")

    def add_batch_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Character Files",
            "",
            "Character Files (*.xml *.json);;XML Files (*.xml);;JSON Files (*.json);;All Files (*.*)",
        )

        for file_path in file_paths:
            if file_path not in [f[0] for f in self.batch_files]:
                if file_path.lower().endswith(".xml"):
                    file_type = "xml"
                elif file_path.lower().endswith(".json"):
                    file_type = "json"
                else:
                    continue
                self.batch_files.append((file_path, "", file_type))
                self.add_file_to_list(file_path, "", file_type)

        self.update_batch_ui_state()

    def add_batch_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder containing character files"
        )

        if folder_path:
            files = []
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.lower().endswith(".xml") or filename.lower().endswith(
                        ".json"
                    ):
                        full_path = os.path.join(root, filename)
                        file_type = (
                            "xml" if filename.lower().endswith(".xml") else "json"
                        )
                        files.append((full_path, file_type))

            for file_path, file_type in files:
                if file_path not in [f[0] for f in self.batch_files]:
                    self.batch_files.append((file_path, "", file_type))
                    self.add_file_to_list(file_path, "", file_type)

            self.add_log_message(
                f"Added {len(files)} files from folder: {folder_path}", "info"
            )
            self.update_batch_ui_state()

    def add_file_to_list(self, file_path: str, output_path: str, file_type: str):
        file_type_display = "XML" if file_type == "xml" else "JSON"
        item_text = f"[{file_type_display}] {os.path.basename(file_path)}"
        item = QListWidgetItem(item_text)
        item.setToolTip(
            f"Input: {file_path}\nType: {file_type_display}\nOutput: {output_path if output_path else 'Not set'}"
        )
        item.setData(Qt.ItemDataRole.UserRole, (file_path, output_path, file_type))
        self.file_list_widget.addItem(item)

    def clear_batch_files(self):
        self.batch_files.clear()
        self.file_list_widget.clear()
        self.update_batch_ui_state()
        self.add_log_message("Cleared all files from batch list", "info")

    def remove_selected_files(self):
        selected_items = self.file_list_widget.selectedItems()
        for item in selected_items:
            file_path, _, _ = item.data(Qt.ItemDataRole.UserRole)
            self.batch_files = [f for f in self.batch_files if f[0] != file_path]
            self.file_list_widget.takeItem(self.file_list_widget.row(item))
        self.update_batch_ui_state()
        self.add_log_message(
            f"Removed {len(selected_items)} file(s) from batch list", "info"
        )

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory for Batch Conversion"
        )

        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(directory)
            self.output_dir_label.setStyleSheet("color: #4CAF50;")

            updated_files = []
            for input_path, _, file_type in self.batch_files:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(directory, f"{base_name}.json")
                updated_files.append((input_path, output_path, file_type))

            self.batch_files = updated_files

            self.file_list_widget.clear()
            for input_path, output_path, file_type in self.batch_files:
                self.add_file_to_list(input_path, output_path, file_type)

            self.add_log_message(f"Output directory set to: {directory}", "success")
            self.update_batch_ui_state()

    def update_batch_ui_state(self):
        has_files = len(self.batch_files) > 0
        has_output_dir = hasattr(self, "output_dir") and self.output_dir

        self.batch_convert_btn.setEnabled(has_files and has_output_dir)
        self.clear_files_btn.setEnabled(has_files)
        self.remove_selected_btn.setEnabled(
            len(self.file_list_widget.selectedItems()) > 0
        )

    def start_batch_conversion(self):
        if not self.batch_files:
            QMessageBox.warning(self, "Warning", "Please add files to convert.")
            return

        if not hasattr(self, "output_dir") or not self.output_dir:
            QMessageBox.warning(self, "Warning", "Please select an output directory.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Batch Conversion",
            f"Are you sure you want to convert {len(self.batch_files)} file(s)?\n\n"
            f"Output directory: {self.output_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.set_batch_ui_enabled(False)

        self.log_text.clear()
        self.add_log_message(
            f"Starting batch conversion of {len(self.batch_files)} file(s)...", "info"
        )

        self.batch_manager = BatchConversionManager()
        self.batch_manager.setup_batch(self.batch_files, self.output_dir)

        self.batch_manager.progress_updated.connect(self.on_batch_progress)
        self.batch_manager.file_completed.connect(self.on_batch_file_completed)
        self.batch_manager.batch_finished.connect(self.on_batch_finished)
        self.batch_manager.log_message.connect(self.add_log_message)

        self.batch_manager.start()

    def stop_batch_conversion(self):
        if self.batch_manager and self.batch_manager.is_running:
            reply = QMessageBox.question(
                self,
                "Stop Batch Conversion",
                "Are you sure you want to stop the batch conversion?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.batch_manager.stop()
                self.add_log_message("Stopping batch conversion...", "warning")

    def on_batch_progress(self, current: int, total: int, current_file: str):
        self.batch_progress_bar.setVisible(True)
        self.batch_progress_bar.setRange(0, total)
        self.batch_progress_bar.setValue(current)
        self.current_file_label.setVisible(True)
        self.current_file_label.setText(
            f"Processing: {current_file} ({current}/{total})"
        )
        self.status_label.setText(f"Batch progress: {current}/{total}")

    def on_batch_file_completed(self, file_path: str, success: bool, message: str):
        for i in range(self.file_list_widget.count()):
            item = self.file_list_widget.item(i)
            item_file_path, _, _ = item.data(Qt.ItemDataRole.UserRole)
            if item_file_path == file_path:
                if success:
                    item.setForeground(QColor(76, 175, 80))
                else:
                    item.setForeground(QColor(244, 67, 54))
                item.setToolTip(f"{item.toolTip()}\nStatus: {message}")
                break

    def on_batch_finished(self, success_count: int, fail_count: int):
        self.set_batch_ui_enabled(True)
        self.batch_progress_bar.setVisible(False)
        self.current_file_label.setVisible(False)

        if fail_count == 0:
            self.status_label.setText(
                f"Batch completed! {success_count} files converted successfully."
            )
            self.status_label.setStyleSheet("color: #4CAF50;")
            QMessageBox.information(
                self,
                "Batch Conversion Complete",
                f"Successfully converted: {success_count} file(s)\nFailed: {fail_count} file(s)\n\n"
                f"Check the log for details.",
            )
        else:
            self.status_label.setText(f"Batch completed with {fail_count} error(s).")
            self.status_label.setStyleSheet("color: #FFA500;")
            QMessageBox.warning(
                self,
                "Batch Conversion Completed with Errors",
                f"Successfully converted: {success_count} file(s)\nFailed: {fail_count} file(s)\n\n"
                f"Check the log for details.",
            )

        self.add_log_message(
            f"Batch conversion finished. Success: {success_count}, Failed: {fail_count}",
            "success" if fail_count == 0 else "warning",
        )

    def set_batch_ui_enabled(self, enabled: bool):
        self.add_files_btn.setEnabled(enabled)
        self.add_folder_btn.setEnabled(enabled)
        self.clear_files_btn.setEnabled(enabled)
        self.remove_selected_btn.setEnabled(enabled)
        self.select_output_dir_btn.setEnabled(enabled)
        self.batch_convert_btn.setEnabled(enabled)
        self.stop_batch_btn.setVisible(not enabled)

        self.select_xml_btn.setEnabled(enabled)
        self.select_json_btn.setEnabled(enabled)
        self.select_output_btn.setEnabled(enabled)
        self.convert_btn.setEnabled(enabled)

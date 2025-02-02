import os
import subprocess
import sys
from getpass import getpass

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QLabel, QHBoxLayout


class WireGuardUI(QWidget):
    def __init__(self):
        super().__init__()
        self.password = None
        self.initUI()

    def get_password(self):
        """Prompt the user for their sudo password."""
        if not self.password:
            self.password = getpass("Enter your sudo password: ")
        return self.password

    def initUI(self):
        self.setWindowTitle("WireGuard UI")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.config_label = QLabel("Select the configuration:")
        layout.addWidget(self.config_label)

        self.config_selector = QComboBox(self)
        configs = self.get_wg_configs()
        self.config_selector.addItems(configs)
        active_config = self.get_active_config()
        if active_config and active_config in configs:
            self.config_selector.setCurrentText(active_config)
        layout.addWidget(self.config_selector)

        self.status_text = QTextEdit(self)
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        self.__init_buttons(layout)

        self.setLayout(layout)
        self.get_status()

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#stop_button {
                background-color: #f44336;
            }
            QPushButton#stop_button:hover {
                background-color: #e53935;
            }
            QComboBox {
                padding: 5px;
                font-size: 14px;
            }
            QTextEdit {
                border: 1px solid #ccc;
                padding: 10px;
                font-size: 14px;
            }
        """)

    @staticmethod
    def get_active_config():
        """Return the active WireGuard configuration."""
        try:
            output = subprocess.check_output('wg show interfaces', shell=True, text=True).strip()
            if output:
                return output.split('\n')[0]
        except subprocess.CalledProcessError:
            return None

    def __init_buttons(self, layout):
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Connect", self)
        self.start_button.clicked.connect(self.start_wg)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Disconnect", self)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.stop_wg)
        button_layout.addWidget(self.stop_button)

        self.refresh_button = QPushButton("Refresh status", self)
        self.refresh_button.clicked.connect(self.get_status)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

    def get_wg_configs(self):
        """Return list of WireGuard configurations."""
        config_path = "/etc/wireguard"
        if not os.path.exists(config_path):
            return []
        return [f.replace(".conf", "") for f in os.listdir(config_path) if f.endswith(".conf")]

    def run_command(self, command):
        """Execute shell command with sudo."""
        self.log(f"Executing: {command}")
        try:
            output = subprocess.check_output(f'echo {self.get_password()} | sudo -S {command}', shell=True, text=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.output}\nError code: {e.returncode}"
        self.log(output)
        return output

    def get_status(self):
        """Get status of WireGuard."""
        selected_config = self.config_selector.currentText()
        status = self.run_command(f"wg show {selected_config}")
        self.status_text.setPlainText(status)

    def start_wg(self):
        """Start WireGuard."""
        selected_config = self.config_selector.currentText()
        self.run_command(f"wg-quick up {selected_config}")
        self.get_status()

    def stop_wg(self):
        """Stop WireGuard."""
        selected_config = self.config_selector.currentText()
        self.run_command(f"wg-quick down {selected_config}")
        self.get_status()

    def log(self, message):
        """Adds the log to the output field."""
        self.status_text.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WireGuardUI()
    window.show()
    sys.exit(app.exec())

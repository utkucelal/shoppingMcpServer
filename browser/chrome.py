import os
import platform
import shutil
import subprocess


class chromeInstance:



    remote_debugging_port = 9222
    user_data_dir_name = "ShoppinMcp"

    def __init__(self, remote_debugging_port=9222, user_data_dir_name="ShoppinMcp"):
        self.remote_debugging_port = remote_debugging_port
        self.user_data_dir_name = user_data_dir_name
        self.process = None

    def _chrome_path(self) -> str:
        system = platform.system()
        if system == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == "Windows":
            for candidate in (
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ):
                if os.path.exists(candidate):
                    return candidate
            return "chrome.exe"
        else:
            for candidate in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
                path = shutil.which(candidate)
                if path:
                    return path
            return "google-chrome"

    def _user_data_dir(self) -> str:
        return os.path.join(os.path.expanduser("~"), "Chromes", self.user_data_dir_name)

    def start_instance(self):
        if self.process is not None and self.process.poll() is None:
            return self.process

        args = [
            self._chrome_path(),
            f"--remote-debugging-port={self.remote_debugging_port}",
            f"--user-data-dir={self._user_data_dir()}",
        ]
        self.process = subprocess.Popen(args)
        return self.process

    def stop_instance(self):
        if self.process is None:
            return

        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        self.process = None

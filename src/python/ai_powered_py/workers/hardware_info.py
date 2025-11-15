import platform
import subprocess
import json
import workers.abstract

class Hardware(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions = ["getCPUInfo", "getRAMInfo", "getGPUInfo", "getStorageInfo"]
        self.behavior = "No args needed. Returns hardware information."
        self.result = {}

    def getPossibleActions(self) -> list[str]:
        return self.actions

    def describeBehavior(self) -> str:
        return self.behavior

    def executeAction(self) -> dict:
        self.result["getCPUInfo"] = self._getCPUInfo()
        self.result["getRAMInfo"] = self._getRAMInfo()
        self.result["getGPUInfo"] = self._getGPUInfo()
        self.result["getStorageInfo"] = self._getStorageInfo()
        return self.result

    def _getCPUInfo(self) -> dict:
        if platform.system() == "Linux":
            cmd="lscpu"
            return subprocess.getoutput(cmd).splitlines()[:16]
        else:
            return "Unsupported OS for CPU info."

    def _getRAMInfo(self) -> dict:
        if platform.system() == "Linux":
            cmd="free -h"
            return subprocess.getoutput(cmd).splitlines()
        else:
            return "Unsupported OS for RAM info."

    def _getGPUInfo(self) -> str:
        if platform.system() == "Linux":
            cmd="lspci | grep -i vga"
            return subprocess.getoutput(cmd)
        else:
            return "Unsupported OS for GPU info."

    def _getStorageInfo(self) -> str:
        if platform.system() == "Linux":
            cmd="df -h"
            return subprocess.getoutput(cmd).splitlines()
        else:
            return "Unsupported OS for storage info."

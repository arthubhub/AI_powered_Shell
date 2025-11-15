import platform
import subprocess
import json
import workers.abstract

class SystemInfo(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions = ["getOSInfo", "getKernelVersion", "getSystemArchitecture", "getEnvironmentVariables"]
        self.behavior = "Returns system information.\
            argument format : no arguments"
        self.result = {}

    def getPossibleActions(self) -> list[str]:
        return self.actions

    def describeBehavior(self) -> str:
        return self.behavior

    def executeAction(self, **kwargs) -> dict:
        self.result["getOSInfo"] = self._getOSInfo()
        self.result["getKernelVersion"] = self._getKernelVersion()
        self.result["getSystemArchitecture"] = self._getSystemArchitecture()
        self.result["getEnvironmentVariables"] = self._getEnvironmentVariables()
        return self.result

    def _getOSInfo(self) -> dict:
        sys_info = {}
        sys_info["system"] = platform.system()
        sys_info["release"] = platform.release()
        sys_info["version"] = platform.version()
        return sys_info

    def _getKernelVersion(self) -> str:
        if platform.system() == "Linux":
            return subprocess.getoutput("uname -r")
        else:
            return "Unsupported OS for kernel version."

    def _getSystemArchitecture(self) -> str:
        return platform.machine()

    def _getEnvironmentVariables(self) -> dict:
        result_dict = [ line.split("=",1) for line in subprocess.getoutput("env").splitlines()]
        return dict(result_dict)
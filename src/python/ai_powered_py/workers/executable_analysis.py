import subprocess
import json
import os
import shlex
import workers.abstract

class ExecutableAnalysis(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions = [
            "getFileType",
            "getArchitecture",
            "getDependencies",
            "getStrings",
            "getSymbols",
            "getSections",
            "getDisassembly"
        ]
        self.behavior = (
            "Give a list of executable files in the format: [\"file1\", \"dir/file2\", ...]. "
            "Returns static analysis information about the executables."
        )
        self.result = {}

    def getPossibleActions(self) -> list[str]:
        return self.actions

    def describeBehavior(self) -> str:
        return self.behavior

    def executeAction(self, file_list: list[str]) -> dict:
        for file_path in file_list:
            if not os.path.exists(file_path):
                self.result[file_path] = {"error": f"File not found: {file_path}"}
                continue
            self.result[file_path] = {}
            self.result[file_path]["getFileType"] = self._getFileType(file_path)
            self.result[file_path]["getArchitecture"] = self._getArchitecture(file_path)
            self.result[file_path]["getDependencies"] = self._getDependencies(file_path)
            self.result[file_path]["getStrings"] = self._getStrings(file_path)
            self.result[file_path]["getSymbols"] = self._getSymbols(file_path)
            self.result[file_path]["getSections"] = self._getSections(file_path)
            self.result[file_path]["getDisassembly"] = self._getDisassembly(file_path)
        return self.result

    def _getFileType(self, file_path: str) -> str:
        cmd = f"file {shlex.quote(file_path)}"
        return subprocess.getoutput(cmd)

    def _getArchitecture(self, file_path: str) -> str:
        cmd = f"file {shlex.quote(file_path)}"
        output = subprocess.getoutput(cmd)
        if "ELF" in output:
            return output.split(",")[1].strip() # -> x86/x86_64/etc
        else:
            return "Unknown architecture"

    def _getDependencies(self, file_path: str) -> list:
        if "ELF" in subprocess.getoutput(f"file {shlex.quote(file_path)}"):
            cmd = f"ldd {shlex.quote(file_path)}"
            return subprocess.getoutput(cmd).splitlines()
        else:
            return ["Unsupported file type for dependency analysis"]

    def _getStrings(self, file_path: str) -> list:
        cmd = f"strings {shlex.quote(file_path)}"
        return subprocess.getoutput(cmd).splitlines()[:20]

    def _getSymbols(self, file_path: str) -> list:
        if "ELF" in subprocess.getoutput(f"file {shlex.quote(file_path)}"):
            cmd = f"nm {shlex.quote(file_path)}"
            return subprocess.getoutput(cmd).splitlines()[:20]
        else:
            return ["Unsupported file type for symbol analysis"]

    def _getSections(self, file_path: str) -> list:
        if "ELF" in subprocess.getoutput(f"file {shlex.quote(file_path)}"):
            cmd = f"readelf -S {shlex.quote(file_path)}"
            return subprocess.getoutput(cmd).splitlines()[:20]
        else:
            return ["Unsupported file type for section analysis"]

    def _getDisassembly(self, file_path: str) -> list:
        if "ELF" in subprocess.getoutput(f"file {shlex.quote(file_path)}"):
            cmd = f"objdump -d {shlex.quote(file_path)}"
            return subprocess.getoutput(cmd).splitlines()[:20]
        else:
            return ["Unsupported file type for disassembly"]
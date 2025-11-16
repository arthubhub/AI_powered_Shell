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
            "Give a list of executable files and it will returns static analysis information about the executables. Please give the fullpath.\
                argument format : worker_name=\"file1\", \"dir/file2\", ..."
        )
        self.result = {}

    def getPossibleActions(self) -> list[str]:
        return self.actions

    def describeBehavior(self) -> str:
        return self.behavior

    def executeAction(self, file_list: list[str]) -> dict:
        for file_path in file_list:
            cleaned_filename = file_path.strip('"\'')


            if not os.path.exists(cleaned_filename):
                self.result[cleaned_filename] = {"error": f"File not found: {cleaned_filename}"}
                continue
            if not os.path.isfile(cleaned_filename):
                self.result[cleaned_filename] = {"error": f"Not a file: {cleaned_filename}"}
            self.result[cleaned_filename] = {}
            self.result[cleaned_filename]["getFileType"] = self._getFileType(cleaned_filename)
            self.result[cleaned_filename]["getArchitecture"] = self._getArchitecture(cleaned_filename)
            self.result[cleaned_filename]["getDependencies"] = self._getDependencies(cleaned_filename)
            self.result[cleaned_filename]["getStrings"] = self._getStrings(cleaned_filename)
            self.result[cleaned_filename]["getSymbols"] = self._getSymbols(cleaned_filename)
            self.result[cleaned_filename]["getSections"] = self._getSections(cleaned_filename)
            self.result[cleaned_filename]["getDisassembly"] = self._getDisassembly(file_path)
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
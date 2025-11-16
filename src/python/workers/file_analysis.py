import workers.abstract
import magic # magic bytes
import subprocess
import shlex
import os

class FileAnalysis(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions=["getFileType", "getLineWordsCount", "getFilePermissions", "getFileStrings"]
        self.behavior="When calling this worker, give a list of files and it will return information about given files.\
            argument format : worker_name=\"file1\", \"dir/file2\", ..."
        self.result={}
    def getPossibleActions(self) -> list[str]:
        """Return a list of actions this worker performs."""
        return self.actions

    def describeBehavior(self) -> str:
        """Return a description of how to call worker."""
        return self.behavior

    def executeAction(self, file_list: list[str]) -> any:
        """Execute the actions."""
        for file in file_list:
            if '"' in file:
                cleaned_filename=file.split('"')[1] # if file is : '"/home/file" # to check if the file exists', it will be handled (thanks dumb ai)
            elif "'" in file:
                cleaned_filename=file.split('"')[1]
            else :
                cleaned_filename = file


            if not os.path.exists(cleaned_filename):
                self.result[cleaned_filename] = {"error": f"File not found: {cleaned_filename} in {os.getcwd()}"}
                continue
            if not os.path.isfile(cleaned_filename):
                self.result[cleaned_filename] = {"error": f"Not a file: {cleaned_filename}"}
                continue
            self.result[cleaned_filename] = {}
            self.result[cleaned_filename]["Type"] = self._getFileType(cleaned_filename)
            self.result[cleaned_filename]["LineWordsCount"] = self._getLineWordsCount(cleaned_filename)
            self.result[cleaned_filename]["FilePermissions"] = self._getFilePermissions(cleaned_filename)
            self.result[cleaned_filename]["Strings"] = self._getFileStrings(cleaned_filename)

        
        return self.result


    def _getFileType(self, file: str) -> str:        
        return magic.from_file(file)
    def _getLineWordsCount(self, file: str) -> str:
        cmd = f"wc {shlex.quote(file)}"
        return subprocess.getoutput(cmd)
    def _getFilePermissions(self, file: str) -> str:
        cmd = f"ls -l {shlex.quote(file)}"
        return subprocess.getoutput(cmd)
    def _getFileStrings(self, file: str) -> list[str]:
        cmd = f"strings {shlex.quote(file)}"
        return subprocess.getoutput(cmd).splitlines()[:10]

    



    
        
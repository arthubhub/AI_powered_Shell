import workers.abstract
import magic # magic bytes
import subprocess
import shlex



class FileAnalysis(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions=["getFileType", "getLineWordsCount", "getFilePermissions", "getFileStrings"]
        self.behavior="When calling this worker, give a list of files in the following format : [\"file1\", \"dir1/file2\", ... ]\n It will return information about given files."
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
            self.result[file]={}
            self.result[file]["Type"]=self._getFileType(file)
            self.result[file]["LineWordsCount"]=self._getLineWordsCount(file)
            self.result[file]["FilePermissions"]=self._getFilePermissions(file)
            self.result[file]["Strings"]=self._getFileStrings(file)
        
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

    



    
        
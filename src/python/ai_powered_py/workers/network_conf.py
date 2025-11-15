import workers.abstract
import subprocess
import ifcfg
import json

class NetworkConf(workers.abstract.AbstractWorker):
    def __init__(self):
        self.actions=["getInterfaces", "getRoute", "traceRoute", "pingInternet"]
        self.behavior="Returns information about network status.\
            argument format : no arguments"
        self.result={}
    def getPossibleActions(self) -> list[str]:
        """Return a list of actions this worker performs."""
        return self.actions

    def describeBehavior(self) -> str:
        """Return a description of how to call worker."""
        return self.behavior

    def executeAction(self, list=[]) -> any:
        """Execute the actions."""
        self.result["getInterfaces"]=self._getInterfaces()
        self.result["getRoute"]=self._getRoute()
        self.result["traceRoute"]=self._traceRoute()
        self.result["pingInternet"]=self._pingInternet()
        return self.result
    
    def _getInterfaces(self) -> dict[dict]:
        interfaces_dict={}
        for interface in ifcfg.interfaces().values():
            interfaces_dict[interface['device']]={}
            interfaces_dict[interface['device']]["ipv4"]=interface['inet4']
            interfaces_dict[interface['device']]["netmasks"]=interface['netmasks']
        return interfaces_dict
    def _getRoute(self) -> list:
        cmd=" ".join(['ip','route','show'])
        return subprocess.getoutput(cmd).splitlines()
    def _traceRoute(self) -> list:
        static_ip="8.8.8.8"
        cmd=" ".join(['traceroute', static_ip]) 
        return subprocess.getoutput(cmd).splitlines()
    
    def __runPingWithTimeout(self,host):
        try:
            result = subprocess.run(
                ["ping", "-c", "1", host],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return f"Ping to {host} timed out after 1 second(s)."
        except Exception as e:
            return f"Error pinging {host}: {e}"
    def _pingInternet(self):

        ping_results={}
        hosts=["yahoo.com", "8.8.8.8"]
        for host in hosts:
            ping_results["host"]=self.__runPingWithTimeout(host).splitlines()
        return ping_results



    


    



import importlib
import pkgutil
from workers.abstract import AbstractWorker
import json
class AI_POWER:
    def __init__(self):
        self.workers = {}

    def loadWorkers(self):
        excludelist=["abstract"]
        for _, name, _ in pkgutil.iter_modules(['workers']):
            if name not in excludelist:
                module = importlib.import_module(f"workers.{name}")
                for attribute in dir(module):
                    attr = getattr(module, attribute)
                    if isinstance(attr, type) and issubclass(attr, AbstractWorker) and attr != AbstractWorker :
                        self.workers[name]=attr()
    
    def describeWorkers(self):
        print("Loading modules ...")
        for key,attr in self.workers.items():
            print(f"> MODULE : {key}")
            print(attr.describeBehavior())

    def getWorkersPossibleActions(self):
        for key,attr in self.workers.items():
            print(key, " -> ", attr.getPossibleActions())
    def runWorkers(self):
        name="file_analysis"
        file_list=["../../../install.sh","/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall/ch64"]
        print("-"*20,name,"-"*20)
        json_string=json.dumps(self.workers[name].executeAction(file_list), indent=4)
        print(json_string)

        name="executable_analysis"
        file_list=["/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall/ch64"]
        print("-"*20,name,"-"*20)
        json_string=json.dumps(self.workers[name].executeAction(file_list), indent=4)
        print(json_string)

        name="network_conf"
        print("-"*20,name,"-"*20)
        json_string = json.dumps(self.workers[name].executeAction(), indent=4)
        print(json_string)

        name="hardware_info"
        print("-"*20,name,"-"*20)
        json_string = json.dumps(self.workers[name].executeAction(), indent=4)
        print(json_string)

        name="system_info"
        print("-"*20,name,"-"*20)
        json_string = json.dumps(self.workers[name].executeAction(), indent=4)
        print(json_string)
        





if __name__=="__main__":
    print("Debugging")
    my_ai=AI_POWER()
    my_ai.loadWorkers()
    my_ai.describeWorkers()
    my_ai.getWorkersPossibleActions()
    my_ai.runWorkers()
        
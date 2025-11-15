import importlib
import pkgutil
from workers.abstract import AbstractWorker
import json
class AI_POWER:
    def __init__(self):
        self.workers = {}
    
    def to_markdown(self, module, data: dict) -> str:

        markdown = f"## {module}\n"
        for key, elem in data.items():
            markdown += f"- **{key}:**\n"
            if isinstance(elem, str):
                markdown += f"  `{elem}`\n"
            elif isinstance(elem, list):
                markdown += "  ```\n"
                for val in elem:
                    markdown += f"  {val}\n"
                markdown += "  ```\n"
            elif isinstance(elem, dict):
                markdown += "  ```\n"
                for dict_key, dict_val in elem.items():
                    if isinstance(dict_val, dict):
                        markdown += f"  {dict_key}:\n"
                        for sub_key, sub_val in dict_val.items():
                            markdown += f"    - {sub_key}: `{sub_val}`\n"
                    else:
                        markdown += f"  {dict_key}: `{dict_val}`\n"
                markdown += "  ```\n"
        return markdown

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
        markdown=self.to_markdown(name,self.workers[name].executeAction(file_list))
        print(markdown)

        name="executable_analysis"
        file_list=["/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall/ch64"]
        markdown=self.to_markdown(name,self.workers[name].executeAction(file_list))
        print(markdown)


        name="network_conf"
        markdown=self.to_markdown(name,self.workers[name].executeAction())
        print(markdown)


        name="hardware_info"
        markdown=self.to_markdown(name,self.workers[name].executeAction())
        print(markdown)


        name="system_info"
        markdown=self.to_markdown(name,self.workers[name].executeAction())
        print(markdown)

        





if __name__=="__main__":
    print("Debugging")
    my_ai=AI_POWER()
    my_ai.loadWorkers()
    my_ai.describeWorkers()
    my_ai.getWorkersPossibleActions()
    my_ai.runWorkers()
        
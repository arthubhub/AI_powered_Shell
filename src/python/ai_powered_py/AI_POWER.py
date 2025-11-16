import importlib
import pkgutil
from workers.abstract import AbstractWorker
import json
import re
import sys
import subprocess
import platform
import os
from datetime import datetime

class Colors:
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'


class AI_POWER:
    def __init__(self, logs_file, mode="Q", last_command="", model="mistral", debug=0):
        self.DEBUG=debug
        self.workers = {}
        self.logs_file=logs_file
        self.mode=mode
        self.last_command=last_command
        self.ollama_model=model
        self.logs={}
        self.context_info={}
        self.env_info={}
        self.current_dir_content={}
        self.current_system_prompt=""
        self.current_user_prompt=""
        self.required_workers={}
        self.workers_output_md=""
        
    
    def formatText(self, text):
        text = re.sub(r'\$\{CYAN\}', Colors.CYAN, text)
        text = re.sub(r'\$\{NC\}', Colors.NC, text)
        text = re.sub(r'\$\{BOLD\}', Colors.BOLD, text)
        text = re.sub(r'\$\{GREEN\}', Colors.GREEN, text)
        text = re.sub(r'\$\{YELLOW\}', Colors.YELLOW, text)
        text = re.sub(r'\$\{RED\}', Colors.RED, text)
        text = re.sub(r'\$\{BLUE\}', Colors.BLUE, text)
        
        text = re.sub(r'\{CYAN\}', Colors.CYAN, text)
        text = re.sub(r'\{NC\}', Colors.NC, text)
        text = re.sub(r'\{BOLD\}', Colors.BOLD, text)
        text = re.sub(r'\{GREEN\}', Colors.GREEN, text)
        text = re.sub(r'\{YELLOW\}', Colors.YELLOW, text)
        text = re.sub(r'\{RED\}', Colors.RED, text)
        text = re.sub(r'\{BLUE\}', Colors.BLUE, text)
        
        return text
    
    def formatMdToShell(self, text):
        newstring = re.sub(r'```[^\n]*\n([^```]*)```', r'{BLUE}\1{NC}', text)
        newstring = re.sub(r'`([^`]*)`', r'{CYAN}\1{NC}', newstring)

        newstring = re.sub(r'\*\*(.*?)\*\*', r'{BOLD}\1{NC}', newstring)
        newstring = re.sub(r'\*(.*?)\*', r'{RED}\1{NC}', newstring)

        return newstring

    def toMarkdown(self, module, data: dict) -> str:

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


    def printHeader(self,text):
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80
        print(f"\n{Colors.CYAN}{'=' * width}{Colors.NC}")
        print(f"{Colors.BOLD}{text.center(width)}{Colors.NC}")
        print(f"{Colors.CYAN}{'=' * width}{Colors.NC}\n")
    def printSeparator(self):
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80
        print(f"{Colors.CYAN}{'=' * width}{Colors.NC}\n")
        

    ###################################
    # The following methods are used to 
    # build the prompts.
    ###################################

    def buildQuickModePromptUser(self):
        self.current_user_prompt=""
        user_prompt=["[BEGIN USER PROMPT]"]
        user_prompt.append("""# Important
Using the "SYSTEM INDICATIONS", you will analyse the context in the following sections, and find the problem stated by the user.
You will see the following sections:
1. User machine context.
2. Previous commands and results.
3. Environment information.
4. Current directory content
5. Problem faced by the user.""")
        user_prompt.append("""# Host information""")
        user_prompt.append(self.toMarkdown("User machine context",self.context_info))
        user_prompt.append("## Previous commands and results")
        user_prompt.append(self.getCommandHistory())
        user_prompt.append(self.toMarkdown("Environment information",self.env_info))
        user_prompt.append(self.toMarkdown("Current directory content",self.current_dir_content))
        user_prompt.append("# User Prompt <- that is where you find your mission")
        user_prompt.append(f"IMPORTANT : Here is the last command of the user, it is your mission. Consider it as a failed command, or as its question : **`{self.last_command}`**")
        user_prompt.append("[END USER PROMPT]")

        self.current_user_prompt="\n".join(user_prompt)
        



    def buildQuickModePromptSystem(self):
        self.current_system_prompt=""
        self.current_system_prompt="""[BEGIN SYSTEM INDICATIONS]
# Context
- You are a command-line assistant;
- You are called by the user in its shell;
- You have to use context about user env to solve its problem.

# Rules
1. **Only use the provided context and command.** Never invent, assume, or reference files/commands not mentioned in the context.
2. **Be concise:** One-line summary, followed by a short list of actionable solutions.
3. **If the context is unclear or missing, ask for clarification. Do NOT guess.**
4. **Focus on the logic** Use context and find real logical problems.

# Answer structure
1. Begin by resuming the context.
2. State the problem of the situation, show what part is wrong.
3. Give short advices, and command to run.
4. Give advice to better understand the situation.

# Answer format
1. Put small commands between `command`
2. Put command blocs between ```bloc```
3. Make important words strong with **bold**
4. If the user make a typo mistake, put the sample in italic, between single stars, and not backsticks.
[END SYSTEM INDICATIONS]"""



    def buildQuickModePrompt(self):
        self.buildQuickModePromptSystem()
        self.buildQuickModePromptUser()


    def buildDeepModePromptSystemFinalStep(self):
        self.current_system_prompt=""
        self.current_system_prompt="""[BEGIN SYSTEM INDICATIONS]
# Context
- You are a command-line assistant;
- You are called by the user in its shell;
- You have to use context about user env to solve its problem.

# Rules
1. **Only use the provided context and command.** Never invent, assume, or reference files/commands not mentioned in the context.
2. **Be concise:** One-line summary, followed by a short list of actionable solutions.
3. **If the context is unclear or missing, ask for clarification. Do NOT guess.**
4. **Focus on the logic** Use context and find real logical problems.

# Answer structure
1. Begin by resuming the context.
2. State the problem of the situation, from the "User Prompt" section.
3. Explain what you can see from "Workers Results" section.
3. Give short advices, and command to run.
4. Give advice to better understand the situation.

# Answer format
1. Put small commands between `command`
2. Put command blocs between ```bloc```
3. Make important words strong with **bold**
[END SYSTEM INDICATIONS]"""
    def buildDeepModePromptUserFinalStep(self):
        self.current_user_prompt=""
        user_prompt=["[BEGIN USER PROMPT]"]
        user_prompt.append("""# Important
Using the "SYSTEM INDICATIONS", you will analyse the context in the following sections, and find the problem stated by the user.
You will see the following sections:
1. User machine context.
2. Previous commands and results.
3. Environment information.
4. Current directory content
5. Workers Results
6. Problem faced by the user.""")
        user_prompt.append("""# Host information""")
        user_prompt.append(self.toMarkdown("User machine context",self.context_info))
        user_prompt.append("## Previous commands and results")
        user_prompt.append(self.getCommandHistory())
        user_prompt.append(self.toMarkdown("Environment information",self.env_info))
        user_prompt.append(self.toMarkdown("Current directory content",self.current_dir_content))
        user_prompt.append("# Workers Results")
        user_prompt.append(self.workers_output_md)
        user_prompt.append("# User Prompt <- that is where you find your mission")
        user_prompt.append(f"IMPORTANT : Here is the last command of the user, it is your mission. Consider it as a failed command, or as its question : **`{self.last_command}`**")
        user_prompt.append("[END USER PROMPT]")

        self.current_user_prompt="\n".join(user_prompt)

    def buildDeepModePromptSystemInitStep(self):
        self.current_system_prompt=""
        system_prompt=["[BEGIN SYSTEM INDICATIONS]"]
        system_prompt.append("""# Context
- You are a command-line assistant;
- You are called by the user in its shell;
- You have to use context about user env to solve its problem;
- you are currently in the `Initial prompt` step.

# Process
The process is divided into three steps:
1. Initial prompt
2. Workers actions
3. Final prompt

## Initial prompt
- During this step, the user context will be provided. 
- Then you will receive a list of possible actions.
- You will decide which actions to perform.
- You will follow the syntax indications for the answer.

## Workers actions
- The workers will be called according to your requirements.
- They will get additional context for you.
- Worker actions just give you information about what the worker does.

## Final prompt
- During this step, you will analyse the context provided by the worker.
- You will follow the instructions.
- You will bring your help to solve the problem.

# Workers list""")
        for key,attr in self.workers.items():
            system_prompt.append(f"## '{key}'")
            system_prompt.append(f"- Behavior: {attr.describeBehavior()}")
            system_prompt.append(f"- Worker actions: {attr.getPossibleActions()}")

        system_prompt.append("""# Calling convetions 
- Print the name of the worker to call
- Put the arguments in an comma separated list
## Good Format (just example with fictive workers, apply it with actual ones)
- You need info about the network ? just run something like that
```
It seems that ...
[WORKERS]
network_conf
```
- You are not sure the file allow this behavior ? just run something like that
```
[WORKERS]
file_analysis=./test/myfile
```                      
- Other valid example :
```
To help the user ...

To find the type ... here is what we can perform:
[WORKERS]
executable_analysis=file.exe,run.bin
```
## Very Wrong Format                        
- Never use non existing workers :
```
[WORKERS]
fictive_worker_analyse_file=file
```
- Never put worker capabilities as argument :
```
[WORKERS]
fictive_worker_check_internet=getRoute
```
- Never put other things than given workers :
```
[WORKERS]
file_analysis=main.py
hardware_info 
cwd, pwd <- VERY VERY BAD
system_info
```                         
- Never put comments :
```
[WORKERS]
file_analysis="/etc/test" # To check if the file exists <- WRONG
```                              
""")
        system_prompt.append("""# Output format (IMPORTANT)
- You are now in the initial step;
- You will perform an analysis of the user request;
- You will try to find logical problems;
- You will print the list of workers to be called with their arguments;
- Firstly, state what is happening
- Then put the commands under the "[WORKERS]" bloc
- You will use the format given in the previous section (Workers list);
- Your answer will be parsed in python , respect the required format.""")


        system_prompt.append("[END SYSTEM INDICATIONS]")
        self.current_system_prompt="\n".join(system_prompt)



    def buildDeepModeInitialPrompt(self):
        self.buildDeepModePromptSystemInitStep()
        self.buildQuickModePromptUser()
    def buildDeepModeFinalPrompt(self):
        self.buildDeepModePromptSystemFinalStep()
        self.buildDeepModePromptUserFinalStep()
    



    ########################################
    # The following methods are used to give 
    # a quick overview of context to the AI.
    ########################################

    def getCommandHistory(self):
        history_items = list(self.logs.get('command_history', {}).items())
        # Skip first command (usually the cat of json file itself) and get last 10
        recent_commands = history_items[-11:-1] if len(history_items) > 11 else history_items[:-1] if len(history_items) > 1 else []
        command_history_md=""
        if not recent_commands:
            command_history_md += "*No command history available*\n"
        else:
            for idx, (timestamp, data) in enumerate(recent_commands, 1):
                command_content = data.get('command', {}).get('content', 'N/A')
                result_content = data.get('result', {}).get('content', '')
                
                command_history_md += f"### {idx}. [{timestamp}]\n"
                command_history_md += f"**Command:** `{command_content}`\n"
                
                if result_content:
                    truncated_result = result_content[:500] + "..." if len(result_content) > 500 else result_content
                    command_history_md += f"**Output:**\n```\n{truncated_result}\n```\n"
                else:
                    command_history_md += "**Output:** *(no output captured yet)*\n"
        return command_history_md



    def loadJsonLogs(self):
        try:
            with open(self.logs_file, 'r') as f:
                self.logs = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: File '{self.logs_file}' not found.{Colors.NC}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}Error: Invalid JSON in '{self.logs_file}': {e}{Colors.NC}", file=sys.stderr)
            sys.exit(1)

    def getEnvInfo(self):
        for key in ['PATH', 'HOME', 'SHELL', 'LANG', 'TERM']:
            value = os.environ.get(key, 'N/A')
            if key == 'PATH' and len(value) > 200:
                value = value[:200] + "..."
            self.env_info[key]=value

    def getOSAndPackageManager(self):
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = f.read().splitlines()[0] # -> NAME="Arch Linux"
                self.context_info['distro']=os_release
                
        except FileNotFoundError:
            pass
        
        for packagemanager in ['pacman', 'apt', 'apt-get', 'dnf', 'yum', 'zypper']:
            if subprocess.run(['which', packagemanager], capture_output=True).returncode == 0:
                self.context_info['package_manager'] = packagemanager
                if packagemanager == 'pacman':
                    self.context_info['package_install_command'] = f'sudo {packagemanager} -S'
                elif packagemanager in ['apt', 'apt-get']:
                    self.context_info['package_install_command'] = f'sudo {packagemanager} install'
                elif packagemanager in ['dnf', 'yum']:
                    self.context_info['package_install_command'] = f'sudo {packagemanager} install'
                elif packagemanager == 'zypper':
                    self.context_info['package_install_command'] = f'sudo {packagemanager} install'
                break
    def getSystemInfo(self):
        self.context_info['cwd']=os.getcwd()
        self.context_info['shell']=os.environ.get('SHELL', 'unknown')
        self.context_info['user']=os.environ.get('USER', 'unknown')
        self.context_info['os']=f"{platform.system()} {platform.release()}"
        self.context_info['machine']=platform.machine()
        self.context_info['python_version']=platform.python_version()
        self.context_info['date']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def getDirectoryContent(self,path='.'):
        try:
            self.current_dir_content[os.path.abspath(path)]=subprocess.run(
                ['ls', '-la', path],
                capture_output=True,
                text=True,
                timeout=2
            ).stdout.splitlines()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Listing failed"

    def loadContext(self):
        self.getOSAndPackageManager()
        self.getSystemInfo()
        self.getDirectoryContent()
        self.getEnvInfo()


    ############################################
    # Functions to be called by the main program
    ############################################

    def buildObject(self): # <- called by the main program
        self.loadWorkers()
        self.loadJsonLogs()
        self.loadContext()
    
    def runModel(self): # <- called by the main program
        if self.mode=="D":
            self.deepModel()
        else:
            self.quickModel()

            


    ###############################################
    # The following methods handles ai interactions
    ###############################################


    def quickModel(self):
        self.buildQuickModePrompt()
        print(f"\n{Colors.YELLOW}...{Colors.NC} Calling Ollama API (model: {Colors.BOLD}mistral{Colors.NC})...\n")
        ollama_answer=self.callOllama()
        formatted_to_shell_response = self.formatMdToShell(ollama_answer)
        formatted_response = self.formatText(formatted_to_shell_response)

        self.printHeader("OLLAMA RESPONSE")
        print(formatted_response)
        self.printSeparator()

    def deepModel(self):
        def update_status(message):
            print(f"\r\033[K{Colors.BOLD}Status:{Colors.NC} {message}", end='', flush=True)
        
        print("Deep Model")
        
        # Step 1: Initial prompt
        self.buildDeepModeInitialPrompt()
        output_str = f"{Colors.YELLOW}...{Colors.NC} {Colors.BOLD}Step 1{Colors.NC}: Requesting for the workers using Ollama API (model: {Colors.BOLD}mistral{Colors.NC})..."
        update_status(output_str)
        ollama_answer = self.callOllama()
        if self.DEBUG:
            print()  # New line before debug output
            formatted_to_shell_response = self.formatMdToShell(ollama_answer)
            formatted_response = self.formatText(formatted_to_shell_response)
            self.printHeader("OLLAMA RESPONSE")
            print(formatted_response)
            self.printSeparator()
        
        # Step 2: Workers
        self.getRequiredWorkers(ollama_answer)
        output_str = f"{Colors.YELLOW}...{Colors.NC} {Colors.BOLD}Step 2{Colors.NC}: Running following workers: {list(self.required_workers.keys())}..."
        update_status(output_str)        
        self.runWorkers()
        
        # Step 3: Final prompt with workers results
        self.buildDeepModeFinalPrompt()
        if self.DEBUG:
            print()
            print("-" * 20 + "FINAL REQUEST" + "-" * 20)
            print(self.current_user_prompt)
            print("-" * 50)
        output_str = f"{Colors.YELLOW}...{Colors.NC} {Colors.BOLD}Step 3{Colors.NC}: Final AI request using Ollama API (model: {Colors.BOLD}mistral{Colors.NC})..."
        update_status(output_str)
        ollama_answer = self.callOllama()
        print()
        formatted_to_shell_response = self.formatMdToShell(ollama_answer)
        formatted_response = self.formatText(formatted_to_shell_response)
        self.printHeader("OLLAMA RESPONSE")
        print(formatted_response)
        self.printSeparator()







    #####################################################
    # The following methods handle connection with ollama
    #####################################################
    def callOllama(self):
        try:
            import ollama
        except ImportError:
            print(f"{Colors.RED}Error: 'ollama' Python package is not installed.{Colors.NC}", file=sys.stderr)
            print(f"{Colors.YELLOW}Install it with: pip install ollama{Colors.NC}", file=sys.stderr)
            sys.exit(1)

        
        try:
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'system',
                        'content': self.current_system_prompt
                    },
                    {
                        'role': 'user',
                        'content': self.current_user_prompt
                    }
                ]
            )
            return response['message']['content']
        
        except Exception as e:
            print(f"{Colors.RED}Error calling Ollama: {e}{Colors.NC}", file=sys.stderr)
            print(f"{Colors.YELLOW}Make sure Ollama is running with: ollama serve{Colors.NC}", file=sys.stderr)
            sys.exit(1)





    ####################################################
    # The following methods perform actions with workers
    ####################################################
    def getRequiredWorkers(self,ollama_answer):
        if "[WORKERS]" not in ollama_answer:
            print(f"{Colors.RED}Error: 'ollama' didn't give any worker.{Colors.NC}", file=sys.stderr)
            sys.exit(1)
        worker_list={}

        worker_blocs=ollama_answer.split("[WORKERS]\n")[1:] # <- we get all blocs beginning with [WORKERS]\n 
        for worker_bloc in worker_blocs:

            worker_bloc_lines=worker_bloc.splitlines()
            if len(worker_bloc_lines)>0:
                for i in range(len(worker_bloc_lines)):
                    curr_worker=worker_bloc_lines[i].split("=")
                    curr_worker_name=curr_worker[0].strip()
                    #print("curr worker name : ",curr_worker_name)
                    if curr_worker_name in self.workers.keys():
                        if self.DEBUG:
                            print(f"{Colors.GREEN}[+]{Colors.NC} Valid worker : {curr_worker}")
                        worker_list[curr_worker_name]=[]
                        if len(curr_worker)>1:
                            worker_list[curr_worker_name]=curr_worker[1].split(",")
                        i+=1
                        if i<len(worker_bloc_lines):
                            curr_worker=worker_bloc_lines[i].split("=")
                            curr_worker_name=curr_worker[0].strip()
        
        self.required_workers=worker_list


    def loadWorkers(self):
        if self.workers == {}:
            excludelist = ["abstract"]
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            workers_path = os.path.join(parent_dir, 'workers')
            
            #print(f"Looking for workers in: {workers_path}")
            for _, name, _ in pkgutil.iter_modules([workers_path]):
                #print(f"Found worker module: {name}")
                if name not in excludelist:
                    module = importlib.import_module(f"workers.{name}")
                    for attribute in dir(module):
                        attr = getattr(module, attribute)
                        if isinstance(attr, type) and issubclass(attr, AbstractWorker) and attr != AbstractWorker:
                            self.workers[name] = attr()
            #print(f"Loaded workers: {self.workers}")
            
            
                

    
    def describeWorkers(self):
        print("Loading modules ...")
        for key,attr in self.workers.items():
            print(f"> MODULE : {key}")
            print(attr.describeBehavior())

    def getWorkersPossibleActions(self):
        for key,attr in self.workers.items():
            print(key, " -> ", attr.getPossibleActions())

    def runWorkers(self):
        markdown=[]
        for name, args in self.required_workers.items():
            markdown.append(self.toMarkdown(name,self.workers[name].executeAction(args)))
        self.workers_output_md="\n".join(markdown)
        #print(self.workers_output_md)

    
    def runWorkersExample(self):
        name="file_analysis"
        file_list=["../../../install.sh","/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall/ch64"]
        markdown=self.toMarkdown(name,self.workers[name].executeAction(file_list))
        print(markdown)

        name="executable_analysis"
        file_list=["/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall/ch64"]
        markdown=self.toMarkdown(name,self.workers[name].executeAction(file_list))
        print(markdown)


        name="network_conf"
        markdown=self.toMarkdown(name,self.workers[name].executeAction())
        print(markdown)


        name="hardware_info"
        markdown=self.toMarkdown(name,self.workers[name].executeAction())
        print(markdown)


        name="system_info"
        markdown=self.toMarkdown(name,self.workers[name].executeAction())
        print(markdown)

        





if __name__=="__main__":
    print("Debugging")
    logs_file="/tmp/ai_powered_shell_arthub.json"
    test_prompts=["why cant i run the program /home/arthub/Downloads/ch64",
                  "why cant i run main.py",
                  "what is the biggest file of my current directory",
                  "why cant i reach my friend on 192.168.1.2"]

    for prompt in test_prompts:
        my_ai=AI_POWER(logs_file,"D",prompt,debug=1)
        my_ai.buildObject()
        my_ai.runModel()
        
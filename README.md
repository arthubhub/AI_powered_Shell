# AI_powered_Shell
This project implements a shell add-on to improve productivity with local LLM usage.

## Global workflow

![KSS-design](https://github.com/user-attachments/assets/945b1804-9b95-4e02-9a9c-52ded016e45a)


## Internal process

![workflow](https://github.com/user-attachments/assets/b15241bd-2c71-4e69-8727-63403d187bcb)


## Commands logging

In order to give context about previous commands and results, the add-on should log them to a file (one per session). This file will be created when initiating the shell session ( when calling `source add-on.sh` ).
The data will have to be sent to python3 script in JSON format. To do so we can either format the data asthey arrive to the file, or parse them before giving them to the python scrpit.

## LLM interactions

### **Behavior** : 
We first want to make clear how the LLM should process requests. This part must be persistant. We want it to clearly be able to :
  -  Understand the structure of the prompts
  -  Know how it should handle data
  -  Know how it should answer to the user
  -  Know it abalilities
In order to solve this problem, we must create a verry good first prompt, and find a way to make it persistant. For example we can send it at each request, or we can try to find a parameter to specify it.

### **Context** :
We then wants the AI to understand the context behind the user prompt :
  -  OS - hardware info
  -  File structure
  -  ...
  -  Previous commands / results
To do so, we have to log previous commands. Then we have to find the best way to structure the data ine a clear way to make the AI able to easyly filter data. Maybe using json or yaml could be a good solution if AI handles it.

### **User Prompt**:
We must 

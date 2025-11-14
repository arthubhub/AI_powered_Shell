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
In order to solve this problem, we must create a verry good first prompt, and find a way to make it persistant. For example we can send it at each request, or we can try to find a parameter to specify it. Finally, we do not want the ai to use data from the examples to answer, just the structure, we have to clearly anounce it.

### **Context** :
We then wants the AI to understand the context behind the user prompt :
  -  OS - hardware info
  -  File structure
  -  ...
  -  Previous commands / results
To do so, we have to log previous commands. Then we have to find the best way to structure the data ine a clear way to make the AI able to easyly filter data. Maybe using json or yaml could be a good solution if AI handles it.

### **User Prompt**:
The user prompt should be process normally. However, it could be a good feature to allow the user to ask something else to the AI concerning the previous response.

### *Aditional feature*:
The AI might need more specific context to handle user request, like analysing a file, or see the result of a specific command. A good feature could be to allow the AI to ask the program for aditional data using pre made requests.



## Usage example

### Installation
Here just run ./install.sh with the desired shell:
<img width="769" height="817" alt="image" src="https://github.com/user-attachments/assets/ab32f14d-3b41-4952-a5be-d80c83c8ce02" />

### Usage
Then just use the terminal as usual. If you need assistance, just ask!
<img width="827" height="326" alt="image" src="https://github.com/user-attachments/assets/c226ac6a-c86c-42ce-bd91-d7b09c467cb0" />

Finally, just let do the magic (it is not really magic):
<img width="1384" height="674" alt="image" src="https://github.com/user-attachments/assets/2c74be3e-aff4-4b44-bd4c-64bcf51a8fb8" />

Another example:
<img width="878" height="806" alt="image" src="https://github.com/user-attachments/assets/8dc78692-fd08-44d0-a01e-1c89d9a2f4c8" />

This shows that the tool works. However, some features are missing and the AI doesn't handle all the formating well.

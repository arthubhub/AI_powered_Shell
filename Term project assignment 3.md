# Term project assignment 3

# **Topic: AI-Augmented Shell Assistant for Context-Aware Command Line Help**

> This document is 100% human written.
> 

> *Summary   
This projects aims to add an in-shell AI LLM to enhance productivity with context aware AI helper. Being totally run in local, it would respect privacy of the user, while providing it relevant solutions.*
> 

### Project definition 2 state

Here is the final bloc of the previous document about the project:

```
Here are the next steps:
	Create the prompt for the LLM
    Give it the output format (can be inspired by ssage one)
    Standardize the context data format
	Find a way to add context specific information
    Find a way to get the field of the request
    Run additive informational commands
    Example : If the user asks why he cant connect via ssh → check network config.
	Create the LLM process
	Interact with LLM API

```

# Validation process

As the process is made of two main components, it would be important to assess them alone and together. The evaluation process will then be separated in two steps : the first one focusing on logging feature, the second one using all the tool capabilities.

## Phasis 1 : Logging

During this phase, we will be focusing on 5 main features, to check the ability to log data from the user interactions, while ensuring confidentiality and reliability:

1. Check that basic commands are logged
2. Check that more complex commands are logged
3. Check that long execution commands are logged
4. Check that concurrent commands are logged (multiple commands at same time)
5. Check access control

## Phasis 2 : Scenarios

To evaluate the project, we have to follow the objectives, and to see how good the project is at solving the problems. To do so, we can create multiple scenario in which a user could be, with some variation to test the limits. Finally, we would run these tests multiple times and assess the precision of the project.

### Scenario 1 : Find the biggest file of the directory

In this fictive scenario, the user would need to know which file of its current directory id the largest. We can create multiple prompts to test the limits of the tool:

1. Easy
    
    ```c
    $ ls -la
    $ according to command history what is the biggest file of my current directory
    ```
    
2. Medium
    
    ```c
    $ ls -la
    $ what is the biggest file of my current directory
    ```
    
3. Hard
    
    ```c
    $ what is the biggest file of my current directory
    ```
    

### Scenario 2 : Find the file containing the string “True”

In this fictive scenario, the user wants to know which file from his current directory contains the string “True”. We can create multiple prompts to test the limits of the tool:

1. Easy
    
    ```c
    $ ls -1 | while read -r l ; do echo -ne "${l}:\n$(strings ${l})\n" ; done
    $ according to command history which file contains the string 'True'
    ```
    
2. Hard
    
    ```c
    $ which file of my directory contains the string 'True'
    ```
    

### Scenario 3 : Buggy DNS

In this fictive scenario, the user is having internet connection issues: it is impossible to go on the internet from his browser.  We can create multiple prompts to test the limits of the tool:

1. Easy
    
    ```c
    $ ping -c 1 yahoo.com
    $ ping -c 1 8.8.8.8
    $ dig yahoo.com
    $ dig yahoo.com  @8.8.8.8
    $ according to command history why cant I reach internet on firefox
    ```
    
2. Hard
    
    ```c
    $ why cant I reach internet on firefox
    ```
    

### Scenario 4 : Wrong file type

In this fictive scenario, the user wants to execute a binary. However, he can’t because the binary is from the wrong OS/Arch/permissions/… We can create multiple prompts to test the limits of the tool:

1. Easy
    
    ```c
    $ ls -l file123
    $ readelf -h file123
    $ ./file123
    $ according to command history why cant I run file123
    ```
    
2. Hard
    
    ```c
    $ why cant I run file123
    ```
    

# Implementation

To implement the project, we have to define the steps of the development. As we have discussed in the previous assignment, we will have multiple main components, corresponding to the main features of the project:

- Installation
- Logging
- AI Interactions

For the whole development, I have been maintaining a CI/CD structure by implementing code and updates on github :  https://github.com/arthubhub/AI_powered_Shell/tree/main.

### Logging

For the logging of the commands, I have decided to rely on commands called by today’s shells like bash and zsh. 

To make the process of switching between normal and stable shell and shell with features in development, I implemented the code in zsh, while using BASH as my regular shell terminal. 

The first steps has been to find ways to trigger events when a command was called, and when it terminates. To do so, I have made researches on internet.

Then, I have created the main algorithm in pseudo code, allowing an easy implementation of bash or zsh code. Here was my algorithm:

```
# This file is a template file for both bash and zsh scripts

### 1. Variables declaration

## FILES
# temp file storing last command output -> user specific file and 
#   per - terminal command : "ps -p $$ -o pid="
# temp file storing new json file value -> user specific file
# json file containing list of previous commands -> user specific file
# file containing all context to be sent to ollama (user specific):
"""
{
"command_history": { 
    "date1": {"command": "ls -l", "result": ".\n..\n"}, 
    "date2": {"command": "cat ../file.txt", "result": "hello\n"} 
    },
"environment_context" : {
    "OS": "Darwin MacBook-Pro-... 22.6.0 Darwin Kernel", 
    "User": "user_name", 
    "shell": "/bin/bash", 
    "pwd": "/user/root/Desktop", 
    "directory_content": "birthday_party dhcpcd.conf" }
}
"""

## Static variables
# Max number of lines of the result to store in json file
# Max number of bytes of the result to store in json file
# Ollama model to be used
# Logging state flag -> logging enable/disable -> avoid debugging 
#    while the program take the hand on the execution AND avoir recursive calls

## Mutable variables
# Date of the running command

### 2. Functions to run once

## Check requirements (run once)
# - Python3
# - Ollama
# - Python3 ollama library
# - Ollama model

## Access control (run once)
# - Check files existence, create missing ones
# - Update files access rights (600 : - R-- --- ---)

## Check that Ollama is running
# - read the title again

### 3. Functions 

## create_context_file
# - Clear file
# - Put the json history file to the context file
# - Run commands to get additional context
# - Insert result into the context file

## ollama_interactions (maybe find a way to print result as a stream)
# Local variable : ollama result
# - call python3 with the python script that handles the communication 
#   with ollama, give the context file path and the model as a parameter
# - output result to the user

### 4. Hooks (function called automatically at specific moments)

## log_command_preexec
# - check if logging is enabled -> True = return
# - set logging flag to False -> logging in progress
# - set the date of current command (gdate +%FT%T.%3N)
# - add the current command to the json file (see logging poc)
# - set the logging flag to True -> logging can continue

## log_command_precmd
# - check if logging is enabled -> True = return
# - set logging flag to False -> logging in progress
# - wait a small time to permit the write of call output to file 
# - check if the file exists and is not emty
# - get the file content with size limit using pre defined Static Variables
# - add the result to the json file using the same date as when the command 
#   was called 
# - set the logging flag to True -> logging can continue

## command_not_found_handler , command_fails_handler
# Local var : failed_command
# Local var : mode = "1" -> quick or "2" -> reflexion
# - check if logging is enable -> false = return
# - set logging flag to False -> logging in progress
# - get the command that has produced the error -> failed_command
# - ask the user if he wants to have help : Q/q : quick , P/p : Precise 
#   (default) : F/f : False
# - if false restore context and exit (logging flag to True)
# - call create_context_file
# - call ollama_interactions
# - set the logging flag to True -> logging can continue

### 5. Add outputing of commands to log file
# - "exec > >(tee -a "$aishtmplogfile") 2>&1"

### 6. Hooks registration
# - "autoload -Uz add-zsh-hook"
# - "add-zsh-hook preexec log_command_preexec"
# - "add-zsh-hook precmd log_command_precmd"

### 7. Traps
# trap int :  interruptions during execution of ai_powered_shell -> Reconstruct 
#    the logic in case of interruptions, Log the result as if the usual post 
#    call function would do

```

### AI Interactions

In this section, I have decided to create two modes to interact with the AI in python:

- Quick : runs one prompt
- Deep : runs workers, multiple steps

Doing the first mode only would have been really simple. But since my objective was to provide real context aware help, I have decided to create something bigger.

To solve this problem, I have divided the python code into multiple interdependent components.

![image.png](Term%20project%20assignment%203/image.png)

Once again, the code is available at https://github.com/arthubhub/AI_powered_Shell.

Here is the final list of the files of the python program:

![image.png](Term%20project%20assignment%203/image%201.png)

### Installation

The installation script is pretty simple. It simply install the missing requirements, and then it adds the logging functions to the source of the used shell, as wall as python, in a directory in the user home. 

# Results

Finally, we are going to see the results. 

On an average, the interactions with LLM takes quite a long time on my computer. Also, the AI usually miss informations, and get away from its main instructions. This may be due to the length of the prompts I have created. Also, the model I am running is really small.

Concerning the logging, all main cases are working. The logging don’t stop, it even handles interruption signals. Also, it makes the distinction between real user commands, and itself. This part has taken a long time to develop but is working nicely.

Here are example results from the  “Validation process”:

### 1. Find biggest file of the current directory

Easy: (Quick)

![image.png](Term%20project%20assignment%203/image%202.png)

Medium: (Quick)

![image.png](Term%20project%20assignment%203/image%203.png)

Hard: (Deep)

![image.png](Term%20project%20assignment%203/image%204.png)

### 2. Find the file containing the string “True”

Easy: (quick)

![image.png](Term%20project%20assignment%203/image%205.png)

As you can see, the LLM is really really dumb. But we will say it is my fault.

Hard: (Deep)

![image.png](Term%20project%20assignment%203/image%206.png)

### 3. Buggy DNS

Easy: (Quick)

![image.png](Term%20project%20assignment%203/image%207.png)

Hard: (Deep)

The network worker is temporarily unavailable…

### 4. Wrong file type

Easy: (Quick)

![image.png](Term%20project%20assignment%203/image%208.png)

Hard: (Deep)

![image.png](Term%20project%20assignment%203/image%209.png)

# Conclusion

To conclude, this project has shown that is could be a very good feature to be able to have a context-aware local LLM. However, there are still a lot of limits, due to the performances of local LLMs. We have also seen that giving a too much big prompt will result to an incomprehension of the context by the LLM.
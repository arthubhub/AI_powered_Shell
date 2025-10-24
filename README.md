# AI_powered_Shell
This project implements a shell add-on to improve productivity with local LLM usage.

## Global workflow

![KSS-design](https://github.com/user-attachments/assets/945b1804-9b95-4e02-9a9c-52ded016e45a)


## Internal process

![workflow](https://github.com/user-attachments/assets/b15241bd-2c71-4e69-8727-63403d187bcb)


## Commands logging

In order to give context about previous commands and results, the add-on should log them to a file (one per session). This file will be created when initiating the shell session ( when calling `source add-on.sh` ).
The data will have to be sent to python3 script in JSON format. To do so we can either format the data asthey arrive to the file, or parse them before giving them to the python scrpit.

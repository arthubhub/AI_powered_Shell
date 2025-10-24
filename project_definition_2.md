# Term project assignment 2

# **Topic: AI-Augmented Shell Assistant for Context-Aware Command Line Help**

> This document has not been AI generated
> 

## OS feature global design

![Fig. 1: AISH workflow](Term%20project%20assignment%202%2029660a0dc9098088a37edaf9e29fa14c/KSS-design.jpg)

Fig. 1: AISH workflow

As you can see on the Fig. 1, the feature will be presented as an add-on for system shells. Using internal callbacks from modern shells, we will add a special case for unknown commands. This commands will be handled by a custom function.

## AISH requests interceptor

When modern shells captures unknown commands, they usually permit the user to chose a custom behavior. Using this pre-made feature, we will just have to plug our code into the source of the default shell to add our feature.

When the user runs an unknown command like “Why my ssh server is not accessible”, we will be able to intercept the command and perform various actions with it. To do so, we have to implement a function in the source of the shell, called:

- `command_not_found_handle()` → bash
- `command_not_found_handler()` → zsh

## AISH requests processing

By addinf a few lines in the source file of your default shell, you can specify a new source file for AISH:

```xml
$ cat "$HOME/.zshrc" | tail -2      
export AISH="$HOME/.aish"
source "$AISH/aish.sh"
```

Then, we can add the function into the `$AISH/aish.sh` file:

```xml
command_not_found_handler() {

    echo -ne "Error: '$1' not found.\n > Ask ai? (Y/n)" >&2
    read -r answer
    if [[ "$answer[1]" != "n" ]]; then
        echo "Okay, here is what bashai think about this..."
        echo "We are currently in: $PWD"
        echo "Shell              : $SHELL"
        echo "User               : $(whoami)"
        echo "OS                 : $(uname -a)"
        echo "Recent commands: $(tail -20 "$HOME/.zsh_history")"
    else
        echo "Error: $@"
    fi
}
```

## AISH command history handling

To allow the LLM to get more context about user actions (not only commands, but also commands results), we will make all output values beeing add to a log file:

```xml
autoload -Uz add-zsh-hook

aishtmplogfile="/tmp/zsh-output-$(date +%Y%m%d-%H%M%S).log"
echo "See command results in $aishtmplogfile"

typeset -g LOGGING_ENABLED=1

function log_command_preexec() {
    if (( LOGGING_ENABLED )); then
        echo ">>> $(date +'%Y-%m-%d %H:%M:%S') Executing: $1" >> "$aishtmplogfile"
    fi
}

function log_command_precmd() {
    if (( LOGGING_ENABLED )); then
        exec > >(tee -a "$aishtmplogfile") 2>&1
    else
        exec > /dev/tty 2>&1
    fi
}

# hooks
add-zsh-hook preexec log_command_preexec
add-zsh-hook precmd log_command_precmd
```

To avoid `command_not_found_handler` actions also beeing logged, we will set the LOGGING flag to 0 at the beginning of the functions, and put it back to 1 at the end.

## LLM Interactions

For simplicity and robustness, the LLM interactions should better be handled via a python script. In order to do that, we will have to save context data as JSON in a file, and give it to the python program as an input. 

Then, the python program will interact with the LLM and return the result to the bash script.

Finally, the bash script will output the LLM answer to the user.

## To go further…

Here are the next steps:

- Create the prompt for the LLM
    - Give it the output format (can be inspired by ssage one)
    - Standardize the context data format
- Find a way to add context specific information
    - Find a way to get the field of the request
    - Run additive informational commands
    - Example : If the user asks why he cant connect via ssh → check network config.
- Create the LLM process
- Interact with LLM API
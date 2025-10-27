# @arthub
# 2025-10-27 
# Logging proof of concept
# This file can be loaded at shell init and every command/result will be logged in /tmp/aishistory.json
# If you find bugs, please say it




autoload -Uz add-zsh-hook                                                                                                                                                                                    

aishtmplogfile="/tmp/zsh-output-$(date +%Y%m%d_%H%M%S).log"
echo "See command results in $aishtmplogfile"
echo '{"command_history": {}}' > /tmp/aishistory.json
cat /tmp/aishistory.json

current_aish_command_date=""
typeset -gi LOGGING_ENABLED=1
typeset -gi LOGGING_IN_PROGRESS=0

function log_command_preexec() {
    if [[ $LOGGING_IN_PROGRESS -eq 1 ]]; then
        return
    fi
    
    if [[ $LOGGING_ENABLED -eq 1 ]]; then
        LOGGING_IN_PROGRESS=1
        current_aish_command_date="$(date +'%Y-%m-%d_%H:%M:%S')"
        
        # from https://unix.stackexchange.com/questions/548892/how-to-json-escape-input
        jq --arg d "$current_aish_command_date" --arg f "$1" \
          '.command_history[($d)] = {command: {content: $f}, result: {content: ""}}' \
          < /tmp/aishistory.json > /tmp/aishistory.json.tmp && \
          mv /tmp/aishistory.json.tmp /tmp/aishistory.json

        echo "" > "$aishtmplogfile"
        LOGGING_IN_PROGRESS=0
    fi
}

function log_command_precmd() {
    if [[ $LOGGING_IN_PROGRESS -eq 1 ]]; then
        return
    fi
    
    if [[ $LOGGING_ENABLED -eq 1 && -n "$current_aish_command_date" ]]; then
        LOGGING_IN_PROGRESS=1
        
        sleep 0.1
        
        local output=""
        if [[ -f "$aishtmplogfile" && -s "$aishtmplogfile" ]]; then
            output="$(tail -100 "$aishtmplogfile" 2>/dev/null || echo "")"
        fi
        
        # from https://unix.stackexchange.com/questions/548892/how-to-json-escape-input
        jq --arg d "$current_aish_command_date" --arg f "$output" \
          '.command_history[($d)].result.content = $f' \
          < /tmp/aishistory.json > /tmp/aishistory.json.tmp && \
          mv /tmp/aishistory.json.tmp /tmp/aishistory.json
        
        LOGGING_IN_PROGRESS=0
    fi
}

add-zsh-hook preexec log_command_preexec
add-zsh-hook precmd log_command_precmd

command_not_found_handler() {
    local cmd="$1"
    shift
    
    LOGGING_ENABLED=0
    LOGGING_IN_PROGRESS=1
    
    echo -ne "Error: '$cmd' not found.\n > Ask bashia? (Y/n): " >&2
    read -r answer
    
    if [[ "${answer[1]}" != "n" && "${answer[1]}" != "N" ]]; then
        echo "Okay, here is what bashai think about this..."
        echo "We are currently in: $PWD"
        echo "Shell              : $SHELL"
        echo "User               : $(whoami)"
        echo "OS                 : $(uname -a)"
        echo "Recent commands: $(tail -20 "$HOME/.zsh_history" 2>/dev/null || echo "No history available")"
        echo "-----------------------"
        echo "Result of last commands:"
        if [[ -f "$aishtmplogfile" ]]; then
            tail -50 "$aishtmplogfile" 2>/dev/null || echo "No log available"
        else
            echo "No log file available"
        fi
    else
        echo "Error: command not found: $cmd" >&2
    fi
    
    LOGGING_IN_PROGRESS=0
    LOGGING_ENABLED=1
    
    return 127
}

exec > >(tee -a "$aishtmplogfile") 2>&1

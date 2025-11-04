# @arthub
# 2025-10-27 
# Logging proof of concept
# This file can be loaded at shell init and every command/result will be logged in /tmp/aishistory.json
# If you find bugs, please say it




autoload -Uz add-zsh-hook                                                                                                                                                                                    

aishtmplogfile="/tmp/zsh-output-$USER-$(date +%Y%m%d_%H%M%S).log"
aishjsonlogfile="/tmp/aishistory_$USER.json"
aishjsonlogtmpfile="/tmp/aishistory_$USER.json.tmp"


echo "See command results in $aishtmplogfile"



# Create files :
if [ -f "$aishjsonlogfile" ]; then
    echo "Reusing existing command_history"
else
    echo '{"command_history": {}}' > "$aishjsonlogfile"
fi
echo "" > "$aishtmplogfile"
echo "" > "$aishjsonlogtmpfile"

# Access control
chmod 600 "$aishtmplogfile" "$aishjsonlogfile" "$aishjsonlogtmpfile" # to avoid other users to read history

#Debugging - printthe dates of the commands of the current user
jq -r '.command_history | keys[]'  "$aishjsonlogfile"


# Global variables
current_aish_command_date=""
LINES_LIMIT="100"
CHARS_LIMIT="2000"


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
          < "$aishjsonlogfile" > "$aishjsonlogtmpfile" && \
          cp "$aishjsonlogtmpfile" "$aishjsonlogfile"

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
          < "$aishjsonlogfile" > "$aishjsonlogtmpfile" && \
          cp "$aishjsonlogtmpfile" "$aishjsonlogfile"
        
        LOGGING_IN_PROGRESS=0
    fi
}

# Handle Ctrl+C interruptions
TRAPINT() {
    if [[ $LOGGING_ENABLED -eq 1 && -n "$current_aish_command_date" ]]; then
        local prev_in_progress=$LOGGING_IN_PROGRESS
        LOGGING_IN_PROGRESS=1
        
        local output=""
        if [[ -f "$aishtmplogfile" && -r "$aishtmplogfile" && -s "$aishtmplogfile" ]]; then
            output="$(tail -100 "$aishtmplogfile" 2>/dev/null || echo "")"
        fi
        
        # Append interruption marker
        if [[ -n "$output" ]]; then
            output="$output
^C (interrupted)"
        else
            output="^C (interrupted)"
        fi
        
        
        jq --arg d "$current_aish_command_date" --arg f "$output" \
          '.command_history[($d)].result.content = $f' \
          < "$output" > "$aishjsonlogtmpfile" && \
          cp "$aishjsonlogtmpfile" "$aishjsonlogfile"


        current_aish_command_date=""
        LOGGING_IN_PROGRESS=$prev_in_progress
    fi
    return 130
}

# Handle other signals for robustness
TRAPTERM() {
    TRAPINT
    return 143
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
        echo "Recent commands: $(tail -n "$LINES_LIMIT" "$HOME/.zsh_history" | tail -c "$CHARS_LIMIT" 2>/dev/null || echo "No history available")"
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

exec > >(tee -a "$aishtmplogfile" 2>/dev/null || cat) 2>&1

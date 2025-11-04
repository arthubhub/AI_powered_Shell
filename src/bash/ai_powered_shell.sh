#!/usr/bin/env zsh
# AI-Powered Shell Assistant
# Compatible with ZSH
# This script logs commands and provides AI assistance for errors


### 1. VARIABLES DECLARATION


## FILES
CURRENT_PID="$(ps -p $$ -o pid= | tr -d ' ')"
TEMP_LAST_OUTPUT="/tmp/bash-output-${USER}-${CURRENT_PID}-$(date +%Y%m%d_%H%M%S).log"
LOGS_JSON="/tmp/ai_powered_shell_${USER}.json"
TEMP_LOGS_JSON="/tmp/ai_powered_shell-${USER}-${CURRENT_PID}.json.tmp"
CONTEXT_FILE="/tmp/ai_context-${USER}-${CURRENT_PID}.txt"

## STATIC VARIABLES
MAX_LOGGED_LINES="50"
MAX_LOGGED_BYTES="2000"
OLLAMA_MODEL="mistral"
typeset -gi LOGGING_STATE=1  # 1 = enabled, 0 = disabled

## MUTABLE VARIABLES
CURRENT_COMMAND_DATE=""


### 2. FUNCTIONS TO RUN ONCE


check_requirements() {
    local missing_requirements=0
    
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is required but not installed." >&2
        missing_requirements=1
    fi
    
    if ! command -v ollama &> /dev/null; then
        echo "Error: ollama is required but not installed." >&2
        echo "Install from: https://ollama.ai" >&2
        missing_requirements=1
    fi
    
    if ! python3 -c "import ollama" 2>/dev/null; then
        echo "Error: Python ollama library is required." >&2
        echo "Install with: pip3 install ollama" >&2
        missing_requirements=1
    fi
    
    if command -v ollama &> /dev/null; then
        if ! ollama list 2>/dev/null | grep -q "^${OLLAMA_MODEL}"; then
            echo "Warning: Ollama model '${OLLAMA_MODEL}' not found." >&2
            echo "Pull with: ollama pull ${OLLAMA_MODEL}" >&2
            missing_requirements=1
        fi
    fi
    
    if [[ $missing_requirements -eq 1 ]]; then
        echo "Please install missing requirements before using AI-powered shell." >&2
        return 1
    fi
    
    return 0
}

setup_access_control() {
    if [[ ! -f "$LOGS_JSON" ]]; then
        echo '{"command_history": {}}' > "$LOGS_JSON"
    fi
    
    touch "$TEMP_LAST_OUTPUT" "$TEMP_LOGS_JSON" "$CONTEXT_FILE"
        chmod 600 "$TEMP_LAST_OUTPUT" "$LOGS_JSON" "$TEMP_LOGS_JSON" "$CONTEXT_FILE" 2>/dev/null
}

check_ollama_running() {
    if ! pgrep -x "ollama" > /dev/null 2>&1; then
        echo "Warning: Ollama service doesn't appear to be running." >&2
        echo "Start it with: ollama serve" >&2
        return 1
    fi
    return 0
}


### 3. FUNCTIONS


create_context_file() { # This will be modified to be 100% json
    > "$CONTEXT_FILE"
    
    cat >> "$CONTEXT_FILE" << EOF
=== SYSTEM CONTEXT ===
Current Directory: $PWD
Shell: $SHELL
User: $(whoami)
OS: $(uname -a)
Date: $(date)

=== COMMAND HISTORY ===
EOF
    
    # Add JSON history (last 10 commands)
    if [[ -f "$LOGS_JSON" ]]; then
        echo "Recent command history:" >> "$CONTEXT_FILE"
        jq -r '.command_history | to_entries | .[-10:] | .[] | "[\(.key)] Command: \(.value.command.content)\nResult: \(.value.result.content)\n"' \
            "$LOGS_JSON" 2>/dev/null >> "$CONTEXT_FILE" || echo "No history available" >> "$CONTEXT_FILE"
    fi
    
    # Add recent shell history
    echo -e "\n=== RECENT SHELL COMMANDS ===" >> "$CONTEXT_FILE"
    if [[ -f "$HOME/.zsh_history" ]]; then
        tail -n 20 "$HOME/.zsh_history" 2>/dev/null | tail -c "$MAX_LOGGED_BYTES" >> "$CONTEXT_FILE" || echo "No shell history available" >> "$CONTEXT_FILE"
    fi
    
    # Add environment information
    echo -e "\n=== ENVIRONMENT ===" >> "$CONTEXT_FILE"
    echo "PATH: $PATH" >> "$CONTEXT_FILE"
    echo "HOME: $HOME" >> "$CONTEXT_FILE"
    
    # Add last command output if available
    if [[ -f "$TEMP_LAST_OUTPUT" && -s "$TEMP_LAST_OUTPUT" ]]; then
        echo -e "\n=== LAST COMMAND OUTPUT ===" >> "$CONTEXT_FILE"
        tail -n "$MAX_LOGGED_LINES" "$TEMP_LAST_OUTPUT" | tail -c "$MAX_LOGGED_BYTES" >> "$CONTEXT_FILE"
    fi
}

ollama_interaction() {
    local prompt="$1"
    local mode="${2:-quick}"  # quick or reflexion
    
    # Create Python script for Ollama interaction
    echo "Calling python ..."
    local result="$(echo "run pyhton code")"
    echo "> ${result}"
}


### 4. HOOKS


log_command_preexec() {
    # Skip if logging disabled
    if [[ $LOGGING_STATE -eq 0 ]]; then
        return
    else
        # Disable logging during this function
        LOGGING_STATE=0
        
        # Set current command date with milliseconds (use gdate if available, otherwise date)
        if command -v gdate &> /dev/null; then
            CURRENT_COMMAND_DATE="$(gdate +%FT%T.%3N)"
        else
            CURRENT_COMMAND_DATE="$(date +%Y-%m-%dT%H:%M:%S)"
        fi
        
        # Add command to JSON history
        jq --arg d "$CURRENT_COMMAND_DATE" --arg cmd "$1" \
            '.command_history[($d)] = {command: {content: $cmd}, result: {content: ""}}' \
            < "$LOGS_JSON" > "$TEMP_LOGS_JSON" 2>/dev/null && \
            cp "$TEMP_LOGS_JSON" "$LOGS_JSON"
        
        # Clear output log
        > "$TEMP_LAST_OUTPUT"
        
        # Re-enable logging
        LOGGING_STATE=1
    fi
}

log_command_precmd() {
    # Skip if logging disabled or no command date set
    if [[ $LOGGING_STATE -eq 0 || -z "$CURRENT_COMMAND_DATE" ]];then
        return
    else
        
        # Disable logging during this function
        LOGGING_STATE=0
        
        # Small delay to ensure output is written
        sleep 0.05
        
        # Get command output with limits
        local output=""
        if [[ -f "$TEMP_LAST_OUTPUT" && -s "$TEMP_LAST_OUTPUT" ]]; then
            output="$(tail -n "$MAX_LOGGED_LINES" "$TEMP_LAST_OUTPUT" 2>/dev/null | head -c "$MAX_LOGGED_BYTES")"
        fi
        
        # Update JSON with result
        jq --arg d "$CURRENT_COMMAND_DATE" --arg res "$output" \
            '.command_history[($d)].result.content = $res' \
            < "$LOGS_JSON" > "$TEMP_LOGS_JSON" 2>/dev/null && \
            cp "$TEMP_LOGS_JSON" "$LOGS_JSON"
        
        # Re-enable logging
        LOGGING_STATE=1
    fi
}

command_not_found_handler() {
    local failed_command="$1"
    shift
    local args="$@"
    
    # Return if logging is disabled
    if [[ $LOGGING_STATE -ne 0 ]]; then
        # Disable logging
        LOGGING_STATE=0
        
        echo -e "\nError: Command '$failed_command' not found." >&2
        echo -ne "Would you like AI assistance? [Q]uick / [P]recise / [N]o (default: Q): " >&2
        read -r answer
        
        local mode="quick"
        case "${answer:l}" in
            q|"")
                mode="quick"
                ;;
            p)
                mode="reflexion"
                ;;
            n|f)
                echo "No assistance requested." >&2
                LOGGING_STATE=1
                return 127
                ;;
            *)
                echo "Invalid option. Using quick mode." >&2
                mode="quick"
                ;;
        esac
        
        # Create context and get AI help
        create_context_file
        
        local prompt="The command '$failed_command $args' was not found. What should I do?"
        ollama_interaction "$prompt" "$mode"
        
        # Re-enable logging
        LOGGING_STATE=1
    fi
    return 127
}

handle_command_failure() {
    local exit_code=$?
    local failed_command="$1"
    
    # Only handle actual failures (non-zero exit codes, excluding 127 which is command not found)
    # Return if logging is disabled
    if [[ $exit_code -eq 0 || $exit_code -eq 127 ]]; then
        return $exit_code
    fi
    if [[ $LOGGING_STATE -eq 0 ]];then
        return $exit_code
    fi
    
    # Disable logging
    LOGGING_STATE=0
    
    echo -e "\nCommand failed with exit code $exit_code: '$failed_command'" >&2
    echo -ne "Would you like AI assistance? [Q]uick / [P]recise / [N]o (default: N): " >&2
    read -r answer
    
    local mode="quick"
    case "${answer:l}" in
        q)
            mode="quick"
            ;;
        p)
            mode="reflexion"
            ;;
        n|"")
            LOGGING_STATE=1
            return $exit_code
            ;;
        *)
            echo "Invalid option. Skipping assistance." >&2
            LOGGING_STATE=1
            return $exit_code
            ;;
    esac
    
    # Create context and get AI help
    create_context_file
    
    local prompt="The command '$failed_command' failed with exit code $exit_code. What went wrong and how can I fix it?"
    ollama_interaction "$prompt" "$mode"
    
    # Re-enable logging
    LOGGING_STATE=1
    
    return $exit_code
}

################################################################################
### 7. TRAPS
################################################################################

TRAPINT() {
    # Handle interrupt during command execution
    if [[ $LOGGING_STATE -eq 1 && -n "$CURRENT_COMMAND_DATE" ]]; then
        LOGGING_STATE=0
        
        local output=""
        if [[ -f "$TEMP_LAST_OUTPUT" && -s "$TEMP_LAST_OUTPUT" ]]; then
            output="$(tail -n "$MAX_LOGGED_LINES" "$TEMP_LAST_OUTPUT" 2>/dev/null | head -c "$MAX_LOGGED_BYTES")"
        fi
        
        # Append interruption marker
        if [[ -n "$output" ]]; then
            output="$output\n^C (interrupted)"
        else
            output="^C (interrupted)"
        fi
        
        # Update JSON with interrupted result
        jq --arg d "$CURRENT_COMMAND_DATE" --arg res "$output" \
            '.command_history[($d)].result.content = $res' \
            < "$LOGS_JSON" > "$TEMP_LOGS_JSON" 2>/dev/null && \
            cp "$TEMP_LOGS_JSON" "$LOGS_JSON"
        
        CURRENT_COMMAND_DATE=""
        LOGGING_STATE=1
    fi
    
    return 130
}

TRAPTERM() {
    TRAPINT
    return 143
}

################################################################################
### INITIALIZATION
################################################################################

# Run setup functions
if check_requirements; then
    setup_access_control
    check_ollama_running
    
    echo "AI-Powered Shell Assistant initialized."
    echo "Logs: $LOGS_JSON"
    echo "Output: $TEMP_LAST_OUTPUT"
    
    # Load zsh hooks
    autoload -Uz add-zsh-hook
    
    ### 6. HOOKS REGISTRATION
    add-zsh-hook preexec log_command_preexec
    add-zsh-hook precmd log_command_precmd
    
    ### 5. REDIRECT OUTPUT TO LOG FILE
    exec > >(tee -a "$TEMP_LAST_OUTPUT" 2>/dev/null) 2>&1
else
    echo "AI-Powered Shell Assistant could not be initialized due to missing requirements." >&2
fi
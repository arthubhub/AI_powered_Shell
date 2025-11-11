#!/usr/bin/env bash
# AI-Powered Shell Assistant
# Compatible with Bash
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
LOGGING_STATE=1  # 1 = enabled, 0 = disabled

## MUTABLE VARIABLES
CURRENT_COMMAND_DATE=""
LAST_COMMAND=""


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
    echo "" > "$CONTEXT_FILE"
    
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
    if [[ -f "$HOME/.bash_history" ]]; then
        tail -n 20 "$HOME/.bash_history" 2>/dev/null | tail -c "$MAX_LOGGED_BYTES" >> "$CONTEXT_FILE" || echo "No shell history available" >> "$CONTEXT_FILE"
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

command_to_json() {
    local timestamp="$1"
    local command="$2"
    
    # Add command to JSON history with empty result
    jq --arg d "$timestamp" --arg cmd "$command" \
        '.command_history[($d)] = {command: {content: $cmd}, result: {content: ""}}' \
        < "$LOGS_JSON" > "$TEMP_LOGS_JSON" 2>/dev/null && \
        cp "$TEMP_LOGS_JSON" "$LOGS_JSON"
}

result_to_json() {
    local timestamp="$1"
    local result="$2"
    
    # Update JSON with result only
    jq --arg d "$timestamp" --arg res "$result" \
        '.command_history[($d)].result.content = $res' \
        < "$LOGS_JSON" > "$TEMP_LOGS_JSON" 2>/dev/null && \
        cp "$TEMP_LOGS_JSON" "$LOGS_JSON"
}


### 4. HOOKS


log_command_preexec() {
    # Skip if logging disabled
    if [[ $LOGGING_STATE -eq 0 ]]; then
        return
    fi
    LOGGING_STATE=0

    # Save the command string for the next hook
    LAST_COMMAND="$BASH_COMMAND"

    # Set current command date
    if command -v gdate &> /dev/null; then
        CURRENT_COMMAND_DATE="$(gdate +%FT%T.%3N)"
    else
        CURRENT_COMMAND_DATE="$(date +%Y-%m-%dT%H:%M:%S)"
    fi

    command_to_json "$CURRENT_COMMAND_DATE" "$LAST_COMMAND"
    echo "" > "$TEMP_LAST_OUTPUT"

    LOGGING_STATE=1
}


log_command_precmd() {
    local last_exit_code=$?
    
    # Skip if disabled or no command recorded
    if [[ $LOGGING_STATE -eq 0 || -z "$CURRENT_COMMAND_DATE" || -z "$LAST_COMMAND" ]]; then
        return
    fi
    LOGGING_STATE=0

    # Capture output from temp file if it exists
    local output=""
    if [[ -s "$TEMP_LAST_OUTPUT" ]]; then
        output="$(cat "$TEMP_LAST_OUTPUT")"
    fi

    # Save trimmed output for JSON
    echo "$output" | tail -n "$MAX_LOGGED_LINES" | head -c "$MAX_LOGGED_BYTES" > "$TEMP_LAST_OUTPUT"
    result_to_json "$CURRENT_COMMAND_DATE" "$output"

    # Handle command failures
    if [[ $last_exit_code -ne 0 && $last_exit_code -ne 127 ]]; then
        handle_command_failure "$LAST_COMMAND" "$last_exit_code"
    fi

    # Cleanup
    LAST_COMMAND=""
    LOGGING_STATE=1
}


command_not_found_handle() {
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
        answer_lower=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
        case "$answer_lower" in
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
    local failed_command="$1"
    local exit_code="$2"
    
    # Only handle actual failures (non-zero exit codes, excluding 127 which is command not found)
    # Return if logging is disabled
    if [[ $exit_code -eq 0 || $exit_code -eq 127 ]]; then
        return $exit_code
    fi
    if [[ $LOGGING_STATE -eq 0 ]]; then
        return $exit_code
    fi
    
    # Disable logging
    LOGGING_STATE=0
    
    echo -e "\nCommand failed with exit code $exit_code: '$failed_command'" >&2
    echo -ne "Would you like AI assistance? [Q]uick / [P]recise / [N]o (default: N): " >&2
    read -r answer
    
    local mode="quick"
    answer_lower=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    case "$answer_lower" in
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


### 5. COMMAND EXECUTION WRAPPER
run_and_log_command() {
    local cmd="$1"
    {
        eval "$cmd"
    } 2>&1 | tee "$TEMP_LAST_OUTPUT"
}


### 6. TRAPS


trapint() {
    if [[ $LOGGING_STATE -eq 1 && -n "$CURRENT_COMMAND_DATE" ]]; then
        LOGGING_STATE=0

        # If output file exists, take its tail
        local temp_output=""
        if [[ -s "$TEMP_LAST_OUTPUT" ]]; then
            temp_output="$(tail -n "$MAX_LOGGED_LINES" "$TEMP_LAST_OUTPUT" 2>/dev/null | head -c "$MAX_LOGGED_BYTES")"
        fi

        # Append the ^C marker directly into the file
        echo "^C (interrupted)" >> "$TEMP_LAST_OUTPUT"

        # And update JSON entry using the file, not a shell variable
        result_to_json "$CURRENT_COMMAND_DATE" "$(cat "$TEMP_LAST_OUTPUT")"

        CURRENT_COMMAND_DATE=""
        LOGGING_STATE=1
    fi

    return 130
}

trapterm() {
    trapint
    return 143
}


### 7. INITIALIZATION


# Run setup functions
if check_requirements; then
    setup_access_control
    check_ollama_running
    
    echo "AI-Powered Shell Assistant initialized."
    echo "Logs: $LOGS_JSON"
    echo "Output: $TEMP_LAST_OUTPUT"
    
    # Set up Bash hooks using DEBUG and PROMPT_COMMAND
    trap 'log_command_preexec' DEBUG
    trap 'trapint' INT
    trap 'trapterm' TERM
    
    # Add to PROMPT_COMMAND (preserve existing commands)
    if [[ -z "$PROMPT_COMMAND" ]]; then
        PROMPT_COMMAND="log_command_precmd"
    else
        PROMPT_COMMAND="log_command_precmd; $PROMPT_COMMAND"
    fi
    
else
    echo "AI-Powered Shell Assistant could not be initialized due to missing requirements." >&2
fi
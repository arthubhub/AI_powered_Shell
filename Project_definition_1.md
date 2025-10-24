# Term project assignment 1

# **Topic Proposal: AI-Augmented Shell Assistant for Context-Aware Command Line Help**

## **Introduction**

As AI large language models (LLMs) like Copilot, Claude, and ChatGPT Codex become integral to development and system administration, the command line interface (CLI) remains a static, context-unaware environment. Developers and sysadmins frequently switch between their terminal and web browsers to search for commands, debug errors, or recall past solutions. This context-switching leads to productivity losses, cognitive overhead, and increased risk of errors.

To address this gap, I propose a user-level shell plugin that integrates a local AI assistant directly into the terminal. This tool will provide real-time, context-aware command suggestions, file-specific help, and transparent logging of AI-generated actions. By bringing AI assistance into the CLI, this project bridges the divide between traditional command-line workflows and the interactive, adaptive interfaces expected in the AI era.

---

## **The Problem**

### **Context-Switching and Productivity Loss**

Modern development and system administration rely heavily on AI-powered tools for code completion, debugging, and documentation. However, the CLI lacks native AI integration. Users must:

- Manually search the web for command syntax or error fixes.
- Copy-paste solutions from AI chatbots or documentation into their terminal.
- Recall or re-derive commands they’ve used before but don’t remember.

This workflow is inefficient and disruptive. For example:

- A developer compiling cross-architecture code (e.g., `aarch64` on `x86_64`) may need to look up compiler flags, emulator usage, and debugging steps, breaking their focus.
- Sysadmins troubleshooting logs or config files must juggle between their terminal and external resources, increasing the risk of mistakes.

### **Missing Features in Current Solutions**

Existing tools fall short in several ways:

- Generic AI chatbots lack awareness of the user’s environment, files, or command history.
- Shell autocompletion only works for predefined commands and lacks contextual understanding.
- Local documentation tools, like man, require exact queries and don’t adapt to the user’s specific context.

There is no unified, intelligent assistant that understands the user’s environment, recalls past actions, and provides file-aware, command-specific help directly in the terminal.

---

## **The Solution**

### **AI-Powered Shell Plugin**

I propose a lightweight, local AI assistant that developers can invoke from their terminal. The tool will:

1. Intercept unknown or failed commands and provide context-aware suggestions.
2. Access relevant files (with user permission) to offer targeted help (e.g., explaining errors in a `Makefile` or suggesting fixes for a script).
3. Log all AI-generated commands for transparency and security.
4. Integrate seamlessly with existing shells (Bash, Zsh) as a plugin or script.

### **Implementation**

- **Language**: Python (for AI logic) + Bash (for shell integration).
- **AI Backend**: Local LLM (e.g., [Ollama](https://ollama.ai/) or [Llama.cpp](https://github.com/ggerganov/llama.cpp)) to ensure privacy and offline functionality.
- **File Access**: Restricted to user-owned files/directories, with explicit consent.
- **Security**: Commands are never auto-executed; users must confirm before running.

### **Example Workflow**

1. User types: `ai how to compile _pwn_me.c in aarch64 without PIE?`
2. Plugin:
    - Checks `.bash_history` for similar commands.
    - Reads `_pwn_me.c`
    - Give info about installed tools
    - Queries the local AI model for a suggestion.
3. Output:
    
    ```
    Based on your history and file context, try:
    $ aarch64-linux-gnu-gcc _pwn_me.c -o pwn_me.bin -fno-pie -fPIC
    To run on x86_64:
    $ qemu-aarch64 pwn_me.bin
    Execute? [y/N]
    
    ```
    
4. If executed, the command is logged to `~/.ai_shell_commands.log`.
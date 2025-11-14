#!/usr/bin/env python3
"""
AI-Powered Shell Assistant - Ollama Context Handler
Processes command history and system context to provide AI assistance
"""
import sys
import os
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
import requests
import re


# ANSI Color codes
class Colors:
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'


def format_response(text):
    """Replace placeholders with actual Bash color codes"""
    text = re.sub(r'\$\{CYAN\}', Colors.CYAN, text)
    text = re.sub(r'\$\{NC\}', Colors.NC, text)
    text = re.sub(r'\$\{BOLD\}', Colors.BOLD, text)
    text = re.sub(r'\$\{GREEN\}', Colors.GREEN, text)
    text = re.sub(r'\$\{YELLOW\}', Colors.YELLOW, text)
    text = re.sub(r'\$\{RED\}', Colors.RED, text)
    text = re.sub(r'\$\{BLUE\}', Colors.BLUE, text)
    
    text = re.sub(r'\{CYAN\}', Colors.CYAN, text)
    text = re.sub(r'\{NC\}', Colors.NC, text)
    text = re.sub(r'\{BOLD\}', Colors.BOLD, text)
    text = re.sub(r'\{GREEN\}', Colors.GREEN, text)
    text = re.sub(r'\{YELLOW\}', Colors.YELLOW, text)
    text = re.sub(r'\{RED\}', Colors.RED, text)
    text = re.sub(r'\{BLUE\}', Colors.BLUE, text)
    
    return text


def load_command_history(json_file):
    """Load command history from JSON file"""
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{json_file}' not found.{Colors.NC}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error: Invalid JSON in '{json_file}': {e}{Colors.NC}", file=sys.stderr)
        sys.exit(1)


def detect_os_and_package_manager():
    """Detect OS distribution and package manager"""
    os_info = {
        'distro': 'Unknown',
        'package_manager': 'unknown',
        'package_install_command': 'unknown'
    }
    
    # Try to read /etc/os-release
    try:
        with open('/etc/os-release', 'r') as f:
            os_release = f.read()
            if 'arch' in os_release.lower():
                os_info['distro'] = 'Arch Linux'
                os_info['package_manager'] = 'pacman'
                os_info['package_install_command'] = 'sudo pacman -S'
            elif 'ubuntu' in os_release.lower() or 'debian' in os_release.lower():
                os_info['distro'] = 'Debian/Ubuntu'
                os_info['package_manager'] = 'apt/apt-get'
                os_info['package_install_command'] = 'sudo apt install'
            elif 'fedora' in os_release.lower() or 'rhel' in os_release.lower():
                os_info['distro'] = 'Fedora/RHEL'
                os_info['package_manager'] = 'dnf/yum'
                os_info['package_install_command'] = 'sudo dnf install'
    except FileNotFoundError:
        pass
    
    # Check which package managers are available
    for pm in ['pacman', 'apt', 'apt-get', 'dnf', 'yum', 'zypper']:
        if subprocess.run(['which', pm], capture_output=True).returncode == 0:
            os_info['package_manager'] = pm
            if pm == 'pacman':
                os_info['package_install_command'] = 'sudo pacman -S'
            elif pm in ['apt', 'apt-get']:
                os_info['package_install_command'] = f'sudo {pm} install'
            elif pm in ['dnf', 'yum']:
                os_info['package_install_command'] = f'sudo {pm} install'
            elif pm == 'zypper':
                os_info['package_install_command'] = 'sudo zypper install'
            break
    
    return os_info


def get_system_info():
    """Gather system information"""
    os_info = detect_os_and_package_manager()
    
    return {
        'cwd': os.getcwd(),
        'shell': os.environ.get('SHELL', 'unknown'),
        'user': os.environ.get('USER', 'unknown'),
        'os': f"{platform.system()} {platform.release()}",
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'distro': os_info['distro'],
        'package_manager': os_info['package_manager'],
        'package_install_command': os_info['package_install_command']
    }


def get_directory_content(path='.', max_depth=2):
    """Get directory structure"""
    try:
        result = subprocess.run(
            ['ls', '-lah', path],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout if result.returncode == 0 else "Unable to list directory"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "Unable to list directory"


def format_context_as_markdown(command_history, system_info, question=None):
    """Format all context data as Markdown with XML tags for emphasis"""
    
    # Use XML tags to emphasize critical system information
    context_md = f"""<system_context>
<critical_info>
**IMPORTANT: This system uses {system_info['distro']}**
**Package Manager: {system_info['package_manager']}**
**Correct package installation command: {system_info['package_install_command']} <package_name>**
</critical_info>

## System Details
- **Current Directory:** {system_info['cwd']}
- **Shell:** {system_info['shell']}
- **User:** {system_info['user']}
- **Operating System:** {system_info['os']} ({system_info['machine']})
- **Python Version:** {system_info['python_version']}
- **Date:** {system_info['date']}
</system_context>

---

<command_history>
## Recent Command History

"""
    
    history_items = list(command_history.get('command_history', {}).items())
    # Skip first command (usually the cat of json file itself) and get last 10
    recent_commands = history_items[-11:-1] if len(history_items) > 11 else history_items[:-1] if len(history_items) > 1 else []
    
    if not recent_commands:
        context_md += "*No command history available*\n"
    else:
        for idx, (timestamp, data) in enumerate(recent_commands, 1):
            command_content = data.get('command', {}).get('content', 'N/A')
            result_content = data.get('result', {}).get('content', '')
            
            context_md += f"### {idx}. [{timestamp}]\n"
            context_md += f"**Command:** `{command_content}`\n"
            
            if result_content:
                truncated_result = result_content[:500] + "..." if len(result_content) > 500 else result_content
                context_md += f"**Output:**\n```\n{truncated_result}\n```\n\n"
            else:
                context_md += "**Output:** *(no output captured yet)*\n\n"
    
    context_md += "</command_history>\n\n---\n\n"
    
    context_md += "<directory_content>\n"
    context_md += "## Current Directory Content\n\n"
    context_md += "```\n"
    context_md += get_directory_content()
    context_md += "```\n"
    context_md += "</directory_content>\n\n---\n\n"
    
    context_md += "<environment_variables>\n"
    context_md += "## Key Environment Variables\n\n"
    for key in ['PATH', 'HOME', 'SHELL', 'LANG', 'TERM']:
        value = os.environ.get(key, 'N/A')
        if key == 'PATH' and len(value) > 200:
            value = value[:200] + "..."
        context_md += f"- **{key}:** `{value}`\n"
    context_md += "</environment_variables>\n\n---\n\n"
    
    if question:
        context_md += f"<user_question>\n## User's Question\n\n{question}\n</user_question>\n"
    
    try:
        with open("/tmp/prompt.md", "w") as file:
            file.write(context_md)
    except IOError:
        pass 
    
    return context_md


def call_ollama(context_markdown, model='mistral', question=None):
    """Call Ollama API with the formatted context"""
    try:
        import ollama
    except ImportError:
        print(f"{Colors.RED}Error: 'ollama' Python package is not installed.{Colors.NC}", file=sys.stderr)
        print(f"{Colors.YELLOW}Install it with: pip install ollama{Colors.NC}", file=sys.stderr)
        sys.exit(1)
    
    system_prompt = """You are AI_POWERED_SHELL, a command-line assistant specialized in Linux/Unix systems.

Your role is to analyze the provided context and diagnose shell command issues with precision and clarity.

<core_principles>
1. **Read ALL context sections carefully** - Each XML-tagged section contains important information
2. **Base analysis ONLY on provided context** - Never invent files, commands, or facts not present in the context
3. **Think step-by-step** - Break down the problem logically before suggesting solutions
4. **Be specific and actionable** - Provide concrete commands that can be executed immediately
5. **When uncertain, ask questions** - If context is missing or ambiguous, request clarification rather than guessing
</core_principles>

<reasoning_approach>
Before formulating your response, systematically analyze:
1. What command did the user try to execute? (from <user_question>)
2. What system are they on? (from <critical_info>)
3. What happened when they ran it? (from <command_history>)
4. What related context exists? (from <directory_content>, <environment_variables>)
5. What is the root cause? (logic error, missing dependency, permission issue, wrong syntax, etc.)
</reasoning_approach>

<response_structure>
Your responses must follow this format:
1. **One-line diagnosis** - Clearly state the root problem
2. **Brief explanation** - Why did this happen? (1-2 sentences max)
3. **Actionable solutions** - List 2-4 specific commands or steps to fix the issue
4. **Optional: Additional context** - If helpful, suggest diagnostic commands to gather more info

Use color tags for clarity:
- ${CYAN} ... ${NC} - For executable shell commands
- ${BOLD} some keywords ... ${NC} - For emphasis on important terms
- ${RED} error ${NC} - For problems or failures
- ${GREEN} success ${NC} - For correct approaches
- ${YELLOW} warning ${NC} - For cautions or important notes
</response_structure>

<quality_guidelines>
- Prioritize clarity over cleverness
- Use the user's actual system tools (check <critical_info>)
- Match your response length to problem complexity
- Avoid generic advice - be specific to THIS context
- Don't repeat information already in the context
</quality_guidelines>"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': context_markdown
                }
            ]
        )
        
        return response['message']['content']
    
    except Exception as e:
        print(f"{Colors.RED}Error calling Ollama: {e}{Colors.NC}", file=sys.stderr)
        print(f"{Colors.YELLOW}Make sure Ollama is running with: ollama serve{Colors.NC}", file=sys.stderr)
        sys.exit(1)


def print_header(text):
    """Print a formatted header"""
    width = 80
    print(f"\n{Colors.CYAN}{'=' * width}{Colors.NC}")
    print(f"{Colors.BOLD}{text.center(width)}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * width}{Colors.NC}\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Usage: python ollama_context_handler.py <context_json_file> [question]{Colors.NC}", file=sys.stderr)
        print(f"\n{Colors.BOLD}Example:{Colors.NC}", file=sys.stderr)
        print(f"  {Colors.CYAN}python ollama_context_handler.py /tmp/ai_powered_shell_user.json{Colors.NC}", file=sys.stderr)
        print(f"  {Colors.CYAN}python ollama_context_handler.py /tmp/ai_powered_shell_user.json \"Why did my last command fail?\"{Colors.NC}", file=sys.stderr)
        sys.exit(1)
    
    context_file = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "Analyze the command history and provide insights about recent commands and any potential issues."
    
    print_header("AI-POWERED SHELL ASSISTANT")
    
    print(f"{Colors.BOLD}Loading context from:{Colors.NC} {Colors.CYAN}{context_file}{Colors.NC}")
    print(f"{Colors.BOLD}Question:{Colors.NC} {question}\n")
    
    command_history = load_command_history(context_file)
    
    system_info = get_system_info()
    
    # Show detected system info
    print(f"{Colors.GREEN}✓{Colors.NC} Detected OS: {Colors.BOLD}{system_info['distro']}{Colors.NC}")
    print(f"{Colors.GREEN}✓{Colors.NC} Package Manager: {Colors.BOLD}{system_info['package_manager']}{Colors.NC}")
    
    context_md = format_context_as_markdown(command_history, system_info, question)
    
    debug_file = f"/tmp/ollama_context_debug_{os.getpid()}.md"
    try:
        with open(debug_file, 'w') as f:
            f.write(context_md)
        print(f"{Colors.GREEN}✓{Colors.NC} Debug context saved to {Colors.CYAN}{debug_file}{Colors.NC}")
    except IOError:
        print(f"{Colors.YELLOW}!{Colors.NC} Could not save debug context file")
    
    print(f"\n{Colors.YELLOW}...{Colors.NC} Calling Ollama API (model: {Colors.BOLD}mistral{Colors.NC})...\n")
    
    response = call_ollama(context_md, model='mistral', question=question)
    formatted_response = format_response(response)
    
    print_header("OLLAMA RESPONSE")
    print(formatted_response)
    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.NC}\n")


if __name__ == "__main__":
    main()
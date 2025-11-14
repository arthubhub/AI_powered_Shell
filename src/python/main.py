# first tests

import requests, re

def format_response(text):
    # Replace placeholders with actual Bash color codes
    text = re.sub(r'\$\{CYAN\}', '\033[0;36m', text)
    text = re.sub(r'\$\{NC\}', '\033[0m', text)
    text = re.sub(r'\$\{BOLD\}', '\033[1m', text)
    return text


response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "mistral",
        "stream": False, 
        "messages": [
            {
                "role": "system",
                "content": 'You are AI_POWERED_SHELL, a command-line assistant.\
Your role is to analyze the provided context and user command, then respond with a quick, clear, and actionable summary.\
\
### Rules:\
1. **Only use the provided context and command.** Never invent, assume, or reference files/commands not mentioned in the context.\
2. **Never repeat examples or generic advice.** Only respond to the actual user input.\
3. **Be concise:** One-line summary, followed by a short list of actionable solutions.\
4. **Syntax:**\
   - Replace ```bash with "${CYAN}" and ``` with "${NC}".\
   - Replace `word` with "${BOLD}word${NC}".\
5. **Format:**\
   - Start with a one-line summary of the issue.\
   - List only relevant, actionable solutions.\
6. **If the context is unclear or missing, ask for clarification. Do NOT guess or use examples.**\
\
### Example of a good response:\
The context indicates your binary (${BOLD}ch64${NC}) is a 32-bit MIPS executable, but your system is x86_64.\
To run it:\
- Recompile for x64: ${CYAN}gcc -m64 ch64.c -o ch64${NC}\
- Use QEMU: ${CYAN}qemu-mips ch64${NC}'
            },
            {
                "role": "user",
                "content": '[CONTEXT]$ ls\
ch64  lib  Makefile  run.sh\
$ file ch64 \
ch64: ELF 32-bit MSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, interpreter /lib/ld.so.1, for GNU/Linux 3.2.0, BuildID[sha1]=449e7f2913faba0676cbf7c8d87ca63fcf993b64, not stripped\
$ uname -a\
Linux archlinux 6.17.3-arch2-1 #1 SMP PREEMPT_DYNAMIC Fri, 17 Oct 2025 13:29:06 +0000 x86_64 GNU/Linux\
$ pwd\
/home/arthub/Documents/Root-me/app-system/ELF MIPS - Basic ROP/Multiarch-PwnBox/shared/chall\
$ whoami\
arthub\
$ host\
host         hostapd      hostapd_cli  hostid       hostname     hostnamectl  \
$ hostname\
archlinux\
    [PROMPT] Why cant i run my binary'
            }
        ]
    }
)
text_response=response.json()['message']['content']
formatted_response = format_response(text_response)
print(formatted_response)

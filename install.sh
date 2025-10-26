#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "        _____                                               _            _    _           _ _ 
   /\  (_____)                                             | |          | |  | |         | | |
  /  \    _           ____   ___  _ _ _  ____  ____ ____ _ | |           \ \ | | _   ____| | |
 / /\ \  | |         |  _ \ / _ \| | | |/ _  )/ ___) _  ) || |            \ \| || \ / _  ) | |
| |__| |_| |_ _______| | | | |_| | | | ( (/ /| |  ( (/ ( (_| |_______ _____) ) | | ( (/ /| | |
|______(_____|_______) ||_/ \___/ \____|\____)_|   \____)____(_______|______/|_| |_|\____)_|_|
                     |_|                                                                      
 _                               _           _                                                
| |                         _   | |         | |                                               
| | _  _   _     ____  ____| |_ | | _  _   _| | _                                             
| || \| | | |   / _  |/ ___)  _)| || \| | | | || \                                            
| |_) ) |_| |  ( ( | | |   | |__| | | | |_| | |_) )                                           
|____/ \__  |   \_||_|_|    \___)_| |_|\____|____/                                            
      (____/                                                                                  "
echo -e "${NC}"

# Variables
AI_POWERED_SHELL="AI_POWERED_SHELL"
DEFAULT_SHELL="bash"
USER_HOME="${HOME}"
BASHRC_PATH="${USER_HOME}/.bashrc"
ZSHRC_PATH="${USER_HOME}/.zshrc"
AI_POWERED_SHELL_PATH="${USER_HOME}/.${AI_POWERED_SHELL}"
BASH_SCRIPT_NAME="ai_powered_shell.sh"
ZSH_SCRIPT_NAME="ai_powered_shell.zsh"


update_context() {
    local shell_type="${1:-bash}"
    
    echo -e "${BLUE}Initializing AI Powered Shell for ${BOLD}${shell_type}${NC}${BLUE}...${NC}"
    
    if [[ "${shell_type}" != "bash" && "${shell_type}" != "zsh" ]]; then
        echo -e "${RED}Error: shell type '${shell_type}' unsupported. Use 'bash' or 'zsh'.${NC}"
        return 1
    fi
    
    DEFAULT_SHELL="${shell_type}"
    
    if [[ "${DEFAULT_SHELL}" = "zsh" ]]; then
        CURRENT_SCRIPT_NAME="${ZSH_SCRIPT_NAME}"
    else
        CURRENT_SCRIPT_NAME="${BASH_SCRIPT_NAME}"
    fi
    
    echo -e "${GREEN}+ Context updated for ${DEFAULT_SHELL} shell${NC}"
    return 0
}

update_rc() {
    local shell_type="${1:-bash}"
    local rc_path=""
    local script_name=""
    
    if [[ "${shell_type}" = "zsh" ]]; then
        rc_path="${ZSHRC_PATH}"
        script_name="${ZSH_SCRIPT_NAME}"
    else
        rc_path="${BASHRC_PATH}"
        script_name="${BASH_SCRIPT_NAME}"
    fi
    
    echo -e "${BLUE}Checking ${BOLD}${shell_type}rc${NC}${BLUE} configuration...${NC}"
    
    if [[ ! -f "${rc_path}" ]]; then
        echo -e "${YELLOW}${rc_path} does not exist, file created...${NC}"
        touch "${rc_path}"
    fi
    
    local rc_stubs="$(cat "${rc_path}" | grep "${AI_POWERED_SHELL}")"
    
    if [[ "${rc_stubs}" != "" ]]; then
        echo -e "${YELLOW}! Link to ${USER_HOME}/.${AI_POWERED_SHELL} already exists in ${shell_type}rc${NC}"
    else
        echo -ne "\n\n" >> "${rc_path}"
        echo "export AI_POWERED_SHELL_PATH=\"${AI_POWERED_SHELL_PATH}\"" >> "${rc_path}"
        echo "source \"\${AI_POWERED_SHELL_PATH}/${script_name}\"" >> "${rc_path}"
        echo -e "${GREEN}+ Link to ${USER_HOME}/.${AI_POWERED_SHELL} has been added to ${shell_type}rc${NC}"
    fi
}

update_files() {
    local shell_type="${1:-bash}"
    local script_name=""
    local src_dir=""
    
    if [[ "${shell_type}" = "zsh" ]]; then
        script_name="${ZSH_SCRIPT_NAME}"
        src_dir="src/zsh"
    else
        script_name="${BASH_SCRIPT_NAME}"
        src_dir="src/bash"
    fi
    
    echo -e "${BLUE}Updating files for ${BOLD}${shell_type}${NC}${BLUE}...${NC}"
    
    if [[ -d "${AI_POWERED_SHELL_PATH}" ]]; then
        echo -e "${YELLOW}Removing old files from ${AI_POWERED_SHELL_PATH}...${NC}"
        rm -rf "${AI_POWERED_SHELL_PATH}"
    fi
    
    echo -e "${BLUE}Creating ${AI_POWERED_SHELL_PATH}...${NC}"
    mkdir -p "${AI_POWERED_SHELL_PATH}"
    
    if [[ -f "${src_dir}/${script_name}" ]]; then
        echo -e "${BLUE}Copying ${script_name}...${NC}"
        cp "${src_dir}/${script_name}" "${AI_POWERED_SHELL_PATH}/"
        echo -e "${GREEN}+ ${script_name} copied${NC}"
    else
        echo -e "${RED}Error: ${src_dir}/${script_name} not found${NC}"
        return 1
    fi
    
    if [[ -d "src/python" ]]; then
        echo -e "${BLUE}Copying Python files...${NC}"
        cp -r "src/python" "${AI_POWERED_SHELL_PATH}/"
        echo -e "${GREEN}+ Python files copied${NC}"
    else
        echo -e "${YELLOW}! Warning: src/python directory not found${NC}"
    fi
    
    echo -e "${GREEN}+ Files updated successfully.${NC}"
}

install_ai_powered_shell() {
    local shell_type="${1}"
    
    if [[ -z "${shell_type}" ]]; then
        echo -e "${RED}Error: Shell type not specified.${NC}"
        echo -e "${YELLOW}Usage: install_ai_powered_shell <bash|zsh>${NC}"
        return 1
    fi
    
    if [[ "${shell_type}" != "bash" && "${shell_type}" != "zsh" ]]; then
        echo -e "${RED}Error: Invalid shell type '${shell_type}'.${NC}"
        echo -e "${YELLOW}Usage: install_ai_powered_shell <bash|zsh>${NC}"
        return 1
    fi
    
    echo -e "${MAGENTA}${BOLD}==========================================${NC}"
    echo -e "${MAGENTA}${BOLD}  Installing AI Powered Shell for ${shell_type}${NC}"
    echo -e "${MAGENTA}${BOLD}==========================================${NC}"
    echo ""
    
    update_context "${shell_type}" || return 1
    echo ""
    update_rc "${shell_type}" || return 1
    echo ""
    update_files "${shell_type}" || return 1
    
    echo ""
    echo -e "${GREEN}${BOLD}==========================================${NC}"
    echo -e "${GREEN}${BOLD}  Installation complete for ${shell_type}!${NC}"
    echo -e "${CYAN}  Restart your ${shell_type} or run:${NC}"
    echo -e "${WHITE}  source ~/.${shell_type}rc${NC}"
    echo -e "${GREEN}${BOLD}==========================================${NC}"
}


if [[ "$#" == 1 ]]; then
    install_ai_powered_shell "$1"
else
    echo -e "${YELLOW}Usage: ${NC}${WHITE}$0 <shell_type>${NC}"
    echo -e "  ${CYAN}Example:${NC}"
    echo -e "    ${WHITE}$0 bash${NC}"
    echo -e "    ${WHITE}$0 zsh${NC}"
fi
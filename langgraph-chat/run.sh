#!/bin/bash

# LangGraph Chat Agent - Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the agent

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}LangGraph Chat Agent${NC}"
echo "========================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Please create a .env file with your API keys:"
    echo "  OPENAI_API_KEY=sk-..."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Run the chat agent
echo -e "${GREEN}Starting chat agent...${NC}"
echo ""
python chat.py

# Deactivate is automatic when script ends

#!/bin/bash

# LangGraph Document Q&A - Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the pipeline

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}LangGraph Document Q&A${NC}"
echo "======================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Please create a .env file with your API keys:"
    echo "  OPENAI_API_KEY=your_key_here"
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

# Run the Q&A pipeline
echo -e "${GREEN}Starting document Q&A...${NC}"
echo ""
python qna.py

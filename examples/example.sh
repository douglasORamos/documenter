#!/bin/bash
# Example script for analyzing API documentation

# Configuration
INPUT_DOC="api-documentation.pdf"
OUTPUT_FILE="enriched-api.postman_collection.json"
API_BASE_URL="https://api.example.com"
AUTH_TOKEN="your-bearer-token-here"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting API Documentation Analysis...${NC}\n"

# Example 1: Basic analysis (no API testing)
echo -e "${GREEN}Example 1: Basic analysis${NC}"
python cli.py analyze \
  --input "$INPUT_DOC" \
  --output "basic-$OUTPUT_FILE" \
  --collection-name "My API - Basic"

echo -e "\n${GREEN}Example 2: With API testing${NC}"
python cli.py analyze \
  --input "$INPUT_DOC" \
  --output "$OUTPUT_FILE" \
  --test-api \
  --base-url "$API_BASE_URL" \
  --auth-token "$AUTH_TOKEN" \
  --collection-name "My API - Enriched"

echo -e "\n${GREEN}Example 3: Info about a file${NC}"
python cli.py info "$INPUT_DOC"

echo -e "\n${BLUE}Analysis complete!${NC}"


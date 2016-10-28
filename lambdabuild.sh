#!/bin/bash
GREEN='\033[0;32m'
NC='\033[0m'

mkdir build

echo -e "${GREEN}Creating temporary build dir...${NC}"
cp requirements.txt build/
cd build/

echo -e "${GREEN}Installing requirements to build...${NC}"
pip install -r requirements.txt -t .

echo -e "${GREEN}Creating invoices zip...${NC}"
zip -r invoice.zip .

mv invoice.zip ..

echo -e "${GREEN}Cleaning up...${NC}"
cd ..
rm -rf build/

echo -e "${GREEN}Done.${NC}"


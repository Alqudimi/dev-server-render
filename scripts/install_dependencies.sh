#!/bin/bash

# This script installs dependencies for all projects based on their language

PROJECTS_DIR="/app/projects"

for project in "$PROJECTS_DIR"/*; do
    if [ -d "$project" ]; then
        echo "Checking dependencies for project: $(basename "$project")"
        
        # Python project
        if [ -f "$project/requirements.txt" ]; then
            echo "Installing Python dependencies..."
            pip install -r "$project/requirements.txt"
        fi
        
        # Node.js project
        if [ -f "$project/package.json" ]; then
            echo "Installing Node.js dependencies..."
            npm install --prefix "$project"
        fi
        
        # Java project (Maven)
        if [ -f "$project/pom.xml" ]; then
            echo "Installing Java dependencies..."
            mvn -f "$project/pom.xml" dependency:resolve
        fi
        
        # Add more language support as needed
    fi
done

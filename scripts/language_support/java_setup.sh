#!/bin/bash

# Java Environment Setup Script

echo "Setting up Java environment..."

# Install JDK versions (already installed in Dockerfile)
# Configure alternatives if needed
update-alternatives --config java
update-alternatives --config javac

# Install build tools
if ! command -v mvn &> /dev/null; then
    echo "Installing Maven..."
    apt-get install -y maven
fi

if ! command -v gradle &> /dev/null; then
    echo "Installing Gradle..."
    apt-get install -y gradle
fi

echo "Java environment setup complete!"

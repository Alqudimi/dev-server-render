#!/bin/bash

# Node.js Environment Setup Script

NODE_VERSIONS=("14.18.1" "16.13.0" "17.3.0")

echo "Setting up Node.js environments..."

# Install nvm
if ! command -v nvm &> /dev/null; then
    echo "Installing nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Install Node.js versions
for version in "${NODE_VERSIONS[@]}"; do
    if ! nvm ls | grep -q "$version"; then
        echo "Installing Node.js $version..."
        nvm install "$version"
    else
        echo "Node.js $version already installed"
    fi
done

# Set default Node.js version
nvm use 16.13.0

# Install package managers
npm install -g yarn pnpm

echo "Node.js environment setup complete!"

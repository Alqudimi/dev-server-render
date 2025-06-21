#!/bin/bash

echo "Setting up development environment..."

# Install pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"

# Install nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install required Python versions
pyenv install 3.8.12
pyenv install 3.9.7
pyenv global 3.9.7

# Install Node.js versions
nvm install 14.18.1
nvm install 16.13.0
nvm use 16.13.0

# Install other language tools
# Java, Go, Rust, Ruby, PHP are already installed in Dockerfile

echo "Environment setup complete!"

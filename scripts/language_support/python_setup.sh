
#!/bin/bash

# Python Environment Setup Script

PYTHON_VERSIONS=("3.8.12" "3.9.7" "3.10.2")

echo "Setting up Python environments..."

# Install pyenv
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
fi

# Install Python versions
for version in "${PYTHON_VERSIONS[@]}"; do
    if ! pyenv versions | grep -q "$version"; then
        echo "Installing Python $version..."
        pyenv install "$version"
    else
        echo "Python $version already installed"
    fi
done

# Set default Python version
pyenv global 3.9.7

# Install package managers
pip install --upgrade pip pipenv poetry

echo "Python environment setup complete!"

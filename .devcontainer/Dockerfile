ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# Python 3.9
RUN sudo apt update && sudo apt install -y software-properties-common && \
    sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt install -y python3.9 python3.9-venv
# Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
# Azure Developer CLI
RUN curl -fsSL https://aka.ms/install-azd.sh | bash
# Azure Functions Core Tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \\
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list' && \
    sudo apt update && sudo apt install -y azure-functions-core-tools-4

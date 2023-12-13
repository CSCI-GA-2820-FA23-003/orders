# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:fa23
FROM rofrano/pipeline-selenium:latest

# Add any tools that are needed beyond Python 3.11
RUN apt-get update && \
    apt-get install -y sudo vim make git zip tree curl wget jq procps net-tools && \
    apt-get autoremove -y && \
    apt-get clean -y

# Become a regular user for development
ARG USERNAME=vscode
USER $USERNAME

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh

# Set up the Python development environment
WORKDIR /app
COPY requirements.txt .
RUN sudo pip install -U pip wheel && \
    sudo pip install -r requirements.txt

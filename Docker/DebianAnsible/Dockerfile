# Start from the Debian base image
FROM debian:latest

# Update package list and install Python 3, pip, and venv (required for virtual environments)
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Ansible into the isolated virtual environment
RUN pip install ansible ansible-runner

# Set the working directory for your project
WORKDIR /usr/src/app

# Set a command to keep the container running
CMD ["sleep", "infinity"]
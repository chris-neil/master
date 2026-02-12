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

# --- Add ansible-lint here ---
RUN pip install ansible-lint
# ------------------------------
    
# 1. Set the locale environment variable to prevent 'unsupported locale' errors
#    This is critical for ansible-galaxy to run correctly in minimal environments.
ENV LC_ALL C.UTF-8

# 2. Install the Check Point Ansible collections
#    This command uses the 'pip' environment defined in the PATH above.
RUN ansible-galaxy collection install check_point.gaia
RUN ansible-galaxy collection install check_point.mgmt

# Set the working directory for your project
WORKDIR /usr/src/app

# Set a command to keep the container running
CMD ["sleep", "infinity"]
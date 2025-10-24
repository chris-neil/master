# Use an official Node.js runtime as the base image.
# We're using the "lts-alpine" tag which is based on Alpine Linux,
# making the final image very small. "lts" means Long-Term Support.
FROM node:18-alpine

# Set the working directory inside the container.
# All subsequent commands will be run from this directory.
WORKDIR /app

# Copy package.json and package-lock.json into the container.
# This is a key optimization. By copying these files first,
# Docker can cache this layer. If you only change your source code,
# this dependency installation layer won't have to be rebuilt.
COPY package*.json ./

# Install application dependencies.
RUN npm install

# Copy the rest of the application's source code into the container.
COPY . .

# Expose the port that the Node.js application will run on.
# This doesn't publish the port, but it documents which port to publish with `docker run`.
EXPOSE 3000

# Define the command to run the application.
# This is the command that will be executed when the container starts.
CMD ["node", "app.js"]
#https://registry.terraform.io/providers/CheckPointSW/checkpoint/latest/docs

terraform {
  required_providers {
    checkpoint = {
      source = "CheckPointSW/checkpoint"
      version = "2.9.0"
    }
  }
}

# Configure Check Point Provider for GAIA API
provider "checkpoint" {
  server = "192.168.182.11"
  username = "admin"
  password = "Admin123"
  context = "gaia_api"
}

# Set machine hostname
resource "checkpoint_hostname" "hostname" {
  name = "terraform_host"
}
#https://registry.terraform.io/providers/CheckPointSW/checkpoint/latest/docs

terraform {
  required_providers {
    checkpoint = {
      source = "CheckPointSW/checkpoint"
      version = "2.9.0"
    }
  }
}

# Configure Check Point Provider for Management API
provider "checkpoint" {
  server = "192.168.182.10"
  username = "admin"
  password = "Admin123"
  context = "web_api"
  session_name = "Terraform session"
}

# Create network object
resource "checkpoint_management_network" "network" {
  name = "My network"
  subnet4 = "192.0.2.0"
  mask_length4 = "24"
  # ...   
}
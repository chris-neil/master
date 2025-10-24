#https://registry.terraform.io/providers/CheckPointSW/checkpoint/latest/docs

terraform {
  required_providers {
    checkpoint = {
      source = "CheckPointSW/checkpoint"
      version = "2.9.0"
    }
  }
}

# Configure Check Point Provider for Management API for specific domain
provider "checkpoint" {
  server = "192.168.182.8"
  username = "admin"
  password = "Admin123"
  context = "web_api"
  domain = "MyDomain"
  session_file_name = "mydomain.json"
  session_name = "Terraform session"
}

# Create network object
resource "checkpoint_management_network" "network" {
  name = "My network"
  subnet4 = "192.0.2.0"
  mask_length4 = "24"
  # ...   
}
#https://registry.terraform.io/providers/elsudano/vmworkstation/1.0.2/docs

terraform {
  required_providers {
    vmworkstation = {
      source  = "elsudano/vmworkstation"
      version = "1.1.6"
      #version = 1.0.4
    }
  }
  required_version = ">= 0.15.4"
}

provider "vmworkstation" {
  user     = var.vmws_user
  password = var.vmws_password
  url      = var.vmws_url
  https    = false
  debug    = true
}

resource "vmworkstation_vm" "test_machine" {
  sourceid     = var.vmws_resource_frontend_sourceid
  denomination = var.vmws_resource_frontend_denomination
  description  = var.vmws_resource_frontend_description
  path         = var.vmws_resource_frontend_path
  processors   = var.vmws_resource_frontend_processors
  memory       = var.vmws_resource_frontend_memory
}
variable "vmws_user" {
  type        = string
  description = "(Required) The username to connect to REST API"
  default     = "admin"
}
variable "vmws_password" {
  type        = string
  description = "(Required) The password to connect to REST API"
  default     = "Admin!23"
}
variable "vmws_url" {
  type        = string
  description = "(Required) The URL of the REST API"
  default     = "http://localhost:8697/"
}
variable "vmws_resource_frontend_sourceid" {
  type        = string
  description = "(Required) The ID of the VM that to use for clone at the new"
  default     = "6QOKB7KLJOJTLSH8CNDQ5CN1UGNOHM0F" ## This is the Gaia Template ID
}
variable "vmws_resource_frontend_denomination" {
  type        = string
  description = "(Required) The Name of VM in WS"
  default     = "NewInstance"
}
variable "vmws_resource_frontend_description" {
  type        = string
  description = "(Required) The Description at later maybe to explain the instance"
  default     = "Newly created VM using Terraform"
}
variable "vmws_resource_frontend_path" {
  type        = string
  description = "(Required) The Path where will be our instance in VmWare"
  default     = "C:\\Users\\cneil\\Documents\\Virtual Machines"
}
variable "vmws_resource_frontend_processors" {
  type        = number
  description = "(Required) The number of processors of the Virtual Machine"
  default     = "2"
}
variable "vmws_resource_frontend_memory" {
  type        = number
  description = "(Required) The size of memory to the Virtual Machine"
  default     = "512"
}
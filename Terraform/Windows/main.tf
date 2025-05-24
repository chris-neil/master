#https://registry.terraform.io/providers/hashicorp/ad/latest/docs

terraform {
  required_providers {
    ad = {
      source = "hashicorp/ad"
      version = "0.5.0"
    }
  }
}

# provider attributes
variable username { default = "ctneil" }
variable password { default = "Admin123" }

provider "ad" {
  winrm_hostname         = "192.168.182.2"
  winrm_username         = var.username
  winrm_password         = var.password
  krb_realm              = "TEST.LOCAL"
#  krb_conf               = "krb5.conf"
#  krb_spn                = "WIN-R1DO7G0N9CQ"
  winrm_port             = 5985
  winrm_proto            = "http"
#  winrm_pass_credentials = true 
}


# all user attributes
variable principal_name2 { default = "testuser2" }
variable samaccountname2 { default = "testuser2" }
variable container      { default = "CN=Users,DC=test,DC=local" }

resource "ad_user" "u2" {
  principal_name            = var.principal_name2
  sam_account_name          = var.samaccountname2
  display_name              = "Terraform Test User"
  container                 = var.container
  initial_password          = "Password"
  city                      = "City"
  company                   = "Company"
  country                   = "us"
  department                = "Department"
  description               = "Description"
  division                  = "Division"
  email_address             = "some@email.com"
  employee_id               = "id"
  employee_number           = "number"
  fax                       = "Fax"
  given_name                = "GivenName"
  home_directory            = "HomeDirectory"
  home_drive                = "HomeDrive"
  home_phone                = "HomePhone"
  home_page                 = "HomePage"
  initials                  = "Initia"
  mobile_phone              = "MobilePhone"
  office                    = "Office"
  office_phone              = "OfficePhone"
  organization              = "Organization"
  other_name                = "OtherName"
  po_box                    = "POBox"
  postal_code               = "PostalCode"
  state                     = "State"
  street_address            = "StreetAddress"
  surname                   = "Surname"
  title                     = "Title"
  smart_card_logon_required = false
  trusted_for_delegation    = false
}
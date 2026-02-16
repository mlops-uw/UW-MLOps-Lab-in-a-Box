variable "ssh_public_key" {
  type        = string
  description = "Public SSH key"
}

variable "user_object_id" {
  type        = string
  description = "Azure AD Object ID of the user to assign the compute instance to"
}

variable "tenant_id" {
  type        = string
  description = "Azure AD Tenant ID"
}
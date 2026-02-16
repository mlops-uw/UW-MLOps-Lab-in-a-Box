variable "ssh_public_key" {
  type        = string
  description = "Public SSH key"
}

variable "user_object_id" {
  type        = string
  description = "Azure AD Object ID of the user to assign the compute instance to"
  value       = "2e45ddbe-50e2-4849-89c6-152bb08e956f" # Replace with your actual user object ID
}

variable "tenant_id" {
  type        = string
  description = "Azure AD Tenant ID"
  value       = "f6b6dd5b-f02f-441a-99a0-162ac5060bd2" # Replace with your actual tenant ID
}
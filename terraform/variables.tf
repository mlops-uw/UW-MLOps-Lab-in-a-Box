# variable "ssh_public_key" {
#   type        = string
#   description = "Public SSH key"
# }

# variable "user_object_id" {
#   type        = string
#   description = "Azure AD Object ID of the user to assign the compute instance to"
# }

# variable "tenant_id" {
#   type        = string
#   description = "Azure AD Tenant ID"
# }

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group to create resources in"
}

variable name {
  type        = string
  description = "the name of the storage account."
}

variable account_tier {
  type        = string
  description = "the performance tier of the storage account. Valid values are 'Standard' and 'Premium'."
}

variable account_replication_type {
  type        = string
  description = "the replication strategy for the storage account. Valid values are 'LRS', 'GRS', 'RAGRS', and 'ZRS'."
}

variable container_name {
  type        = string
  description = "the name of the storage container."
}

variable container_access_type {
  type        = string
  description = "the access level of the storage container. Valid values are 'private', 'blob', and 'container'."
}

variable virtual_network_name {
  type        = string
  description = "The name of the virtual network"
}

variable address_space{
    type = list(string)
    description = "The address space that is used the virtual network."
}

variable subnet_name {
  type        = string
  description = "The name of the subnetwork"
}

variable address_prefixes{
    type = list(string)
    description = "The address prefixes to use for the subnet"
}

variable application_insights_name{
    type = string
    description = "Specifies the name of the Application Insights component"
}

variable application_type{
    type = string
    description = "Specifies the type of Application Insights to create."
}

variable key_vault_name{
    type = string
    description = "Specifies the name of the Key Vault"
}

variable sku_name{
    type = string
    description = "The Name of the SKU used for this Key Vault"
}

variable workspace_name{
    type = string
    description = "Specifies the name of the Machine Learning Workspace"
}

variable type{
    type = string
    description = "Specifies the type of Managed Service Identity that should be configured on this Machine Learning Workspace"
}

variable datastore_name{
  type = string
  description = "The name of the Machine Learning DataStore"
}

variable ml_instance_name{
    type = string
    description = "The name which should be used for this Machine Learning Compute Instance"
}

variable machine_size {
    type = string
    description = "The Virtual Machine Size."
}

variable authorization_type{
    type = string
    description = "The Compute Instance Authorization type"
}

variable assign_to_user{
    type = object({
        object_id = string
        tenant_id = string
    })
    description = "A user explicitly assigned to a personal compute instance."
}

variable description{
    type = string
    description = "The description of the Machine Learning Compute Instance."
}

variable tags{
    type = object({
        name = string
    })
    description = "A mapping of tags which should be assigned to the Machine Learning Compute Instance."
}

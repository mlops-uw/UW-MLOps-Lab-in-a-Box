
variable key_vault_name{
    type = string
    description = "Specifies the name of the Key Vault"
}

variable secret_name{
    type = string
    description = "Specifies the name of the Key Vault Secret."
}

variable secret_value{
    type = string
    description = "Specifies the value of the Key Vault Secret."
}

variable sku_name{
    type = string
    description = "The Name of the SKU used for this Key Vault"
}


# variable object_id{
#     type = string
#     description = "User's AAD Object Id"
# }
  
variable object_id_sp{
    type = string
    description = "Object Id of the Service Principle"
}

variable tenant_id{
    type = string
    description = "User's AAD Tenant Id"
}

variable location{
    type = string
    description = "the Azure region where the workspace will be created."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group to create resources in"
}
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

variable tenant_id{
    type = string
    description = "The Azure Active Directory tenant ID that should be used for authenticating requests to the key vault"
}

variable sku_name{
    type = string
    description = "The Name of the SKU used for this Key Vault"
}

variable workspace_name{
    type = string
    description = "Specifies the name of the Machine Learning Workspace"
}

variable storage_account_id{
    type = string
    description = "The ID of the Storage Account associated with this Machine Learning Workspace"
}

variable identity{
    type = object({
        type = string
    })
    description = "An identity block"
}

variable datastore_name{
    type = string
    description = "The name of the Machine Learning DataStore"
}

variable storage_container_id{
    type = string
    description = "The ID of the Storage Account Container."
}

variable account_key{
    type = string
    description = "The access key of the Storage Account."
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
  
variable subnet_resource_id{
    type = string
    description = "Virtual network subnet resource ID the compute nodes belong to"
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

variable location{
    type = string
    description = "the Azure region where the workspace will be created."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group to create resources in"
}
variable application_insights_name{
    type = string
    description = "Specifies the name of the Application Insights component"
}

variable application_type{
    type = string
    description = "Specifies the type of Application Insights to create."
}

variable workspace_name{
    type = string
    description = "Specifies the name of the Machine Learning Workspace"
}

variable storage_account_id{
    type = string
    description = "The ID of the Storage Account associated with this Machine Learning Workspace"
}

variable key_vault_id{
    type = string
    description = "The ID of the Key Vault associated with this Machine Learning Workspace"
}

variable type{
    type = string
    description = "Specifies the type of Managed Service Identity that should be configured on this Machine Learning Workspace"
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

variable object_id_sp{
    type = string
    description = "Service Principal's Object Id"
}
  
variable tenant_id{
    type = string
    description = "User's AAD Tenant Id"
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
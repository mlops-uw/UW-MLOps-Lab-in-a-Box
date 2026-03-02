variable name {
  type        = string
  description = "the name of the storage account."
}

variable resource_group_name {
  type        = string
  description = "the name of the resource group in which to create the storage account."
}

variable location {
  type        = string
  description = "the Azure region where the storage account will be created."
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



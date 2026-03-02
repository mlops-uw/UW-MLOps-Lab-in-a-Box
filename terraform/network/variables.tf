variable virtual_network_name {
  type        = string
  description = "The name of the virtual network"
}

variable address_space{
    type = list(string)
    description = "The address space that is used the virtual network."
}

variable location{
    type = string
    description = "the Azure region where the network will be created."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group to create resources in"
}

variable subnet_name {
  type        = string
  description = "The name of the subnetwork"
}

variable address_prefixes{
    type = list(string)
    description = "The address prefixes to use for the subnet"
}
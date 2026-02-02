# terraform {
#   required_providers {
#     azurerm = {
#       source  = "hashicorp/azurerm"
#       version = "=4.1.0"
#     }
#   }
# }

# provider "azurerm" {
#   features {}
#   resource_provider_registrations = "none"

# }

# data "azurerm_resource_group" "example" {
#   name     = "mlops"
# }

# # Create a virtual network within the resource group
# resource "azurerm_virtual_network" "example" {
#   name                = "example-network"
#   resource_group_name = data.azurerm_resource_group.example.name
#   location            = data.azurerm_resource_group.example.location
#   address_space       = ["10.0.0.0/16"]
# }


terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }

  resource_provider_registrations = "none"
}

data "azurerm_client_config" "current" {

}

data "azurerm_resource_group" "example" {
  name     = var.resource_group_name
}

# resource "azurerm_storage_account" "example" {
#   name                     = "taxizonelookup"
#   resource_group_name      = data.azurerm_resource_group.example.name
#   location                 = data.azurerm_resource_group.example.location
#   account_tier             = "Standard"
#   account_replication_type = "LRS"
# }

# resource "azurerm_storage_container" "example" {
#   name                  = "taxidata"
#   storage_account_name    = azurerm_storage_account.example.name
#   container_access_type = "private"
# }
# // since file is so big upload manually
# # resource "azurerm_storage_blob" "example" {
# #   name                   = "taxi_zone_lookup.csv"
# #   storage_account_name   = azurerm_storage_account.example.name
# #   storage_container_name = azurerm_storage_container.example.name
# #   type                   = "Block"
# #   source                 = "../taxi_zone_lookup.csv"
# # }

# resource "azurerm_application_insights" "example" {
#   name                = "workspace-mlops"
#   location            = data.azurerm_resource_group.example.location
#   resource_group_name = data.azurerm_resource_group.example.name
#   application_type    = "web"
# }

# resource "azurerm_key_vault" "example" {
#   name                = "finalcapstonevault"
#   location            = data.azurerm_resource_group.example.location
#   resource_group_name = data.azurerm_resource_group.example.name
#   tenant_id           = data.azurerm_client_config.current.tenant_id
#   sku_name            = "premium"
# }

# resource "azurerm_machine_learning_workspace" "example" {
#   name                    = "finalworkspacecapstone"
#   location                = data.azurerm_resource_group.example.location
#   resource_group_name     = data.azurerm_resource_group.example.name
#   application_insights_id = azurerm_application_insights.example.id
#   key_vault_id            = azurerm_key_vault.example.id
#   storage_account_id      = azurerm_storage_account.example.id

#   identity {
#     type = "SystemAssigned"
#   }
# }

# resource "azurerm_machine_learning_datastore_blobstorage" "example" {
#  name                 = "mlops_datastore"
#  workspace_id         = azurerm_machine_learning_workspace.example.id
#  storage_container_id = "${azurerm_storage_account.example.id}/blobServices/default/containers/${azurerm_storage_container.example.name}"
#  account_key          = azurerm_storage_account.example.primary_access_key
# }

# resource "azurerm_virtual_network" "example" {
#   name                = "mlops-vnet"
#   address_space       = ["10.1.0.0/16"]
#   location            = data.azurerm_resource_group.example.location
#   resource_group_name = data.azurerm_resource_group.example.name
# }

# resource "azurerm_subnet" "example" {
#   name                 = "mlops-subnet"
#   resource_group_name  = data.azurerm_resource_group.example.name
#   virtual_network_name = azurerm_virtual_network.example.name
#   address_prefixes     = ["10.1.0.0/24"]
# }


# resource "azurerm_machine_learning_compute_instance" "example" {
#   name                          = "example"
#   machine_learning_workspace_id = azurerm_machine_learning_workspace.example.id
#   virtual_machine_size          = "STANDARD_DS2_V2"
#   authorization_type            = "personal"
#   # ssh {
#   #   public_key = var.ssh_public_key
#   # }
#   assign_to_user {
#     object_id = var.user_object_id
#     tenant_id = var.tenant_id
# }
#   subnet_resource_id = azurerm_subnet.example.id
#   description        = "The Jupyter Notebook VM for MLOps Capstone project"
#   tags = {
#     mlops = "capstone"
#   }
# }

# module "storage" {
#   source = "./storage"

#   name                     = var.name
#   resource_group_name      = data.azurerm_resource_group.example.name
#   location                 = data.azurerm_resource_group.example.location
#   account_tier             = var.account_tier
#   account_replication_type = var.account_replication_type
#   container_name           = var.container_name
#   container_access_type    = var.container_access_type
# }

# module "network" {
#   source = "./network"

#   virtual_network_name = var.virtual_network_name
#   address_space = var.address_space
#   resource_group_name      = data.azurerm_resource_group.example.name
#   location                 = data.azurerm_resource_group.example.location
#   subnet_name = var.subnet_name
#   address_prefixes = var.address_prefixes
# }

# module "machinelearning"{
#   source = "./machinelearning"
#   application_insights_name =  var.application_insights_name
#   application_type = var.application_type
#   resource_group_name      = data.azurerm_resource_group.example.name
#   location                 = data.azurerm_resource_group.example.location
#   key_vault_name = var.key_vault_name
#   tenant_id_key           = data.azurerm_client_config.current.tenant_id
#   sku_name =  var.sku_name
#   storage_account_id = module.storage.storage_account_id
#   workspace_name = var.workspace_name
#   type = var.type
#   datastore_name = var.datastore_name
#   storage_container_id = "${module.storage.storage_account_id}/blobServices/default/containers/${module.storage.storage_container_name}"
#   account_key          = module.storage.storage_primary_key
#   subnet_resource_id = module.network.subnet_id
#   ml_instance_name = var.ml_instance_name
#   machine_size =  var.machine_size
#   authorization_type = var.authorization_type
#   object_id = var.object_id
#   tenant_id = var.tenant_id
#   description =  var.description
#   tags = var.tags
# }

resource "azurerm_key_vault_access_policy" "example-principal" {
  key_vault_id = "/subscriptions/ce4649d3-242b-451d-bb36-6ff6e58681e2/resourceGroups/mlops/providers/Microsoft.KeyVault/vaults/captonevault"
  object_id = "2e45ddbe-50e2-4849-89c6-152bb08e956f"
  tenant_id = "f6b6dd5b-f02f-441a-99a0-162ac5060bd2"

  key_permissions = [
    "Get", "List"
  ]
  secret_permissions = [
    "Get", "List"
  ]
}
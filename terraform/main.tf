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

module "storage" {
  source = "./storage"

  name                     = var.name
  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = data.azurerm_resource_group.example.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  container_name           = var.container_name
  container_access_type    = var.container_access_type
}

module "network" {
  source = "./network"

  virtual_network_name = var.virtual_network_name 
  address_space = var.address_space
  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = data.azurerm_resource_group.example.location
  subnet_name = var.subnet_name
  address_prefixes = var.address_prefixes
}

module "machinelearning"{
  source = "./machinelearning"
  application_insights_name =  var.application_insights_name
  application_type = var.application_type
  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = data.azurerm_resource_group.example.location
  key_vault_id = module.keyvault.key_id
  storage_account_id = module.storage.storage_account_id
  workspace_name = var.workspace_name
  type = var.type
  datastore_name = var.datastore_name
  storage_container_id = "${module.storage.storage_account_id}/blobServices/default/containers/${module.storage.storage_container_name}"
  account_key          = module.storage.storage_primary_key
  subnet_resource_id = module.network.subnet_id
  ml_instance_name = var.ml_instance_name
  machine_size =  var.machine_size
  authorization_type = var.authorization_type
  object_id = var.object_id  
  tenant_id =  data.azurerm_client_config.current.tenant_id
  description =  var.description
  tags = var.tags
}

module "keyvault" {
  source = "./keyvault"

  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = data.azurerm_resource_group.example.location
  key_vault_name = var.key_vault_name
  secret_name = var.secret_name
  secret_value = module.storage.primary_connection_string
  sku_name = var.sku_name
  object_id_sp = data.azurerm_client_config.current.object_id
  object_id = var.object_id  
  tenant_id =  data.azurerm_client_config.current.tenant_id
}
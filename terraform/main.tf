terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

provider "azurerm" {
  features {}
  resource_provider_registrations = "none"

}

data "azurerm_resource_group" "example" {
  name     = "mlops"
}

resource "azurerm_storage_account" "example" {
  name                     = "Taxi Zone Lookup"
  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "example" {
  name                  = "Taxi Data"
  storage_account_id    = azurerm_storage_account.example.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "example" {
  name                   = "taxi_zone_lookup.csv"
  storage_account_name   = azurerm_storage_account.example.name
  storage_container_name = azurerm_storage_container.example.name
  type                   = "Block"
  source                 = "./taxi_zone_lookup.csv"
}
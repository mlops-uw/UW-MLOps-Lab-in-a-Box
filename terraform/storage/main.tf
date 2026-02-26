resource "azurerm_storage_account" "account" {
  name                     = var.name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
}

resource "azurerm_storage_container" "container" {
  name                  = var.container_name
  storage_account_name    = azurerm_storage_account.account.name
  container_access_type = var.container_access_type
}
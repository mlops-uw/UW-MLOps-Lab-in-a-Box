output storage_account_id {
  value       = azurerm_storage_account.account.id
  description = "The ID of the storage account"
}

output storage_container_name {
  value       = azurerm_storage_container.container.name
  description = "The name of the storage container"
}

output storage_primary_key{
  value = azurerm_storage_account.account.primary_access_key
  description = "The primary access key for the storage account"
}
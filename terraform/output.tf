output "storage_account_id" {
  value       = azurerm_storage_account.example.id
  description = "The ID of the storage account"
}

output "storage_container_id" {
  value       = azurerm_storage_container.example.id
  description = "The ID of the storage container"
}
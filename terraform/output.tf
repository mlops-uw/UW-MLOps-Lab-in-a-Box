output "storage_account_id" {
  value       = module.storage.id
  description = "The ID of the storage account"
}

output storage_container_name {
  value       = module.storage.name
  description = "The name of the storage container"
}

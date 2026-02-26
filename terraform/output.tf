output "storage_account_id" {
  value       = module.storage_account_id.id
  description = "The ID of the storage account"
}

output storage_container_name {
  value       = module.storage_container_name.name
  description = "The name of the storage container"
}

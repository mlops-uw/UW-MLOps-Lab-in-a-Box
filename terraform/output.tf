# output "storage_account_id" {
#   value       = azurerm_storage_account.example.id
#   description = "The ID of the storage account"
# }

# output "storage_container_id" {
#   value       = azurerm_storage_container.example.id
#   description = "The ID of the storage container"
# }

output "ssh_public_key"{
  value       = var.ssh_public_key
  description = "The SSH public key used for VM access"
}
output "key_length" {
  value = local.key_length
}
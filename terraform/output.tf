output storage_account_id {
  value       = module.storage.storage_account_id
  description = "The ID of the storage account"
}

output storage_container_name {
  value       = module.storage.storage_container_name
  description = "The name of the storage container"
}

output storage_primary_key{
  value = module.storage.storage_primary_key
  description = "The primary access key for the storage account"
  sensitive = true
}

output primary_connection_string{
  value = module.storage.primary_connection_string
  description = "The connection string associated with the primary location."
  sensitive = true
}

output subnet_id{
  value       = module.network.subnet_id
  description = "The ID of the subnetwork"
}

output "key_id"{
    value = module.keyvault.key_id
    description = "The Key Vault Secret ID."
}

# output "instance_id"{
#     value = module.machinelearning.instance_id
#     description = "The Machine Learning Compute Instance ID."
# }
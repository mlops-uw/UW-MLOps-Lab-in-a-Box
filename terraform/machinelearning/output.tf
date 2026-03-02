output "key_id"{
    value = azurerm_key_vault.key.id
    description = "The Key Vault Secret ID."
}
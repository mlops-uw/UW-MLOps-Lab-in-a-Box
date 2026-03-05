resource "azurerm_key_vault" "key" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = var.sku_name
}

resource "azurerm_key_vault_access_policy" "pipeline_sp_policy" {
  key_vault_id = azurerm_key_vault.key.id
  tenant_id    = var.tenant_id
  object_id    = var.object_id_sp

  secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore", "Purge"]
}

resource "azurerm_key_vault_access_policy" "user-key-policy" {
  key_vault_id = azurerm_key_vault.key.id
  tenant_id    = var.tenant_id
  object_id    = var.object_id

  key_permissions = [
    "Get", "List", "Create"
  ]
   secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore", "Purge"]
}

resource "azurerm_key_vault_secret" "secret" {
  name         = var.secret_name
  value        = var.secret_value
  key_vault_id = azurerm_key_vault.key.id
  depends_on = [azurerm_key_vault_access_policy.pipeline_sp_policy]

}
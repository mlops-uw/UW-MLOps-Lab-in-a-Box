resource "azurerm_application_insights" "insights" {
  name                = var.application_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = var.application_type
}

resource "azurerm_key_vault" "key" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id_key
  sku_name            = var.sku_name
}

resource "azurerm_machine_learning_workspace" "mlworkspace" {
  name                    = var.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_insights_id = azurerm_application_insights.insights.id
  key_vault_id            = azurerm_key_vault.key.id
  storage_account_id      = var.storage_account_id

  identity {
     type = var.type
   }
}

resource "azurerm_machine_learning_datastore_blobstorage" "blob" {
 name                 = var.datastore_name
 workspace_id         = azurerm_machine_learning_workspace.mlworkspace.id
 storage_container_id = var.storage_container_id
 account_key          = var.account_key
}

resource "azurerm_machine_learning_compute_instance" "example" {
  name                          = var.ml_instance_name
  machine_learning_workspace_id = azurerm_machine_learning_workspace.mlworkspace.id
  virtual_machine_size          = var.machine_size
  authorization_type            = var.authorization_type

  assign_to_user{
    object_id = var.object_id
    tenant_id = var.tenant_id
  }
  subnet_resource_id = var.subnet_resource_id
  description        = var.description
  tags = var.tags
}
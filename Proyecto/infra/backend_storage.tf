provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
}

resource "azurerm_resource_group" "rg_tfstate" {
  name     = "rg-proyecto-negocios-u2-tfstate"
  location = "East US"
}

resource "azurerm_storage_account" "sa_tfstate" {
  name                     = "jkdevelopers"  # NOMBRE NUEVO Y ÚNICO
  resource_group_name      = azurerm_resource_group.rg_tfstate.name
  location                 = azurerm_resource_group.rg_tfstate.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container_tfstate" {
  name                  = "tfstate"
  storage_account_id    = azurerm_storage_account.sa_tfstate.id
  container_access_type = "private"
}

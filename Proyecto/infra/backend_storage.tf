resource "azurerm_resource_group" "tfstate_rg" {
  name     = "rg-terraform"
  location = "East US"
}

resource "azurerm_storage_account" "tfstate_sa" {
  name                     = "tfstatenegociosu2"   
  resource_group_name      = azurerm_resource_group.tfstate_rg.name
  location                 = azurerm_resource_group.tfstate_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "tfstate_container" {
  name                  = "tfstate"
  storage_account_id    = azurerm_storage_account.tfstate_sa.id
  container_access_type = "private"
}

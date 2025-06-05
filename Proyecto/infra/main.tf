terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0.0"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
}

# Grupo de recursos
resource "azurerm_resource_group" "rg-negocios-u2" {
  name     = "rg-negocios-u2"
  location = "East US 2"
}

# Servidor SQL
resource "azurerm_mssql_server" "negocios-u2" {
  name                         = "negocios-u2-sql"
  resource_group_name          = azurerm_resource_group.rg-negocios-u2.name
  location                     = azurerm_resource_group.rg-negocios-u2.location
  version                      = "12.0"
  administrator_login          = var.sqladmin_username
  administrator_login_password = var.sqladmin_password

  identity {
    type = "SystemAssigned"
  }
}

# Base de datos
resource "azurerm_mssql_database" "db_negocios_u2" {
  name                        = "SoftRepoTrack"
  server_id                   = azurerm_mssql_server.negocios-u2.id
  sku_name                    = "GP_S_Gen5_2"
  collation                   = "SQL_Latin1_General_CP1_CI_AS"
  auto_pause_delay_in_minutes = 60
  min_capacity                = 0.5
  storage_account_type        = "Local"
}

# Regla de firewall
resource "azurerm_mssql_firewall_rule" "allow-azure-services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.negocios-u2.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

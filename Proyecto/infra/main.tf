terraform {
  backend "azurerm" {
    resource_group_name   = "rg-proyecto-negocios-u2-tfstate" 
    storage_account_name  = "jkdevelopers"                
    container_name        = "tfstate"
    key                   = "terraform.tfstate"
  }

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

resource "azurerm_resource_group" "rg_proyecto_negocios_u2" {
  name     = "rg-proyecto-negocios-u2"
  location = "East US 2"
}

resource "azurerm_mssql_server" "proyecto_negocios_u2_sql" {
  name                         = "proyecto-negocios-u2-sql"
  resource_group_name          = azurerm_resource_group.rg_proyecto_negocios_u2.name
  location                     = azurerm_resource_group.rg_proyecto_negocios_u2.location
  version                      = "12.0"
  administrator_login          = var.sqladmin_username
  administrator_login_password = var.sqladmin_password

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_mssql_database" "db_proyecto_negocios_u2" {
  name                        = "SoftRepoTrack"
  server_id                   = azurerm_mssql_server.proyecto_negocios_u2_sql.id
  sku_name                    = "GP_S_Gen5_1"
  collation                   = "SQL_Latin1_General_CP1_CI_AS"
  auto_pause_delay_in_minutes = 30
  min_capacity                = 0.5
  storage_account_type        = "Local"
}

resource "azurerm_mssql_firewall_rule" "allow_azure_services_proyecto" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.proyecto_negocios_u2_sql.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

resource "azurerm_storage_account" "proyecto_negocios_u2_storage" {
  name                     = "proyectonegociosu2sa"  # Válido
  resource_group_name      = azurerm_resource_group.rg_proyecto_negocios_u2.name
  location                 = azurerm_resource_group.rg_proyecto_negocios_u2.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = {
    environment = "academic"
    project     = "SoftRepoTrack"
  }
}

resource "azurerm_storage_container" "proyecto_datafiles" {
  name                  = "datafiles"
  storage_account_name  = azurerm_storage_account.proyecto_negocios_u2_storage.name
  container_access_type = "private"
}

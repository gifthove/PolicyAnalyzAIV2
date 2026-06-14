terraform {
  # backend "local" {}
  backend "azurerm" {
  }
}

terraform {

  required_version = ">=1.6"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

data "azurerm_client_config" "current" {}

module "resourcegroup" {
  source   = "./modules/resourcegroup"
  name     = local.resource_group_name
  location = local.location
}

module "appinsights" {
  source              = "./modules/appinsights"
  name                = local.appinsights_name
  log_analytics_name  = local.log_analytics_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
}

module "openai" {
  source              = "./modules/openai"
  name                = local.openai_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
}

module "aisearch" {
  source              = "./modules/aisearch"
  name                = local.search_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
}

module "storage" {
  source              = "./modules/storage"
  name                = local.storage_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
}

module "acr" {
  source              = "./modules/acr"
  name                = local.acr_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
}

module "containerappenv" {
  source                     = "./modules/containerappenv"
  env_name                   = local.container_app_env_name
  location                   = local.location
  resource_group_name        = module.resourcegroup.resource_group_name
  log_analytics_workspace_id = module.appinsights.workspace_id
}

module "containerapp" {
  source                        = "./modules/containerapp"
  container_app_environment_id  = module.containerappenv.id
  app_name                      = local.app_name
  resource_group_name           = module.resourcegroup.resource_group_name
  acr_login_server              = module.acr.login_server
  acr_username                  = module.acr.admin_username
  acr_password                  = module.acr.admin_password
  openai_key                    = module.openai.primary_key
  search_key                    = module.aisearch.primary_key
  blob_connection_string        = module.storage.primary_connection_string
  appinsights_connection_string = module.appinsights.connection_string
  env_vars = {
    "AZURE_OPENAI_ENDPOINT"             = module.openai.endpoint
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" = "text-embedding-ada-002"
    "AZURE_OPENAI_CHAT_DEPLOYMENT"      = "gpt-4.1"
    "AZURE_OPENAI_API_VERSION"          = "2024-02-01"
    "AZURE_OPENAI_EMBEDDING_DIMENSIONS" = "1536"
    "AZURE_SEARCH_ENDPOINT"             = module.aisearch.endpoint
    "AZURE_SEARCH_INDEX_NAME"           = "policy-documents"
    "AZURE_BLOB_CONTAINER"              = "documents"
    "AZURE_STORAGE_ACCOUNT_NAME"        = module.storage.account_name
    "KEY_VAULT_URI"                     = module.keyvault.key_vault_uri
    "ENVIRONMENT"                       = var.environment
    "CORS_ALLOWED_ORIGINS"              = "https://${module.containerapp_ui.fqdn}"
  }
}

module "containerapp_ui" {
  source                       = "./modules/containerapp-ui"
  container_app_environment_id = module.containerappenv.id
  app_name                     = local.ui_app_name
  resource_group_name          = module.resourcegroup.resource_group_name
  acr_login_server             = module.acr.login_server
  acr_username                 = module.acr.admin_username
  acr_password                 = module.acr.admin_password
}

module "keyvault" {
  source              = "./modules/keyvault"
  name                = local.key_vault_name
  location            = local.location
  resource_group_name = module.resourcegroup.resource_group_name
  secrets = {
    "resource--group--name"           = module.resourcegroup.resource_group_name
    "openai--endpoint"                = module.openai.endpoint
    "openai--api--key"                = module.openai.primary_key
    "search--endpoint"                = module.aisearch.endpoint
    "search--api--key"                = module.aisearch.primary_key
    "storage--connection--string"     = module.storage.primary_connection_string
    "appinsights--connection--string" = module.appinsights.connection_string
    "acr--login--server"              = module.acr.login_server
  }
}

# Container app managed identity — read secrets at runtime
resource "azurerm_key_vault_access_policy" "webapp" {
  key_vault_id = module.keyvault.key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.containerapp.principal_id

  secret_permissions = ["Get", "List"]
}

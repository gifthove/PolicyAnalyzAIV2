resource "azurerm_container_app_environment" "env" {
  name                       = var.env_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id
}

resource "azurerm_container_app" "app" {
  name                         = var.app_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  registry {
    server               = var.acr_login_server
    username             = var.acr_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = var.acr_password
  }

  secret {
    name  = "openai-key"
    value = var.openai_key
  }

  secret {
    name  = "search-key"
    value = var.search_key
  }

  secret {
    name  = "blob-connection-string"
    value = var.blob_connection_string
  }

  secret {
    name  = "appinsights-connection-string"
    value = var.appinsights_connection_string
  }

  template {
    min_replicas = 0
    max_replicas = 10

    container {
      name   = "api"
      image  = "${var.acr_login_server}/${var.docker_image_name}"
      cpu    = 0.5
      memory = "1Gi"

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      env {
        name        = "AZURE_OPENAI_KEY"
        secret_name = "openai-key"
      }

      env {
        name        = "AZURE_SEARCH_KEY"
        secret_name = "search-key"
      }

      env {
        name        = "AZURE_BLOB_CONNECTION_STRING"
        secret_name = "blob-connection-string"
      }

      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "appinsights-connection-string"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

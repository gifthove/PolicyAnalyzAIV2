output "id" {
  value       = azurerm_container_app_environment.env.id
  description = "Container App Environment ID, shared by the API and UI Container Apps"
}

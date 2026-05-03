output "fqdn" {
  value       = azurerm_container_app.app.ingress[0].fqdn
  description = "Fully qualified domain name of the Container App ingress"
}

output "app_name" {
  value = azurerm_container_app.app.name
}

output "principal_id" {
  value       = azurerm_container_app.app.identity[0].principal_id
  description = "System-assigned managed identity principal ID"
}

output "fqdn" {
  value       = azurerm_container_app.ui.ingress[0].fqdn
  description = "Fully qualified domain name of the Container App ingress"
}

output "app_name" {
  value = azurerm_container_app.ui.name
}

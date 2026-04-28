resource "azurerm_search_service" "search" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "basic"
}

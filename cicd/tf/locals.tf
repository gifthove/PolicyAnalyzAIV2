locals {
  name                   = "infra"
  service_prefix         = "polanalyai-${local.name}"
  resource_group_name    = "${local.service_prefix}-${var.environment}-rg"
  key_vault_name         = "${local.service_prefix}-${var.environment}-kv" # max 24 chars: polanalyai-infra-dev-kv = 22 ✓
  location               = "australiaeast"
  environment            = var.environment
  openai_name            = "${local.service_prefix}-${var.environment}-oai"
  search_name            = "${local.service_prefix}-${var.environment}-search"
  storage_name           = "polanalyai${var.environment}sa"  # alphanumeric only, max 24 chars
  acr_name               = "polanalyai${var.environment}acr" # alphanumeric only
  container_app_env_name = "${local.service_prefix}-${var.environment}-cae"
  app_name               = "${local.service_prefix}-${var.environment}-api"
  ui_app_name            = "${local.service_prefix}-${var.environment}-ui"
  appinsights_name       = "${local.service_prefix}-${var.environment}-ai"
  log_analytics_name     = "${local.service_prefix}-${var.environment}-la"
  common_tags = {
    Environment = var.environment
    Application = "policyanalyzai-${var.environment}"
  }
}

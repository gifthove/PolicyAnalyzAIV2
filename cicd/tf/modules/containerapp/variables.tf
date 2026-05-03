variable "env_name" {
  type        = string
  description = "Container App Environment name"
}

variable "app_name" {
  type        = string
  description = "Container App name"
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Log Analytics workspace ID for Container App Environment diagnostics"
}

variable "acr_login_server" {
  type        = string
  description = "ACR login server (e.g. myacr.azurecr.io)"
}

variable "acr_username" {
  type      = string
  sensitive = true
}

variable "acr_password" {
  type      = string
  sensitive = true
}

variable "docker_image_name" {
  type        = string
  description = "Image name and tag without registry prefix (e.g. policyanalyzai/api:latest)"
}

variable "openai_key" {
  type      = string
  sensitive = true
}

variable "search_key" {
  type      = string
  sensitive = true
}

variable "blob_connection_string" {
  type      = string
  sensitive = true
}

variable "appinsights_connection_string" {
  type      = string
  sensitive = true
}

variable "env_vars" {
  type        = map(string)
  description = "Non-sensitive environment variables injected into the container"
  default     = {}
}

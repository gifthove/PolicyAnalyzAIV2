variable "plan_name" {
  type        = string
  description = "App Service Plan name"
}

variable "app_name" {
  type        = string
  description = "Web App name"
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "docker_image" {
  type        = string
  description = "Full Docker image reference including registry (e.g. myacr.azurecr.io/api:latest)"
}

variable "acr_login_server" {
  type        = string
  description = "ACR login server URL"
}

variable "acr_username" {
  type        = string
  sensitive   = true
  description = "ACR admin username"
}

variable "acr_password" {
  type        = string
  sensitive   = true
  description = "ACR admin password"
}

variable "app_settings" {
  type        = map(string)
  description = "Application settings injected as environment variables"
  default     = {}
}

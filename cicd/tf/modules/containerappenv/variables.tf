variable "env_name" {
  type        = string
  description = "Container App Environment name"
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

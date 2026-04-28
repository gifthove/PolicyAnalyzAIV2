variable "name" {
  type        = string
  description = "Application Insights instance name"
}

variable "log_analytics_name" {
  type        = string
  description = "Log Analytics workspace name"
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

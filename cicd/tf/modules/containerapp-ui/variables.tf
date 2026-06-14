variable "app_name" {
  type        = string
  description = "Container App name"
}

variable "resource_group_name" {
  type = string
}

variable "container_app_environment_id" {
  type        = string
  description = "ID of the shared Container App Environment"
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
  description = "Image name and tag without registry prefix (e.g. policyanalyzai/ui:latest). Empty string uses a public placeholder — CI/CD pipeline owns the live image update."
  default     = ""
}

variable "env_vars" {
  type        = map(string)
  description = "Non-sensitive environment variables injected into the container"
  default     = {}
}

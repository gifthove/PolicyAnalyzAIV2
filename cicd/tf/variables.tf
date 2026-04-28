variable "environment" {
  type        = string
  description = "The environment short name (dev or prod)"
}

variable "docker_image_name" {
  type        = string
  description = "The Docker image name to deploy to the web app (without registry prefix)"
  default     = "policyanalyzai/api:latest"
}

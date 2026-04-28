variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "secrets" {
  type        = map(string)
  description = "The secret values to create"
}

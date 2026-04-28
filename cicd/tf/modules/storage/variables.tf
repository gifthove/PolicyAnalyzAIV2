variable "name" {
  type        = string
  description = "Storage account name (alphanumeric only, max 24 chars)"
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

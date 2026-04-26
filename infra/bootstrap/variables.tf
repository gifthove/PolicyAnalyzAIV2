variable "resource_group_name" {
  default = "rg-policyanalyzai-tfstate"
}

variable "storage_account_name" {
  description = "Must be globally unique, 3-24 lowercase alphanumeric chars"
  type        = string
}

variable "location" {
  default = "australiaeast"
}

variable "trust_relationship" {
  type = string
  default = ""
}
variable "role_name" {
  type = string
  default = ""
}
variable "policy_arns" {
  type = list(string)
  default = []
}
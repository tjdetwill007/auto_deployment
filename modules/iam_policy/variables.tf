variable "policy_name" {
  type = string
  default = ""
}

variable "action" {
  type = list(string)
  default = [ "lambda:InvokeFunction" ]
}

variable "resources" {
  type = string
  default = "*"
}
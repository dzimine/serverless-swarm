# Declaraions for terraform.tfvars
variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "key_name" {}
variable "key_path" {}
variable "aws_region" {}

# Variables
variable ami {
  default = "ami-a58d0dc5"
}
variable instance_type_manager {
  default = "t2.micro"
  # Recommened: t2.medium for testing, m4.large for production
  # default = "t2.medium"
}
variable instance_type_worker {
  default = "t2.micro"
  # Recommened: t2.medium for testing, c4.xlarge for production
  # default = "t2.medium"
}
variable n_workers {
  default = 1
}
variable "gs_efs_share" {
  default = "fs-5b418ff2.efs.us-west-2.amazonaws.com"
  description = "AWS EFS storage ID for RW `share`"
}
variable "gs_ebs_snapshot" {
  default = "snap-02b46f961d1d16e0e"
  description = "Data EBS Volume for RO `data`"
}
# AWS Reads
variable "aws_availability_zone" {
  default = "us-west-2a"
}
variable subnet {
  default = "subnet-f2e732bb"
}
variable "security_group_vpc" {
  default = "sg-c09cebb8"
}
variable "security_group_ssh" {
  default = "sg-4f83f437"
}
variable "security_group_st2" {
  default = "sg-cfdfa8b7"
}

# Declaraions for terraform.tfvars
variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "key_name" {}
variable "key_path" {}
variable "aws_region" {}

# Variables
variable zone_id {
  default = "ZV08YC45J234P"
  description = "Route53 Hosted Zone ID for public DNS"
}
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
  description = "AWS EFS storage ID for read-write `share`"
}
variable "gs_ebs_snapshot" {
  default = "snap-02b46f961d1d16e0e"
  description = "Data EBS Volume for read-only `data`"
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
  description = "Security group for master-worker communications"
}
variable "security_group_ssh" {
  default = "sg-4f83f437"
  description = "Security group to access the boxes via SSH remotely"
}
variable "security_group_st2" {
  default = "sg-cfdfa8b7"
  description = "Security group to for st2 node: HTTP, HTTPS, 8080"
}
variable "asg_min" {
  default = 0
  description = "Auto-scaling group MIN"
}
variable "asg_max" {
  default = 10
  description = "Auto-scaling group MIN"
}
variable "asg_desired" {
  default = 1
  description = "Auto-scaling group desired"
}

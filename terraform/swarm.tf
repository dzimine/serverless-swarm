provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region = "${var.aws_region}"
}

data "template_file" "userdata_worker" {
  template = "${file("worker_cloudinit.tpl")}"
  vars {
    efs = "${var.gs_efs_share}"
  }
}

data "template_cloudinit_config" "config" {
  gzip = false
  base64_encode = false
  part {
    content_type = "text/cloud-config"
    content = "${data.template_file.userdata_worker.rendered}"
  }
}

resource "aws_instance" "worker" {
  count = "${var.n_workers}"
  ami = "${var.ami}"
  instance_type = "${var.instance_type_worker}"
  key_name = "${var.key_name}"
  subnet_id = "${var.subnet}"
  vpc_security_group_ids = [
    "${var.security_group_vpc}",
    "${var.security_group_ssh}"
  ]
  ebs_block_device = {
    device_name = "/dev/sdb"
    snapshot_id = "${var.gs_ebs_snapshot}"
    delete_on_termination = true
  }
  tags {
    Name = "worker"
  }
  user_data = "${data.template_cloudinit_config.config.rendered}"
}

resource "aws_route53_record" "node" {
  count = "${var.n_workers}"
  zone_id = "ZV08YC45J234P"
  name = "node${var.n_workers}"
  type = "CNAME"
  ttl = 60
  records = ["${element(aws_instance.worker.*.public_dns, count.index)}"]
}

resource "aws_instance" "manager" {
  ami = "${var.ami}"
  instance_type = "${var.instance_type_manager}"
  key_name = "${var.key_name}"
  subnet_id = "${var.subnet}"
  vpc_security_group_ids = [
    "${var.security_group_vpc}",
    "${var.security_group_ssh}",
    "${var.security_group_st2}"
  ]
  ebs_block_device = {
    device_name = "/dev/sdb"
    snapshot_id = "${var.gs_ebs_snapshot}"
    delete_on_termination = true
  }
  tags {
    Name = "manager"
  }
  user_data = "${data.template_cloudinit_config.config.rendered}"
}

resource "aws_route53_record" "st2" {
  zone_id = "ZV08YC45J234P"
  name = "st2"
  type = "CNAME"
  ttl = 60
  records = ["${aws_instance.manager.public_dns}"]
}

output "worker_public_ip" {
  value = "${join(",",aws_instance.worker.*.public_ip)}"
}
output "manager_public_ip" {
  value = "${aws_instance.manager.public_ip}"
}
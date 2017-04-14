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
  provisioner "remote-exec" {
    inline = ["# Connected!"]
  }
  tags {
    Name = "worker"
  }
  user_data = "${data.template_cloudinit_config.config.rendered}"
}

resource "aws_route53_record" "node" {
  count = "${var.n_workers}"
  zone_id = "ZV08YC45J234P"
  name = "node${count.index + 1}"
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
  provisioner "remote-exec" {
    inline = ["# Connected!"]
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

# Make sure DNS records seen on localhost (once in a blue moon they aren't due to DNS cache, etc.)
resource "null_resource" "wait_for_dns_workers" {
  count = "${var.n_workers}"
  provisioner "local-exec" {
    command = "until [[  $(dig NS +short ${element(aws_route53_record.node.*.fqdn, count.index)}) ]]; do echo 'waiting'; sleep 10; done"
  }
}

resource "null_resource" "wait_for_dns_manager" {
  provisioner "local-exec" {
    command = "until [[  $(dig NS +short ${aws_route53_record.st2.fqdn}) ]]; do echo 'waiting';  sleep 10;  done"
  }
}

# Generate Ansible inventory
data "template_file" "ansible_node" {
  count = "${var.n_workers}"
  template = "${file("hostname.tpl")}"
  vars {
    index = "${count.index + 1}"
    name  = "node"
    extra = " ansible_host=${element(aws_route53_record.node.*.fqdn, count.index)}"
  }
}

data "template_file" "inventory" {
  template = "${file("inventory.tpl")}"
  vars {
    manager ="st2 ansible_host=${aws_route53_record.st2.fqdn}"
    node_count = "${length(data.template_file.ansible_node.*.rendered)}"
    nodes = "${join("\n",data.template_file.ansible_node.*.rendered)}"
  }
}

resource "null_resource" "local" {
  triggers {
    template = "${data.template_file.inventory.rendered}"
  }

  provisioner "local-exec" {
    command = "echo \"${data.template_file.inventory.rendered}\" > ./inventory.aws"
  }
}

resource "null_resource" "ansible-provision" {
  depends_on = ["null_resource.wait_for_dns_workers", "null_resource.wait_for_dns_manager"]
  provisioner "local-exec" {
    # TODO: make runnable from any dir.
    # command =  "cd .. ; ansible-playbook playbook-swarm.yml -vv -i terraform/inventory.aws"
    command =  "cd .. ; ansible-playbook playbook-all.yml -vv -i terraform/inventory.aws"
  }
}

output "worker_public_ip" {
  value = "${join(",",aws_instance.worker.*.public_ip)}"
}
output "manager_public_ip" {
  value = "${aws_instance.manager.public_ip}"
}
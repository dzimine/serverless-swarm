resource "aws_ami_from_instance" "worker" {
  name               = "swarm-worker-tf"
  depends_on         = ["null_resource.ansible-provision"]
  source_instance_id = "${aws_instance.worker.0.id}"
}

resource "aws_launch_configuration" "workers" {
  name_prefix = "swarm-workers-"
  # How to automatically look up the id from output of other tasks?
  image_id = "${aws_ami_from_instance.worker.id}"
  instance_type = "${var.instance_type_worker}"

  security_groups = [
    "${var.security_group_vpc}",
    "${var.security_group_ssh}"
  ]

  ebs_block_device = {
    device_name = "/dev/sdb"
    snapshot_id = "${var.gs_ebs_snapshot}"
    delete_on_termination = true
  }

  user_data = "${data.template_cloudinit_config.config.rendered}"
  key_name = "${var.key_name}"
}

resource "aws_autoscaling_group" "swarm-workers" {
  name                 = "swarm-workers-tf"
  max_size             = "${var.asg_max}"
  min_size             = "${var.asg_min}"
  desired_capacity     = "${var.asg_desired}"
  force_delete         = true
  launch_configuration = "${aws_launch_configuration.workers.name}"

  # availability_zones   = ["${var.aws_availability_zone}"]
  vpc_zone_identifier = ["${var.subnet}"]

  lifecycle {
    create_before_destroy = true
  }

  tag {
    key                 = "Name"
    value               = "asg_worker"
    propagate_at_launch = "true"
  }
}
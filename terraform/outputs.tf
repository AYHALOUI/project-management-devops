output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value = aws_instance.app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value = aws_instance.app.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value = "ssh -i ~/ .ssh/${var.key_name}.pem ec2-user@{aws_instance.app.public_ip}"
}
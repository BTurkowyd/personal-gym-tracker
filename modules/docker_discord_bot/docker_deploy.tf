resource "null_resource" "docker_deploy" {
  triggers = {
    files = filebase64sha256("${path.module}/Dockerfile")
  }

  provisioner "local-exec" {
    command = <<EOT
      pwd
      aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ${var.account_id}.dkr.ecr.eu-central-1.amazonaws.com
      docker build --platform linux/x86_64 -t discord-bot-lambda ${path.cwd}/${path.module}
      docker tag discord-bot-lambda:latest ${var.account_id}.dkr.ecr.eu-central-1.amazonaws.com/discord-bot-lambda:latest
      docker push 926728314305.dkr.ecr.eu-central-1.amazonaws.com/discord-bot-lambda:latest
    EOT
  }
}
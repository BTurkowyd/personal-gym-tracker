resource "null_resource" "docker_deploy" {
  triggers = {
    files = filebase64sha256("${path.module}/Dockerfile")
  }

  provisioner "local-exec" {
    command = <<EOT
      pwd
      aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 926728314305.dkr.ecr.eu-central-1.amazonaws.com
      docker build -t discord-bot-lambda /Users/bartoszturkowyd/Projects/aws/silka/modules/docker_discord_bot/
      docker tag discord-bot-lambda:latest 926728314305.dkr.ecr.eu-central-1.amazonaws.com/discord-bot-lambda:latest
      docker push 926728314305.dkr.ecr.eu-central-1.amazonaws.com/discord-bot-lambda:latest
    EOT
  }
}
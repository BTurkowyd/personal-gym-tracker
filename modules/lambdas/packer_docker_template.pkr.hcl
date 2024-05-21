packer {
  required_plugins {
    docker = {
      source  = "github.com/hashicorp/docker"
      version = "~> 1"
    }
  }
}

source "docker" "image" {
  image = "public.ecr.aws/lambda/python:3.11"
  commit = true
  platform = "linux/x86_64"
  changes = [
    "CMD [\"${var.lambda_name}.lambda_handler\"]"
  ]
}

build {
  name = var.lambda_name
  sources = ["source.docker.image"]

  provisioner "file" {
    source      = "./${var.lambda_name}/${var.lambda_name}.py"
    destination = "/var/task/${var.lambda_name}.py"
  }

  provisioner "file" {
    source      = "./${var.lambda_name}/requirements.txt"
    destination = "/requirements.txt"
  }

  provisioner "shell" {
    inline = [
      "pip install -r /requirements.txt --target $LAMBDA_TASK_ROOT",
    ]
  }

  post-processors {
    post-processor "docker-tag" {
	repository = "926728314305.dkr.ecr.eu-central-1.amazonaws.com/${var.ecr_repo_name}"
	tags = ["latest"]
    }

    post-processor "docker-push" {
    ecr_login = true
    keep_input_artifact = true
    aws_profile         = "cdk-dev"
    login_server = "926728314305.dkr.ecr.eu-central-1.amazonaws.com"
    }
  }
}

variable "lambda_name" {
  type = string
}

variable "ecr_repo_name" {
  type = string
}
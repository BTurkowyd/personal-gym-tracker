// Packer configuration for building Lambda Docker images.

packer {
  required_plugins {
    docker = {
      source  = "github.com/hashicorp/docker"
      version = "~> 1"
    }
  }
}

// Use the public AWS Lambda Python 3.11 base image.
source "docker" "image" {
  image    = "public.ecr.aws/lambda/python:3.11"
  commit   = true
  platform = "linux/x86_64"
  changes = [
    "CMD [\"${var.lambda_name}.lambda_handler\"]"
  ]
}

// Build block for provisioning and pushing the Docker image.
build {
  name    = var.lambda_name
  sources = ["source.docker.image"]

  // Copy the Lambda handler Python file into the image.
  provisioner "file" {
    source      = "./${var.lambda_name}/"
    destination = "/var/task/"
  }

  // Install Python dependencies into the Lambda task root.
  provisioner "shell" {
    inline = [
      "if [ -f /var/task/requirements.txt ]; then pip install --only-binary=:all: --target $LAMBDA_TASK_ROOT -r /var/task/requirements.txt; fi"
    ]
  }

  // Tag and push the built image to ECR.
  post-processors {
    post-processor "docker-tag" {
      repository = "926728314305.dkr.ecr.eu-central-1.amazonaws.com/${var.ecr_repo_name}"
      tags       = ["latest"]
    }

    post-processor "docker-push" {
      ecr_login            = true
      keep_input_artifact  = true
      aws_profile          = "cdk-dev"
      login_server         = "926728314305.dkr.ecr.eu-central-1.amazonaws.com"
    }
  }
}

// Name of the Lambda function to build.
variable "lambda_name" {
  type = string
}

// Name of the ECR repository to push the image to.
variable "ecr_repo_name" {
  type = string
}
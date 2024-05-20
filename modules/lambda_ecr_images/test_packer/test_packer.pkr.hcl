packer {
  required_plugins {
    docker = {
      source  = "github.com/hashicorp/docker"
      version = "~> 1"
    }
  }
}

source "docker" "test_packer" {
  image = "public.ecr.aws/lambda/python:3.11"
  commit = true
  platform = "linux/x86_64"
  changes = [
    "CMD [\"test_packer.lambda_handler\"]"
  ]
}

build {
  name = "test_packer"
  sources = ["source.docker.test_packer"]

  provisioner "file" {
    source      = "./src/test_packer.py"
    destination = "/var/task/test_packer.py"
  }

  provisioner "file" {
    source      = "./src/requirements.txt"
    destination = "/requirements.txt"
  }

  provisioner "shell" {
    inline = [
      "pip install -r /requirements.txt --target $LAMBDA_TASK_ROOT",
    ]
  }

  post-processors {
    post-processor "docker-tag" {
	repository = "926728314305.dkr.ecr.eu-central-1.amazonaws.com/test-packer"
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
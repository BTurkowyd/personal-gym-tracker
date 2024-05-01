terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-states-6mabw3s4smjiozsqyi76rq"
    key    = "projects/silka"
    region = "eu-central-1"
  }
}

provider "aws" {
  region = "eu-central-1"
}
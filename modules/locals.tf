locals {
  envs = { for tuple in regexall("(.*?)=(.*)", file(".env")) : tuple[0] => tuple[1] }
}

data "external" "get_git_branch" {
  program = ["bash", "${path.module}/src/get-branch.sh"]
}

output "branch_name" {
  value = sha1(data.external.get_git_branch.result["branch"])
}

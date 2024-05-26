include "root" {
  path = find_in_parent_folders()
  expose = true
}

terraform {
  source = "${get_repo_root()}/modules"
}

inputs =  {
  stage = "${basename(get_terragrunt_dir())}"
  env_file = "${get_repo_root()}/modules/.env"
}
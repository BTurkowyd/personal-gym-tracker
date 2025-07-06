// Include the root terragrunt configuration from the nearest parent folder.
// The 'expose = true' option makes the root configuration's outputs available to this module.
include "root" {
  path = find_in_parent_folders("root.hcl")
  expose = true
}

// Specify the Terraform source directory for this environment.
// This points to the 'modules' directory at the repository root.
terraform {
  source = "${get_repo_root()}/modules"
}

// Define input variables for the Terraform module.
// - 'stage' is set to the name of the current directory (e.g., 'dev').
// - 'env_file' points to a shared .env file in the modules directory.
inputs =  {
  stage = "${basename(get_terragrunt_dir())}"
  env_file = "${get_repo_root()}/modules/.env"
}
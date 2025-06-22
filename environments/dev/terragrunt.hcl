// Include the root terragrunt configuration from the nearest parent folder.
// The 'expose = true' option makes the root configuration's outputs available to this module.
include "root" {
  path = find_in_parent_folders()
  expose = true
}

// Specify the Terraform source directory for this environment.
// This points to the 'modules' directory at the repository root.
terraform {
  source = "${get_repo_root()}/modules"
}

// Define
# Load environment variables from the specified env file into a map.
locals {
  envs = { for tuple in regexall("(.*?)=(.*)", file(var.env_file)) : tuple[0] => tuple[1] }
}
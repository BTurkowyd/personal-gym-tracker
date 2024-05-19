resource "aws_lambda_layer_version" "python_requests" {
  layer_name = "python_requests"
  filename = "${path.module}/src/layers/requests_layer.zip"
  compatible_runtimes = ["python3.11"]
}

data "archive_file" "requests_layer" {
  type        = "zip"
  source_dir = "${path.module}/src/layers/requests_layer"
  output_path = "${path.module}/src/layers/requests_layer.zip"
}

resource "aws_lambda_layer_version" "pynacl" {
  layer_name = "pynacl"
  filename = "${path.module}/src/layers/pynacl_layer.zip"
  compatible_runtimes = ["python3.11"]
}

data "archive_file" "pynacl" {
  type        = "zip"
  source_dir = "${path.module}/src/layers/pynacl_layer"
  output_path = "${path.module}/src/layers/pynacl_layer.zip"
}

resource "aws_lambda_layer_version" "pyotp" {
  layer_name = "pyotp"
  filename = "${path.module}/src/layers/pyotp_layer.zip"
  compatible_runtimes = ["python3.11"]
}

data "archive_file" "pyotp" {
  type        = "zip"
  source_dir = "${path.module}/src/layers/pyotp_layer"
  output_path = "${path.module}/src/layers/pyotp_layer.zip"
}
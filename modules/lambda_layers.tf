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
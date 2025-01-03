resource "aws_iam_role" "lambda_role" {
  name = "DiscordBotRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy" "s3_access" {
  name = "DiscordBotS3Access"
  role   = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "s3:PutObject",
        "s3:GetObject"
      ]
      Resource = [
        aws_s3_bucket.upload_bucket.arn,
        "${aws_s3_bucket.upload_bucket.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy" "dynamodb_access" {
  name = "DiscordBotDynamoDBAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "dynamodb:DeleteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ]
      Resource = [
        aws_dynamodb_table.workouts_table.arn,
        "${aws_dynamodb_table.workouts_table.arn}/index/*"
      ]
    }]
  })
  role   = aws_iam_role.lambda_role.id
}

resource "aws_iam_role_policy" "ssm_parameter_access" {
  name = "DiscordBotSSMAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "ssm:GetParameter",
        "ssm:PutParameter",
      ]
      Resource = "*"
    }]
  })
  role   = aws_iam_role.lambda_role.id
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  role       = aws_iam_role.lambda_role.id
}
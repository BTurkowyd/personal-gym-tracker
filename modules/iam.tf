# IAM role for Lambda functions (Discord bot, Hevy API, etc.).
resource "aws_iam_role" "lambda_role" {
  name = "DiscordBotRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Trust policy to allow Lambda service to assume the role.
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

# Policy for Lambda to access S3 bucket for uploads.
resource "aws_iam_role_policy" "s3_access" {
  name = "DiscordBotS3Access"
  role   = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
      ]
      Resource = [
        aws_s3_bucket.upload_bucket.arn,
        "${aws_s3_bucket.upload_bucket.arn}/*",
        aws_s3_bucket.lancedb_bucket.arn,
        "${aws_s3_bucket.lancedb_bucket.arn}/*"
      ]
    }]
  })
}

# Policy for Lambda to access DynamoDB table for workouts.
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

# Policy for Lambda to access SSM Parameter Store for workout index.
resource "aws_iam_role_policy" "ssm_parameter_access" {
  name = "DiscordBotSSMAccess"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ssm:PutParameter"
        ]
        Resource = [
          "arn:aws:ssm:eu-central-1:${data.aws_caller_identity.current.account_id}:parameter/discord/*",
          "arn:aws:ssm:eu-central-1:${data.aws_caller_identity.current.account_id}:parameter/hevy/*",
          "arn:aws:ssm:eu-central-1:${data.aws_caller_identity.current.account_id}:parameter/silka/*"
        ]
      }
    ]
  })
}

# Attach AWS managed policy for Lambda VPC access.
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  role       = aws_iam_role.lambda_role.id
}

# Policy for Lambda to access AWS Glue GetTable (needed for get_table_schema Lambda)
resource "aws_iam_role_policy" "glue_get_table_access" {
  name = "DiscordBotGlueGetTableAccess"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTableVersion",
          "glue:GetTableVersions"
        ]
        Resource = [
          "arn:aws:glue:eu-central-1:${data.aws_caller_identity.current.account_id}:catalog",
          "arn:aws:glue:eu-central-1:${data.aws_caller_identity.current.account_id}:database/*",
          "arn:aws:glue:eu-central-1:${data.aws_caller_identity.current.account_id}:table/*/*"
        ]
      }
    ]
  })
}

# Policy for Lambda to execute Athena queries and get results
resource "aws_iam_role_policy" "athena_access" {
  name = "DiscordBotAthenaAccess"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup",
          "athena:GetDatabase",
          "athena:GetTableMetadata",
          "athena:ListWorkGroups",
          "athena:ListDatabases",
          "athena:ListTableMetadata",
          "athena:GetDataCatalog",
          "athena:ListDataCatalogs"
        ],
        Resource = [
          "arn:aws:athena:eu-central-1:${data.aws_caller_identity.current.account_id}:workgroup/*",
          "arn:aws:athena:eu-central-1:${data.aws_caller_identity.current.account_id}:datacatalog/*",
          "arn:aws:athena:eu-central-1:${data.aws_caller_identity.current.account_id}:database/*",
          "arn:aws:athena:eu-central-1:${data.aws_caller_identity.current.account_id}:table/*/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:AbortMultipartUpload",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ],
        Resource = [
          module.athena.athena_bucket_arn,
          "${module.athena.athena_bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "invoke_bedrock_models" {
  name = "DiscordBotInvokeBedrockModels"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "bedrock:InvokeModel",
          "bedrock:ListModels",
          "bedrock:GetModel",
          "bedrock:ListModelVersions"
        ],
        Resource = "*"
      }
    ]
  })
  
}
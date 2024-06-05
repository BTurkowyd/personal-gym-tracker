resource "aws_iam_user" "superset_user" {
  name = "superset-user"
  path = "/"
}

# Define the custom policy for Athena, S3, and Glue
resource "aws_iam_policy" "superset_policy" {
  name        = "SupersetPolicy"
  description = "Custom policy for Athena, S3, and Glue access"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "athena:StartQueryExecution",
          "athena:StopQueryExecution",
          "athena:GetQueryResults",
          "athena:GetQueryExecution",
          "athena:BatchGetQueryExecution"
        ],
        Resource = ["*"]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          var.data_bucket_arn,
          "${var.data_bucket_arn}/*",
          var.athena_bucket_arn,
          "${var.athena_bucket_arn}/*",
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:*"
        ],
        Resource = [
          var.athena_bucket_arn,
          "${var.athena_bucket_arn}/*",
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions"
        ],
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "superset_policy_attachment" {
  policy_arn = aws_iam_policy.superset_policy.arn
  user       = aws_iam_user.superset_user.name
}

resource "aws_iam_access_key" "superset_user_key" {
  user = aws_iam_user.superset_user.name
}

output "aws_access_key_id" {
  value = aws_iam_access_key.superset_user_key.id
  sensitive = true
}

output "aws_secret_access_key" {
  value = aws_iam_access_key.superset_user_key.secret
  sensitive = true
}
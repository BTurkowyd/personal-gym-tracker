# Silka AWS Infrastructure

This repository contains the complete infrastructure-as-code and supporting scripts for the **Silka Workouts** platform, including:
- Discord bot integration
- Data ingestion from the Hevy API
- Data lake and analytics stack (Athena, Glue, S3, Superset)
- AI agent using AWS Bedrock and Claude 3 Haiku to query data by providing natural language prompts
- Automated deployment using Terraform, Terragrunt, Docker, and Packer

---

## Table of Contents

- [Silka AWS Infrastructure](#silka-aws-infrastructure)
  - [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [Repository Structure](#repository-structure)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Deployment](#deployment)
    - [1. Build and Push Lambda Docker Images](#1-build-and-push-lambda-docker-images)
    - [2. dbt Data Transformation](#2-dbt-data-transformation)
    - [3. Terragrunt Environments](#3-terragrunt-environments)
  - [Local Development (Superset)](#local-development-superset)
  - [Modules Overview](#modules-overview)
  - [Security Notes](#security-notes)
  - [Troubleshooting](#troubleshooting)
  - [Contact](#contact)

---

## Architecture Overview

![Silka Architecture Diagram](./side-scripts/infrastructure-diagram/infrastructure.png)


The infrastructure is designed to ingest workout data from the Hevy API, store it in AWS (S3, DynamoDB), and make it queryable via Athena and Glue. A Discord bot provides an interface for users to interact with the system. Superset is used for analytics and visualization. An AI Agent (powered by AWS Bedrock Claude) enables advanced querying and context-aware analytics.

**Main AWS Components:**
- **API Gateway**: Exposes endpoints for the Discord bot.
- **Lambda Functions**:
  - `discord_bot`: Handles Discord interactions.
  - `hevy_api_caller`: Fetches and processes workout data from Hevy API.
  - `fetch_all_workouts`: Bulk fetches all workouts from Hevy.
  - `ai-agent`: An AI Agent accepting natural language questions about the data.
  - `get_table_schema`: Returns Glue/Athena table schemas for the AI Agent.
  - `execute_query`: Executes SQL queries on Athena for the AI Agent.
- **SNS**: Used for decoupling bot commands and data processing.
- **S3**: Stores raw and processed workout data.
- **DynamoDB**: Metadata and indexing for workouts.
- **Athena & Glue**: Query and catalog workout data (grouped as the Data layer).
- **dbt (Data Build Tool)**: Transforms raw workout data into analytical models, creating staging views and data marts for structured analytics and reporting.
- **AI Agent (Bedrock Claude)**: Receives user prompts (from a local script or Discord), retrieves schema and context from `get_table_schema`, executes queries via `execute_query`, and returns results to the user. It stores successfully executed queries in the vectorized database (LanceDB) to improve the future queries syntax quality.
- **Superset**: Analytics UI, deployed on EC2 or locally via Docker, connected to Athena for advanced analytics and visualization.

**Workflow Overview:**
- The Discord bot and API Gateway handle incoming requests, via set of defined in `side-scripts/discord_bot/bot_commands.py`.
- The user has to provide a one time password (OTP) with each request.
- Raw workout data from Hevy API is stored in S3 as both JSON and Parquet files, cataloged in AWS Glue.
- dbt transforms the raw data into cleaned staging models and analytical marts, creating views in Athena for easy querying.
- For analytics queries, the local script calls Bedrock Claude (AI Agent), which orchestrates calls to `get_table_schema` and `execute_query` Lambdas.
- The AI Agent uses Glue and Athena to access and query workout data (including dbt-generated views), returning results to the user.
- Superset provides a UI for direct analytics and visualization on top of Athena, with access to both raw tables and dbt marts.

---

## Repository Structure

```
.
├── environments/           # Terragrunt environment configs (dev, prod)
├── modules/                # Terraform modules (lambdas, api_gateway, ecr, dynamodb, etc.)
│   ├── lambdas/            # Lambda Docker build, variables, and deployment
│   ├── superset-user/      # IAM user for Superset
│   ├── superset_instance/  # EC2 and Docker Compose for Superset
│   └── ...                 # Other infra modules
├── dbt/                    # dbt project for data transformation
│   └── personal_gym_tracker/  # dbt models, staging, and marts
├── local_postgres/         # Local Docker Compose for Superset development
├── side-scripts/           # Utility scripts (bot commands, diagrams, etc.)
├── Makefile                # Build and deployment automation
└── README.md               # (You are here)
```

---

## Prerequisites

- **AWS Account** with sufficient permissions (IAM, Lambda, S3, DynamoDB, ECR, EC2, etc.)
- **AWS CLI** configured (`aws configure`)
- **Terraform** >= 1.6.1
- **Terragrunt** (for environment management)
- **Docker** and **Docker Compose**
- **Packer** (for building Lambda Docker images)
- **Python 3.11** (for local scripts and Superset)
- **uv** ([https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)) for Python dependency management (compatible with Pipfile/Pipfile.lock)
- **dbt-core** and **dbt-athena-community** (for data transformation) - installed via uv

---

## Environment Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-org/silka.git
    cd silka
    ```

2. **Configure AWS credentials:**
    ```sh
    aws configure
    ```

3. **Install dependencies:**
    - **Terraform:** https://learn.hashicorp.com/tutorials/terraform/install-cli
    - **Terragrunt:** https://terragrunt.gruntwork.io/docs/getting-started/install/
    - **Docker & Docker Compose:** https://docs.docker.com/get-docker/
    - **Packer:** https://developer.hashicorp.com/packer/install
    - **Python:** https://www.python.org/downloads/
    - **uv:** Follow install instructions at https://github.com/astral-sh/uv (e.g. `curl -LsSf https://astral.sh/uv/install.sh | sh`)

4. **Set up environment variables:**
    - Copy `.env.example` to `.env` in relevant directories and fill in secrets (AWS keys, Discord tokens, etc.).
    - Example for `modules/.env`:
      ```
      DISCORD_APP_PUBLIC_KEY=...
      HEVY_TOKEN=...
      OTP_RANDOM_KEY=...
      DISCORD_WEBHOOK=...
      AWS_ACCESS_KEY_ID=...
      AWS_SECRET_ACCESS_KEY=...
      AWS_DEFAULT_REGION=eu-central-1
      ```

5. **Install Python dependencies with uv:**
    - To install all dependencies from the lock file:
      ```sh
      uv sync
      ```
    - To add a new package:
      ```sh
      uv add <package>
      ```
    - For more, see [uv documentation](https://github.com/astral-sh/uv).

6. **Configure dbt:**
    - dbt configuration is already set up in `dbt/personal_gym_tracker/profiles.yml`
    - Update the profile if you need to change the Athena database, S3 staging location, or AWS profile
    - The default configuration uses:
      - Database: `<AWS_ACCOUNT_ID>_workouts_database`
      - S3 Staging: `s3://<AWS_ACCOUNT_ID>-workouts-bucket-6mabw3s4smjiozsqyi76rq/dbt`
      - AWS Profile: `cdk-dev`

---

## Deployment

### 1. Build and Push Lambda Docker Images

All Lambda functions are packaged as Docker images and pushed to AWS ECR using Packer.

- **Build and deploy all Lambda images and infrastructure:**
    ```sh
    make push-all
    ```
    This will:
    - Build all Lambda Docker images (`fetch_all_workouts`, `discord_bot`, `hevy_api_caller`, `get_table_schema`, `execute_athena_query`, `ai_agent`)
    - Push them to ECR
    - Apply Terraform via Terragrunt for the selected stage (`dev` by default)


- **Deploy a single Lambda image:**
    ```sh
    make push-fetch-all-workouts
    make push-discord-bot
    make push-hevy-api-caller
    make push-get-table-schema
    make push-execute-athena-query
    make push-ai-agent
    ```

- **Apply infrastructure only (no Docker builds):**
    ```sh
    make apply
    ```

- **Set up the LanceDB in the S3 Bucket**
    ```sh
    make init-lancedb
    ```

- **Load exercise descriptions**
    ```sh
    make load-exercises-descriptions
    ```

### 2. dbt Data Transformation

The project uses dbt (Data Build Tool) to transform raw workout data into analytical models.

- **Run all dbt models:**
    ```sh
    make run-dbt
    ```
    This will create staging views and analytical marts in your Athena database.

- **Test dbt models:**
    ```sh
    make test-dbt
    ```

- **Generate dbt documentation:**
    ```sh
    make docs-dbt
    ```

**dbt Project Structure:**
- **Staging Models** (`dbt/personal_gym_tracker/models/staging/`):
  - `stg_workouts`: Cleaned workout data with calculated duration
  - `stg_exercises`: Standardized exercise data with muscle groups
  - `stg_sets`: Set data with calculated volume (weight × reps)

- **Mart Models** (`dbt/personal_gym_tracker/models/marts/`):
  - `workout_summary`: Complete workout overview with aggregated metrics
  - `exercise_performance`: Exercise progression tracking with personal bests
  - `weekly_summary`: Weekly aggregated statistics for consistency tracking
  - `muscle_group_frequency`: Training frequency analysis by muscle group
  - `personal_records`: PR tracking with progression history
  - `exercise_frequency`: Exercise usage patterns and popularity rankings
  - `training_patterns`: Day/time patterns and consistency metrics

All models are created as views in the Athena database `926728314305_workouts_database`.

### 3. Terragrunt Environments

- **dev** and **prod** environments are managed in `environments/dev` and `environments/prod`.
- Each environment has its own `terragrunt.hcl` that points to the root modules and sets environment-specific variables.

---

## Local Development (Superset)

You can run Superset locally for development and analytics:

```sh
cd local_postgres
docker-compose up
```

- Access Superset at [http://localhost:8088](http://localhost:8088)
- Default credentials and DB connection are set via `.env` files.

---

## Modules Overview

- **lambdas/**: Lambda function deployment, ECR image lookup, SNS integration, and environment variables.
- **api_gateway.tf**: API Gateway setup for Discord bot endpoint.
- **dynamodb.tf**: DynamoDB table for workout metadata, with GSI for querying by workout day.
- **ecr.tf**: ECR repositories and lifecycle policies for Lambda images.
- **iam.tf**: IAM roles and policies for Lambda and Superset access.
- **athena/**: Athena database, Glue catalog, and S3 bucket for query results.
- **superset-user/**: IAM user and credentials for Superset to access Athena and S3.
- **superset_instance/**: EC2 and Docker Compose setup for running Superset in the cloud.

---

## Security Notes

- **Sensitive values** (tokens, secrets, keys) are loaded from `.env` files and not stored in the repository.
- **IAM policies** are scoped to only necessary resources (Athena, S3, Glue, DynamoDB, Bedrock).
- **SNS topic policy** is open for demonstration; restrict in production.
- **Superset IAM user credentials** are output as sensitive values.

---

## Troubleshooting

- **Docker image build errors:** Ensure Docker and Packer are installed and running.
- **Terraform/AWS errors:** Check AWS credentials and permissions.
- **Superset connection issues:** Verify `.env` values and that all containers are running.
- **Discord bot not responding:** Check Lambda logs in AWS Console and ensure API Gateway is deployed.

---

## Contact

For questions or contributions, please open an issue or contact the repository maintainer.
# Default deployment stage (can be overridden by setting STAGE=prod, etc.)
STAGE ?= dev

# Build and push all Lambda Docker images to ECR, then apply Terraform with Terragrunt.
push-all:
	cd modules/lambdas && \
	packer build -var 'lambda_name=fetch_all_workouts' -var 'ecr_repo_name=fetch-all-workouts' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=discord_bot' -var 'ecr_repo_name=discord-bot-lambda' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=hevy_api_caller' -var 'ecr_repo_name=hevy-api-caller' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=get_table_schema' -var 'ecr_repo_name=get-glue-table-schema' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# Build and push only the fetch_all_workouts Lambda image, then apply Terraform.
push-fetch-all-workouts:
	cd modules/lambdas && \
	packer build -var 'lambda_name=fetch_all_workouts' -var 'ecr_repo_name=fetch-all-workouts' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# Build and push only the discord_bot Lambda image, then apply Terraform.
push-discord-bot:
	cd modules/lambdas && \
	packer build -var 'lambda_name=discord_bot' -var 'ecr_repo_name=discord-bot-lambda' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# Build and push only the hevy_api_caller Lambda image, then apply Terraform.
push-hevy-api-caller:
	cd modules/lambdas && \
	packer build -var 'lambda_name=hevy_api_caller' -var 'ecr_repo_name=hevy-api-caller' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# Build and push only the get_table_schema Lambda image, then apply Terraform.
push-get-table-schema:
	cd modules/lambdas && \
	packer build -var 'lambda_name=get_table_schema' -var 'ecr_repo_name=get-glue-table-schema' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# Only apply Terraform (no Docker builds).
apply:
	cd environments/$(STAGE) && \
	terragrunt apply

# Create LanceDB database and upload initial data.
init-lancedb:
	cd side-scripts/initiate-lance-db && \
	uv run initiance-lance-db.py
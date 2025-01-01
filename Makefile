STAGE ?= dev

# pushes all lambdas to ECR and applies the terraform
push-all:
	cd modules/lambdas && \
	packer build -var 'lambda_name=fetch_all_workouts' -var 'ecr_repo_name=fetch-all-workouts' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=discord_bot' -var 'ecr_repo_name=discord-bot-lambda' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=hevy_api_caller' -var 'ecr_repo_name=hevy-api-caller' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# pushes the fetch all workouts lambda to ECR and applies the terraform
push-fetch-all-workouts:
	cd modules/lambdas && \
	packer build -var 'lambda_name=fetch_all_workouts' -var 'ecr_repo_name=fetch-all-workouts' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# pushes the discord bot lambda to ECR and applies the terraform
push-discord-bot:
	cd modules/lambdas && \
	packer build -var 'lambda_name=discord_bot' -var 'ecr_repo_name=discord-bot-lambda' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# pushes the hevy api caller lambda to ECR and applies the terraform
push-hevy-api-caller:
	cd modules/lambdas && \
	packer build -var 'lambda_name=hevy_api_caller' -var 'ecr_repo_name=hevy-api-caller' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/$(STAGE) && \
	terragrunt apply

# applies the terraform
apply:
	cd environments/$(STAGE) && \
	terragrunt apply
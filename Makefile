push-packer:
	cd modules/lambdas && \
	packer build -var 'lambda_name=fetch_all_workouts' -var 'ecr_repo_name=fetch-all-workouts' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=discord_bot' -var 'ecr_repo_name=discord-bot-lambda' ./packer_docker_template.pkr.hcl && \
	packer build -var 'lambda_name=hevy_api_caller' -var 'ecr_repo_name=hevy-api-caller' ./packer_docker_template.pkr.hcl && \
	cd ../../environments/dev && \
	terragrunt apply
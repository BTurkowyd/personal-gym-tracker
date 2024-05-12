# A simple discord bot using AWS resources (almost free).

## Prerequisites:
1. Own Discord server where you can set up and test your bot application. https://discordpy.readthedocs.io/en/stable/discord.html. There you will get a few authorization values such as `APPLICATION ID`, `PUBLIC KEY` in the `General information` section and `TOKEN` in the `Bot` section which have to be stored in `.env` files mention in point 5..
2. AWS account with an IAM user account which has access keys generated (programmatic access): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html?icmpid=docs_iam_console#Using_CreateAccessKey. This is required for `terraform`.
3. Installed `terraform`: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli#install-terraform
4. Python 3.11 with `pipenv` installed. https://pypi.org/project/pipenv/. While `pipenv` is not mandatory and libraries listed in `Pipfile` can be installed manually with `pip`, `pipenv` makes it much easier and organized.
5. Two `.env` files, one within `./modules` folder which defines environmental variables for lambda functions, another in `./side-scripts/discord_bot` storing environmental variables for `bot_commands.py`

## Setting up the infrastructure in AWS
1. Open the terminal.
2. Be sure that the IAM user with the programmatic access is active:
   - You can check it by executing the following command: `aws configure list`. The output should show the user profile name, access key and secret key (both keys are hidden).
   - If that is not the case, execute the following command: `export AWS_PROFILE='profile-name'`
3. In terminal go to `./modules`
4. Execute the following command `terraform apply`. Then you have to confirm by typing in `yes` in the terminal. You can auto-confirm it by executing `terraform apply -auto-approve`.
5. Infrastructure is set up.

## Setting an interaction endpoint URL in Discord Application.
1. In the AWS console go to `API Gateway`, select the API you created.
2. On the left panel go to `Stages`, 
3. In the main window click the `+` symbol next to the stage name to unwrap it, then do it the same until you will see the `POST` method.
4. There you will see the `Invoke URL`, which you have to copy and paste it in the point 7.
5. Go to https://discord.com/developers/applications
6. Select `Applications` on the left panel and then click on your application/bot.
7. Go to `General information` section and in the `INTERACTIONS ENDPOINT URL` field paste the `Invoke URL` from the point 4. and save changes.
8. If everything goes smoothly, discord will send a `PING` request to the lambda to confirm that endpoint works and returns the proper value.
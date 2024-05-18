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

## A few words from the repository owner.
In the [I was inspired by section](#i-was-inspired-by) I linked a several resources which were guiding me through this process, but I never used any of this tutorial in 100%, even if they are correct. Here is why:
1. In some of these tutorials a dedicated Discord library for Python is used which makes this set up much easier. However, providing additional libraries for AWS Lambda is a bit of a hassle, and wanted to keep the number of additional libraries as low as possible.
   - I was forced to provide some libraries as AWS Lambda Layers anyway ([requests](https://pypi.org/project/requests/) and [PyNaCl](https://pypi.org/project/PyNaCl/)). In one of the tutorials it is shown how it can be dealt with by using docker [AWS Lambda images](https://hub.docker.com/r/amazon/aws-lambda-python), which is supposed to use proper library build files, but still it looked like quite a lot of work.
   - It is critical to provide libraries for the proper system/environment (e.g. trying to create a Lambda layer with Windows compatible library will fail as Lambda is not running on Windows).
   - `requests` library has only one built distribution, so it was easy to download/unpack it and make a layer out of it by using `pip`. But for `PyNaCl` I had to do a trial and error in finding which built distribution to use and furthermore I had to check which third libraries it uses and download the proper built distributions too. Luckily it was not too much work, but it is definitely not the best way to go and using the docker approach is advised.
   - As a positive side effect, I have an AWS Lambda compatible `PyNaCl` layer which deserves its own repo for others who would like to use it. 
2. Not unexpectedly, all these tutorials are shown only in AWS console and are not using any infrastructure as code (IaC) approach. I simply wanted to have a nice and clean system design. 
3. In my opinion these tutorials which are recommending using API Gateway are missing one, very important piece of information, which caused me to spend one evening to solve the problem. 
   - In these tutorials they suggest that setting up an API Gateway (either HTTP or REST) with default settings will do the job. It is only 50% correct. This is correct as long as you create that resource via AWS console browser.
   - While sending a request which was triggering the AWS Lambda bot and it was executing the code as expected, it was not returning the response to the Discord application despite having the return value set properly.
   - The missing piece of puzzle was method response setting in the REST API (see [here](https://github.com/BTurkowyd/silka/blob/main/modules/api_gateway.tf#L18)). After setting it to `application/json` response model, the API Gateway was able to return the response further to the Discord application.
   - So to summarize: it has to be the REST API and it needs a response model to be set up to `application/json`.

## I was inspired by.
- https://youtu.be/BmtMr6Nmz9k?si=aHoztPlpJMtuAi56
- https://youtu.be/1yLfjMtsV9s?si=P8Q6y90wZ8ajmhkz
- https://github.com/ker0olos/aws-lambda-discord-bot?tab=readme-ov-file
- https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292
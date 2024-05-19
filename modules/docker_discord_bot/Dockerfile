FROM public.ecr.aws/lambda/python:3.11

COPY ./src/discord_bot.py "${LAMBDA_TASK_ROOT}"
COPY ./src/requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["discord_bot.lambda_handler"]
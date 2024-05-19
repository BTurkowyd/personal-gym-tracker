FROM public.ecr.aws/lambda/python:3.11

COPY ./src/hevy_api_caller.py "${LAMBDA_TASK_ROOT}"
COPY ./src/requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["hevy_api_caller.lambda_handler"]
FROM public.ecr.aws/lambda/python:3.11

COPY ./src/fetch_all_workouts.py "${LAMBDA_TASK_ROOT}"
COPY ./src/requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["fetch_all_workouts.lambda_handler"]
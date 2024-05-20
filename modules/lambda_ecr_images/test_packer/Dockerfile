FROM public.ecr.aws/lambda/python:3.11

COPY src/test_packer.py "${LAMBDA_TASK_ROOT}"
COPY ./src/requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["test_packer.lambda_handler"]
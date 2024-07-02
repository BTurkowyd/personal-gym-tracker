from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.integration import SNS
from diagrams.onprem.client import Client
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.analytics import Glue, Athena

with Diagram("Infrastructure", show=False):
    hevy_server = Client('Hevy server')
    superset = Client('Superset/Local computer')

    with Cluster("AWS Account"):
        api_gateway = APIGateway('Bot endpoint')
        bot = Lambda('Discord bot')
        sns = SNS("SNS")

        glue = Glue('Workout database')
        athena = Athena('Workout SQL executor')

        with Cluster('API calls'):
            fetch_all = Lambda('Fetch all workouts')
            hevy_api_caller = Lambda('Hevy API caller')

        with Cluster('Storage'):
            s3 = S3('Workouts file storage')
            dynamodb = Dynamodb('Workouts table')

        api_gateway >> bot >> sns >> [fetch_all, hevy_api_caller]
        fetch_all >> [s3, dynamodb]
        hevy_api_caller >> [s3, dynamodb]
        s3 >> glue >> athena
        # sns >> fetch_all
        # sns >> hevy_api_caller

    [fetch_all, hevy_api_caller] >> hevy_server
    hevy_server >> [fetch_all, hevy_api_caller]
    athena >> superset
    superset >> [api_gateway, athena]





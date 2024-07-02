from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.integration import SNS
from diagrams.onprem.client import Client
from diagrams.onprem.analytics import Superset
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.analytics import Glue, Athena

graph_attr = {
    "bgcolor": "transparent",    # Set background color to transparent
    "style": "dotted, bold"
}

with Diagram("Infrastructure", show=False):
    hevy_server = Client('Hevy server')
    superset = Superset('Superset')
    api_gateway = APIGateway('Bot endpoint')

    with Cluster("AWS Account", direction='LR', graph_attr=graph_attr):
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

        bot >> sns >> [fetch_all, hevy_api_caller]
        fetch_all >> Edge(color='#00AA33') >> s3
        fetch_all >> Edge(color='#0033FF') >> dynamodb
        hevy_api_caller >> Edge(color='#00AA33') >> s3
        hevy_api_caller >> Edge(color='#0033FF') >> dynamodb
        s3 >> glue >> athena

    api_gateway >> bot
    bot >> api_gateway
    [fetch_all, hevy_api_caller] >> Edge(style='dotted, bold') >> hevy_server
    hevy_server >> Edge(style='dotted, bold') >> [fetch_all, hevy_api_caller]
    athena >> superset
    superset >> athena





from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.integration import SNS
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.analytics import Superset
from diagrams.onprem.database import PostgreSQL
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.ml import Bedrock

graph_attr = {
    "bgcolor": "transparent",  # Set background color to transparent
    "style": "dotted, bold",
}

with Diagram("Infrastructure", show=False):
    hevy_server = PostgreSQL("Hevy Backend DB")
    api_gateway = APIGateway("Bot endpoint")
    user_script = Client("Local prompt")

    with Cluster("AWS ACCOUNT", direction="LR", graph_attr=graph_attr):
        bot = Lambda("Discord bot")
        sns = SNS("SNS")

        with Cluster("HEVY API CALLS"):
            fetch_all = Lambda("Backfill all workouts")
            hevy_api_caller = Lambda("API caller")

        with Cluster("STORAGE & METADATA"):
            s3 = S3("Workouts file storage")
            dynamodb = Dynamodb("Workouts metadata")

        with Cluster("DATA"):
            glue = Glue("Workout database")
            athena = Athena("Workout SQL executor")

        # Connections inside AWS Account
        bot >> sns
        sns >> fetch_all
        sns >> hevy_api_caller
        fetch_all >> Edge(color="#00AA33") >> s3
        fetch_all >> Edge(color="#0033FF") >> dynamodb
        hevy_api_caller >> Edge(color="#00AA33") >> s3
        hevy_api_caller >> Edge(color="#0033FF") >> dynamodb
        s3 >> glue
        glue >> athena

        with Cluster("AI AGENT", direction="LR"):
            with Cluster("LLM"):
                bedrock = Bedrock("Bedrock Claude Model")
            with Cluster("LANCE DB"):
                lancedb = Server("LanceDB Vector DB")
            with Cluster("AI AGENT TOOLS"):
                # Define tools as Lambda functions
                get_table_schema = Lambda("Get Table Schema")
                execute_query = Lambda("Execute Query")

        # AI Agent connections
        get_table_schema >> glue
        glue >> get_table_schema  # return arrow
        execute_query >> athena
        athena >> execute_query  # return arrow
        execute_query >> lancedb
        lancedb >> get_table_schema
    # Connections outside AWS Account

    superset = Superset("Superset")

    user_script >> bedrock
    bedrock >> user_script  # return arrow
    bedrock >> get_table_schema
    get_table_schema >> bedrock  # return arrow
    bedrock >> execute_query
    execute_query >> bedrock  # return arrow
    fetch_all >> Edge(style="dotted, bold") >> hevy_server
    hevy_api_caller >> Edge(style="dotted, bold") >> hevy_server
    hevy_server >> Edge(style="dotted, bold") >> fetch_all
    hevy_server >> Edge(style="dotted, bold") >> hevy_api_caller
    athena >> superset
    superset >> athena
    # Bidirectional connection between API Gateway and Discord bot
    api_gateway >> bot
    bot >> api_gateway

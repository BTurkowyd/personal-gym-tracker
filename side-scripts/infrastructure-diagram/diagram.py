graph_attr = {
    "bgcolor": "transparent",  # Set background color to transparent
    "style": "dotted, bold",
}

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

# ----------------------
# 1. DATA FEEDING DIAGRAM
# ----------------------
with Diagram(
    "Data Feeding Architecture", show=False, filename="data_feeding_architecture"
):
    hevy_server = PostgreSQL("Hevy Backend DB")

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

        # Data ingestion connections
        bot >> sns
        sns >> fetch_all
        sns >> hevy_api_caller
        fetch_all >> Edge(color="#00AA33") >> s3
        fetch_all >> Edge(color="#0033FF") >> dynamodb
        hevy_api_caller >> Edge(color="#00AA33") >> s3
        hevy_api_caller >> Edge(color="#0033FF") >> dynamodb
        s3 >> glue
        glue >> athena

    # External ingestion connections
    fetch_all >> Edge(style="dotted, bold") >> hevy_server
    hevy_api_caller >> Edge(style="dotted, bold") >> hevy_server
    hevy_server >> Edge(style="dotted, bold") >> fetch_all
    hevy_server >> Edge(style="dotted, bold") >> hevy_api_caller

# ----------------------
# 2. DATA RETRIEVAL DIAGRAM
# ----------------------
with Diagram(
    "Data Retrieval Architecture",
    show=False,
    filename="data_retrieval_architecture",
    direction="TB",
):
    api_gateway = APIGateway("Bot endpoint")  # Now outside AWS account

    with Cluster("AWS ACCOUNT", direction="LR", graph_attr=graph_attr):
        bot = Lambda("Discord bot")

        with Cluster("DATA"):
            glue = Glue("Workout database")
            athena = Athena("Workout SQL executor")

        with Cluster("AI AGENT", direction="LR"):
            with Cluster("LLM"):
                bedrock = Bedrock("Bedrock Claude Model")
            with Cluster("LANCE DB"):
                lancedb = Server("LanceDB Vector DB")
            with Cluster("AI AGENT TOOLS"):
                get_table_schema = Lambda("Get Table Schema")
                execute_query = Lambda("Execute Query")

        # Retrieval connections
        _ = glue >> get_table_schema
        _ = athena >> execute_query
        _ = execute_query >> lancedb
        _ = lancedb >> get_table_schema

    superset = Superset("Superset")

    # User and tool interactions
    _ = bedrock >> get_table_schema
    _ = get_table_schema >> bedrock
    _ = bedrock >> execute_query
    _ = execute_query >> bedrock
    _ = athena >> superset
    _ = superset >> athena

    # API Gateway and Discord bot outside AWS
    _ = api_gateway >> bot
    _ = bot >> api_gateway

    # Discord bot can call LLM (Bedrock)
    _ = bot >> bedrock

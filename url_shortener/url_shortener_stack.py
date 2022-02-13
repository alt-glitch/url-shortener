from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from constructs import Construct

class UrlShortenerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
        table = dynamodb.Table(
            self, "mapping-table", # scope is the construct which contains THIS construct
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        )

        function = _lambda.Function(
            self, 'backend',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('./lambda'),
            handler = 'handler.main'
        )

        table.grant_read_write_data(function)
        function.add_environment("TABLE_NAME", table.table_name)

        gateway = apigw.LambdaRestApi(
            self, 'api',
            handler = function
        )
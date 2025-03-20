import boto3
class S3Manager:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        

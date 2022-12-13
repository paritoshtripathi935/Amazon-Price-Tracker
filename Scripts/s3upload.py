import os
import boto3
import time

class S3Helper:
    def __init__(self, aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                 aws_secret_access_key=os.getenv('AWS_ACCESS_KEY_SECRET'),
                 aws_region_name=os.getenv('AWS_REGION'),
                 current_dir = os.getcwd()):
        self.session = boto3.session.Session(aws_access_key_id=aws_access_key_id,
                                             aws_secret_access_key=aws_secret_access_key,
                                             region_name=aws_region_name)
        self.resource = self.session.resource('s3')
        self.data_path = os.path.join(current_dir, "data")
    
    def upload(self,stamp):
        s3_path = f"s3://django-portfolio-paritosh/bigdata/{stamp}/"
        zip_file_path = '/home/paritosh/My-Projects/amazon-price-tracker/Data/files/{}/Data.json'.format(stamp)
        print(zip_file_path)
        os.system(f"aws s3 cp {zip_file_path} {s3_path}")


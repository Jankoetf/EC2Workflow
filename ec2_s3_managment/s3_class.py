import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import joblib
import io
import json

from ec2_s3_managment.ec2_s3_constants import (
    S3_PREFIX, METRICS_FILENAME, LOGGER_FILENAME, MODEL_FILENAME, LOCAL_OUTPUT_PATH, LOGGER_OUT_PATH)
from ec2_s3_managment.logger_config import logger
load_dotenv(".env")
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


class S3ManagerClass:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.last_index, self.output_exists = self.get_max_output_index()
        self.new_index = self.last_index + 1
        
        self.s3_upload_output_root = f"{S3_PREFIX}_{self.new_index}"
        self.s3_download_output_root = f"{S3_PREFIX}_{self.last_index}" if self.output_exists else None

        self.model_upload_path = self.s3_upload_output_root + f"/{MODEL_FILENAME}.joblib"
        self.model_download_path = self.s3_upload_output_root + f"/{MODEL_FILENAME}.joblib"

        self.metrics_upload_path = self.s3_upload_output_root + f"/{METRICS_FILENAME}.json"
        self.metrics_upload_path = self.s3_upload_output_root + f"/{METRICS_FILENAME}.json"

        self.logger_output_path = self.s3_upload_output_root + f"/{LOGGER_FILENAME}.log"
        self.logger_output_path = self.s3_upload_output_root + f"/{LOGGER_FILENAME}.log"

    def get_max_output_index(self):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Delimiter='/'
            )
            
            # Folders are returned as CommonPrefixes
            root_folders = []
            if 'CommonPrefixes' in response:
                for prefix in response['CommonPrefixes']:
                    root_folders.append(prefix['Prefix'])
            
            max_index, prefix_length = 0, len(S3_PREFIX)

            for folder_name in root_folders:
                if folder_name.startswith(S3_PREFIX + "_"):
                    
                    max_index = max(int(folder_name[prefix_length+1:-1]), max_index)
            return max_index, max_index != 0

        except ClientError as e:
            print(f"Error listing root contents of the bucket: {e}")
            raise

    def upload_single_file(self, local_file_path):
        try:
            self.s3_client.upload_file(
                Filename=local_file_path,  #local path
                Bucket=S3_BUCKET_NAME,  
                Key=self.s3_output_root + "/" + local_file_path  # S3 path
            )
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    def upload_model_to_s3(self):
        try:    
            # Serialize the model to a bytes buffer in memory
            model_buffer = io.BytesIO()
            joblib.dump(self.model, model_buffer)
            model_buffer.seek(0)  # Reset buffer position to beginning
            
            # Upload the model directly from memory to S3
            logger.info(f"Uploading model to S3 bucket {S3_BUCKET_NAME}, key: {self.s3_output_root}/{MODEL_FILENAME}")
            self.s3_client.upload_fileobj(
                model_buffer, 
                S3_BUCKET_NAME, 
                self.model_output_path
            )
            logger.info(f"Successfully uploaded to s3://{S3_BUCKET_NAME}/{self.s3_output_root}")
        except Exception as e:
            print(f"Error uploading model to S3: {e}")
            return None
        
    def upload_metrics_to_s3(self, metrics_dict):
        try:
            # Convert the metrics dictionary to a JSON string then to bytes
            logger.info(f"Uploading metrics to S3 bucket {S3_BUCKET_NAME}, key: {self.metrics_output_path}")
            metrics_data = json.dumps(metrics_dict, indent=4).encode('utf-8')
            
            # Upload the metrics directly to S3
            self.s3_client.put_object(
                Body=metrics_data,
                Bucket=S3_BUCKET_NAME,
                Key=self.metrics_output_path
            )
            logger.info(f"Uploading succesfull")
            
        except Exception as e:
            print(f"Error uploading metrics to S3: {e}")
            return None
        
    def upload_log_to_s3(self):
        try:
            # If log_content is a file path, upload the file
            self.s3_client.upload_file(
                LOGGER_OUT_PATH,
                S3_BUCKET_NAME,
                self.logger_output_path
            )

        except Exception as e:
            print(f"Error uploading log to S3: {e}")
            return None
        

    def download_experiment_files_from_s3(self):
        # Create the local folder if it doesn't exist
        os.makedirs(LOCAL_OUTPUT_PATH, exist_ok=True)
        print("LOCAL_OUTPUT_PATH: ", LOCAL_OUTPUT_PATH)
        response = self.s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=self.s3_last_output_root
        )
        os.makedirs(LOCAL_OUTPUT_PATH + "/" + S3_PREFIX + "_" + str(self.last_index), exist_ok=True)


        for obj in response['Contents']:
            # Get the S3 key (full path in S3)
            s3_key = obj['Key']
            print("response: ", s3_key)
            
            # Create the local file path
            local_path = LOCAL_OUTPUT_PATH + "/" + s3_key
            print("local_path: ", local_path)

            
            print(f"Downloading {s3_key} to {local_path}...")
            # Download the file
            self.s3_client.download_file(
                S3_BUCKET_NAME,
                s3_key,
                local_path
            )

    def __str__(self):
        output_string = f"self.last_index: {self.last_index}\n"
        output_string += f"self.output_exists: {self.output_exists}\n"
        output_string += f"self.new_index: {self.new_index}\n"
        output_string += f"self.s3_output_root: {self.s3_output_root}\n"
        output_string += f"self.s3_last_output_root {self.s3_last_output_root}\n"
        output_string += f"self.model_output_path: {self.model_output_path}\n"
        output_string += f"self.metrics_output_path: {self.metrics_output_path}\n"
        output_string += f"self.logger_output_path: {self.logger_output_path}\n"

        return output_string
        



## AWS Transcribe Project
This project is a web application designed to transcribe audio files into text using AWS Transcribe. It allows users to upload audio files, processes them through AWS, and returns the transcribed text. The project integrates Amazon S3 for file storage, Amazon Transcribe for speech-to-text conversion, and Vue.js for the frontend.

## Features
- Upload audio files (e.g., .mp3, .wav) for transcription
- Store uploaded files in an S3 bucket
- Automatically process audio files using AWS Transcribe
- Display the transcribed text on the frontend
- Real-time updates on transcription progress

## Tech Stack
- **Frontend**: Vue.js
- **Backend**: AWS Lambda (serverless architecture)
- **File Storage**: Amazon S3
- **Speech-to-Text**: Amazon Transcribe
- **API Gateway**: AWS API Gateway

## Prerequisites
Before setting up the project, ensure you have the following:
- AWS Account
- Node.js and npm installed
- AWS CLI configured on your machine
- Required IAM roles for S3, Transcribe, and Lambda services

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/SarayutBz/AWS_Transribe.git
cd AWS_Transribe
```

### 2. Install dependencies
Navigate to the frontend folder and install the necessary packages:

```
npm install
```

### 3. AWS S3 and Transcribe Setup
- Create two S3 buckets: one for input files (e.g., input-files-transcribe-1) and one for storing output files.
- Configure Amazon Transcribe to work with these S3 buckets.

### 4. Backend Setup
- Create an AWS Lambda function that triggers on file uploads to the S3 bucket.

## Use Python
### Lambda Function Example (CreateUploadUrl) 
```
import json
import boto3
import uuid
from datetime import timedelta

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket_name = 'input-files-transcribe'
        file_key = f'{uuid.uuid4()}.mp3'
        expiration = timedelta(minutes=5)
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key,
                'ContentType': 'audio/mpeg'
            },
            ExpiresIn=int(expiration.total_seconds())
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'pre_signed_url': presigned_url,
                'file_key': file_key
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
```
### Lambda Function Example (Transcribe) 
```
import json
import boto3
import uuid
import logging

# ตั้งค่าการบันทึก
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

transcribe_client = boto3.client('transcribe')

def lambda_handler(event, context):
    try:
        # ตรวจสอบว่า 'body' มีอยู่ใน event หรือไม่
        if 'body' not in event:
            raise ValueError("Request body is missing")

        # แปลง JSON string เป็น dictionary
        body = json.loads(event['body'])
        
        # ตรวจสอบว่า 'file_url' มีอยู่ใน body หรือไม่
        if 'file_url' not in body:
            raise ValueError("file_url is required in the event body")

        file_url = body['file_url']
        job_id = f"job-{str(uuid.uuid4())}"  # ใช้ job_id เพียงอย่างเดียว
        
        # ตรวจสอบว่า 'language_code' มีอยู่ใน body หรือไม่ ถ้าไม่มีให้ใช้ 'en-US' เป็นค่าเริ่มต้น
        language_code = body.get('language_code', 'en-US')

        # เริ่มงานการถอดเสียงโดยใช้ language_code ที่ส่งมา
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_id,
            LanguageCode=language_code,  # ใช้ค่า language_code ที่ผู้ใช้ส่งมา
            MediaFormat="mp3",
            Media={"MediaFileUri": file_url},
            OutputBucketName="output-files-transcribe"
        )

        logger.info(f"Transcription job started: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({'job_id': job_id}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
```
### Lambda Function Example (FetchS3) 
```
import json
import boto3
import logging

# ตั้งค่าการบันทึก
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # ตรวจสอบว่า 'queryStringParameters' และ 'job_id' มีอยู่ใน event หรือไม่
        if 'queryStringParameters' not in event or 'job_id' not in event['queryStringParameters']:
            raise ValueError("job_id is required in the query string")

        job_id = event['queryStringParameters']['job_id']
        output_bucket = "output-files-transcribe"
        output_key = f"{job_id}.json"  # ใช้ job_id เป็น Key ของไฟล์

        # ดึงไฟล์จาก S3
        response = s3_client.get_object(Bucket=output_bucket, Key=output_key)
        transcription_result = response['Body'].read().decode('utf-8')

        return {
            'statusCode': 200,
            'body': transcription_result,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
```
### Lambda Function Example (CheckTranscriptionStatusFunction) 
```
import json
import boto3

def lambda_handler(event, context):
    transcribe = boto3.client('transcribe')
    
    # ดึง job_id จาก query string parameters
    job_id = event.get('queryStringParameters', {}).get('job_id')
    
    if not job_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Job ID is required'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    try:
        # ตรวจสอบสถานะของ transcription job
        response = transcribe.get_transcription_job(TranscriptionJobName=job_id)
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': status}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
```


### 5. API Gateway Setup
Configure the following API routes:
- **/presigned-url**: POST
- **/transcription**: POST
- **/transcription-result**: GET
- **/transcription-status**: GET

### 6. Environment Variables
Create an `.env` file in the root of the project and add the necessary AWS credentials and S3 bucket information:

```
VUE_APP_API_URL="//your-api-url.com"
```

### 7. Run the Application
```
npm run serve
```
Navigate to http://localhost:8080 to access the application.

## How it Works
1. Users upload an audio file via the frontend.
2. The file is uploaded to the S3 input bucket.
3. A Lambda function is triggered to process the file with AWS Transcribe.
4. Transcription results are stored and displayed on the frontend.

## License
This project is licensed under the MIT License.




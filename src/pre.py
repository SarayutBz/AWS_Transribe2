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

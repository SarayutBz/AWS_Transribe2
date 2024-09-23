## AWS Transcribe Project
This project is a web application designed to transcribe audio files into text using AWS Transcribe. It allows users to upload audio files, processes them through AWS, and returns the transcribed text. The project integrates Amazon S3 for file storage, Amazon Transcribe for speech-to-text conversion, and Vue.js for the frontend.

## Features
Upload audio files (e.g., .mp3, .wav) for transcription
Store uploaded files in an S3 bucket
Automatically process audio files using AWS Transcribe
Display the transcribed text on the frontend
Real-time updates on transcription progress
## Tech Stack
Frontend: Vue.js
Backend: AWS Lambda (serverless architecture)
File Storage: Amazon S3
Speech-to-Text: Amazon Transcribe
API Gateway: AWS API Gateway
Prerequisites
Before setting up the project, ensure you have the following:

## AWS Account
* Node.js and npm installed
* AWS CLI configured on your machine
* Required IAM roles for S3, Transcribe, and Lambda services
### Setup Instructions
1. Clone the repository

```
git clone https://github.com/SarayutBz/AWS_Transribe.git
cd AWS_Transribe
```
2. Install dependencies
Navigate to the frontend folder and install the necessary packages:

```
npm install
```

3. AWS S3 and Transcribe Setup
Create two S3 buckets: one for input files (e.g., input-files-transcribe-1) and one for storing output files.
Configure Amazon Transcribe to work with these S3 buckets.
4. Backend Setup
* Create an AWS Lambda function that triggers on file uploads to the S3 bucket.
* Configure the Lambda function to call Amazon Transcribe on file uploads.
* Set up an API Gateway to communicate between the frontend and AWS Lambda.
5. Environment Variables
Create an .env file in the root of the project and add the necessary AWS credentials and S3 bucket information:

```
VUE_APP_API_URL="//your-api-url.comI"
```

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


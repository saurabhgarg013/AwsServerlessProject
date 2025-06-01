# AwsServerlessProject

This project aims to showcase a scalable, serverless e-commerce order processing system built on AWS.
It ensures reliable inventory tracking, seamless customer notifications, and effective failure handling to maintain operational continuity and enhance user experience. 
The system demonstrates the power of AWS serverless architecture to handle dynamic workloads, automate error recovery, and provide actionable insights through monitoring, making it ideal for modern e-commerce applications.

Synchronous Invocation
The caller waits for the Lambda function to finish.
The response (output or error) is returned to the caller.
Common in real-time APIs and interactive workflows.

Asynchronous Invocation
The function is called and returns immediately.
The caller does not wait for the result.
Lambda processes the event in the background.
Retries automatically if there’s an error (up to 2 times).


# cloudtrail-daily-email
AWS Lambda function to email cloudtrail logs daily

This Lambda Function sends an email daily with the datetime, username and action of every AWS action performed in the previous 24 hours. Provides an additional measure of visibility for your infrastructure.

Uses SES to send the emails. If you don't have SES configured, it's pretty easy to just verify one email address and put that into this function's environmental variables as the sender and receiver.
http://docs.aws.amazon.com/ses/latest/DeveloperGuide/setting-up-email.html

Setup:

1. Configure AWS SES in an available region and verify at least one email address
2. Create an IAM policy for this Lambda Function. Required permission:
    * ses:SendEmail
    * cloudtrail:LookupEvents
    * logs:CreateLogGroup
    * logs:CreateLogStream
    * logs:PutLogEvents
3. Create a new role of type  and attach policy
4. Create a new custom Lambda Function
    * runtime:python3.6
    * name:Cloudtrail-Daily-Email
    * handler:Cloudtrail-Daily-Email.handler
    * trigger:Cloudwatch Events
        * This cron will trigger at 7:00UTC every day: cron(0 7 * * ? *)
    * edit code inline and paste in the code from this repo
5. Configure environmental variables (all required):
    * toEmails (comma seperated list)
    * fromEmail
    * sesRegion


Example IAM policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudtrail:LookupEvents"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

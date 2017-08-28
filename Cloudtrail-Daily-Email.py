import boto3
import logging
import os
from datetime import datetime


def logs_call(cloudtr,next_token=None):
    if next_token is None:
        res = cloudtr.lookup_events()
    else:
        res = cloudtr.lookup_events(NextToken=next_token)
    return(res)

def get_logs(func_name):
    cloudtrclient = boto3.client('cloudtrail')
    res = logs_call(cloudtrclient)
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        all_events = res['Events']
        alog = all_events[0]
        now = datetime.now(alog['EventTime'].tzinfo)
        while 'NextToken' in res.keys() and (now - all_events[-1]['EventTime']).total_seconds() < 86400:
            res = logs_call(cloudtrclient,next_token=res['NextToken'])
            all_events = all_events + res['Events']
        days_events = []
        for event in all_events:
            if (now - event['EventTime']).total_seconds() < 86400 and event['Username'] != func_name:
                days_events.append(event)
    else:
        days_events = None
    return(res['ResponseMetadata']['HTTPStatusCode'],days_events)
    
def send_mail(logs):
    log_line = "\n{dt} | {un} | {ev}"
    output = "AWS Cloudtrail events for the last 24 hours:\n"
    for log in logs:
        output += log_line.format(dt=log['EventTime'],un=log['Username'],ev=log['EventName'])
    ses = boto3.client('ses',region_name=os.environ['sesRegion'])
    from_email = os.environ['fromEmail']
    to_emails = os.environ['toEmails'].split(",")
    res = ses.send_email(
            Source = from_email,
            Destination = {'ToAddresses':to_emails},
            Message = {
                    'Subject':{'Data':'Daily Cloudtrail Events'},
                    'Body':{'Text':{'Data':output}}
                }
        )
    return(res)

def handler(event,context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    resp_code,logs = get_logs(func_name=context.function_name)
    if logs is not None:
        if logs:
            logger.info("Got {n} logs. Sending emails".format(n=len(logs)))
            sesres = send_mail(logs)
            logger.info(sesres)
        else:
            logger.info("No logs found. Exiting")
    else:
        logger.error("Error making API call. Status code: {sc}".format(sc=resp_code))

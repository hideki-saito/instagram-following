import requests
import boto3
import botocore
import config

def check(bucket_name, key):
    s3 = boto3.resource('s3')
    exists = False

    try:
        s3.Object(bucket_name, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False
        else:
            raise
    else:
        exists = True

    return exists

def check_bucket(bucket_name):
    s3 = boto3.resource('s3')
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError:
        s3.create_bucket(Bucket=bucket_name)


def update_metadata(bucket_name, key):
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucket_name, key)
    api_client = s3.meta.client
    if key.split(".")[-1] == "jpeg":
        response = api_client.copy_object(Bucket=bucket_name,
                                          Key=key,
                                          ContentType='image/jpeg',
                                          MetadataDirective="REPLACE",
                                          CopySource=bucket_name + "/" + key)
    else:
        response = api_client.copy_object(Bucket=bucket_name,
                                          Key=key,
                                          ContentType='audio/mpeg',
                                          MetadataDirective="REPLACE",
                                          CopySource=bucket_name + "/" + key)

    s3_object.Acl().put(ACL='public-read')


def upload(url, filename):
    # credentials = {
    #     'aws_access_key_id': config.AWS_ACCESS_KEY_ID,
    #     'aws_secret_access_key': config.AWS_SECRET_ACCESS_KEY
    # }
    # Uses the creds in ~/.aws/credentials
    s3 = boto3.resource('s3')
    bucket_name = config.aws_bucket

    req_for_image = requests.get(url, stream=True)
    file_object_from_req = req_for_image.raw
    req_data = file_object_from_req.read()

    exists = check(bucket_name, filename)
    count = 1
    while exists:
        filename = os.path.splitext(filename)[0].split("-")[0] + "-" + str(count) + os.path.splitext(filename)[1]
        exists = check(bucket_name, filename)
        count = count + 1

    # Do the actual upload to s3
    if filename.split(".")[-1] == "jpeg":
        s3.Bucket(bucket_name).put_object(Key=filename, Body=req_data, ACL='public-read')
    else:
        s3.Bucket(bucket_name).put_object(Key=filename, Body=req_data, ACL='public-read')

    update_metadata(bucket_name, filename)
    file_url = '%s/%s/%s' % ('https://s3.amazonaws.com', bucket_name, filename)

    return file_url

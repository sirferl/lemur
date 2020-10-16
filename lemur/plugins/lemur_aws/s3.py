"""
.. module: lemur.plugins.lemur_aws.s3
    :platform: Unix
    :synopsis: Contains helper functions for interactive with AWS S3 Apis.
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from flask import current_app
from .sts import sts_client

from botocore.exceptions import ClientError
from lemur.extensions import sentry


@sts_client("s3", service_type="resource")
def put(bucket_name, region, prefix, data, encrypt, **kwargs):
    """
    Use STS to write to an S3 bucket
    """
    bucket = kwargs["resource"].Bucket(bucket_name)
    current_app.logger.debug(
        "Persisting data to S3. Bucket: {0} Prefix: {1}".format(bucket_name, prefix)
    )

    # get data ready for writing
    if isinstance(data, str):
        data = data.encode("utf-8")

    if encrypt:
        bucket.put_object(
            Key=prefix,
            Body=data,
            ACL="bucket-owner-full-control",
            ServerSideEncryption="AES256",
        )
    else:
        try:
            bucket.put_object(Key=prefix, Body=data, ACL="bucket-owner-full-control")
        except ClientError:
            sentry.captureException()


@sts_client("s3", service_type="client")
def delete(bucket_name, prefix, **kwargs):
    """
    Use STS to delete an object
    """
    try:
        response = kwargs["client"].delete_object(Bucket=bucket_name, Key=prefix)
        current_app.logger.debug(f"Delete data from S3."
                                 f"Bucket: {bucket_name},"
                                 f"Prefix: {prefix},"
                                 f"Status_code: {response}")
        return response['ResponseMetadata']['HTTPStatusCode'] < 300
    except ClientError:
        sentry.captureException()


@sts_client("s3", service_type="client")
def get(bucket_name, prefix, **kwargs):
    """
    Use STS to get an object
    """
    try:
        response = kwargs["client"].get_object(Bucket=bucket_name, Key=prefix)
        current_app.logger.debug(f"Get data from S3. Bucket: {bucket_name},"
                                 f"Prefix: {prefix}")
        return response['Body'].read().decode("utf-8")
    except ClientError:
        sentry.captureException()

import boto3
import botocore
import datetime
import warnings

from pytz import timezone


class S3Log(object):

    @classmethod
    def create(cls, row):
        splited = row.split("\t")
        if len(splited) < 6:
            return
        s = cls()
        s.time = datetime.datetime.strptime(splited[0].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")
        s.ip = splited[1]
        s.label = splited[3]
        s.log_type = splited[4]
        s.data = "\t".join(splited[5:])
        return s


def get_prefix_list(time_begin, time_end, hourly_template):
    prefix_time = datetime.datetime(
        time_begin.year, time_begin.month, time_begin.day, time_begin.hour)
    while prefix_time < time_end:
        yield prefix_time.strftime(hourly_template)
        prefix_time += datetime.timedelta(seconds=3600)


def get_key_list(client, bucket, prefix, time_begin):
    tz = timezone('Asia/Shanghai')
    resp = client.list_objects(Bucket=bucket, Prefix=prefix)
    if "Contents" not in resp:
        warnings.warn("%s not found" % prefix)
        return

    for obj in resp["Contents"]:
        if obj["LastModified"] >= tz.localize(time_begin):
            yield obj["Key"]


def read_log_by_prefix(client, bucket, prefix, time_begin):
    for key in get_key_list(client, bucket, prefix, time_begin):
        obj = client.get_object(Bucket=bucket, Key=key)
        for row in obj["Body"].read().split("\n"):
            sys_log = S3Log.create(row)
            yield sys_log


def read_log(time_begin, time_end, bucket, hourly_folder_path_template, access_key_id,
        secret_access_key, region_name):
    ''' 从 s3 读 log。需要传入账户信息，起止时间和小时级文件夹路径模板。
    如果文件夹内的 log 时间与文件夹名是相符的，则输出保证是按时间排序的。
    模板样例："track_log/dt=%Y-%m-%d/hr=%H/" '''

    client = boto3.client(
        "s3", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
        config=botocore.client.Config(region_name=region_name))

    for prefix in get_prefix_list(time_begin, time_end, hourly_folder_path_template):
        for log_time, s3_log in sorted((s.time, s) for s in read_log_by_prefix(
                client, bucket, prefix, time_begin) if s and time_begin <= s.time < time_end):
            yield s3_log

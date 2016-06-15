## Sample

```python

import datetime
import s3_log


if __name__ == "__main__":
    log_iter = s3_log.read_log(
        time_begin=datetime.datetime(2016, 6, 12, 15, 30),
        time_end=datetime.datetime(2016, 6, 12, 15, 40),
        bucket="log_bucket",
        hourly_folder_path_template="track_log/dt=%Y-%m-%d/hr=%H/",
        access_key_id="ABCDEFG",
        secret_access_key="1234567",
        region_name="cn-north-1")

    for row in log_iter:
        print row.data
```

import sys
import os
import datetime
import boto3
from botocore.exceptions import ClientError

## helper methods
def create_bucket(s3, bucket_name):
    # Create bucket
    try:
        print("Bucket doesn't exist yet. Creating new bucket..")
        my_region = boto3.session.Session().region_name
        if my_region != None:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": my_region})
        else:
            s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        return False
    return True

def key_exists(s3, bucket_name, key):
    try:
        s3.Object(bucket_name, key).load()
    except ClientError as e:
        return False
    return True

# Retrieve arguments
try:
    dir_name = sys.argv[1] 
    raw_dir_name = r'{}'.format(dir_name).strip() 
    raw_dir_name = os.path.normpath(raw_dir_name)
    bucket_name, aws_dir = sys.argv[2].split("::") # bucket name and remote directory name
except IndexError as e:
    print("Invalid or missing arguments. Aborting execution..")
    exit()

# Terminate if the local directory does not exist
if not os.path.exists(raw_dir_name):
    print("Specified local directory to backup does not exist. Aborting execution..")
    exit()

# Create bucket if it doesn't exist
s3 = boto3.resource("s3")
found_bucket = False

for bucket in s3.buckets.all():
    if (bucket.name == bucket_name):
        found_bucket = True

if found_bucket: 
    print("Found the bucket..")
else:
    created = create_bucket(s3, bucket_name)
    if not created:
        print("Illegal or already existing bucket name. Please choose another one. Aborting execution..")
        exit()

print("Backing up local files to the cloud..")

# Traverse the directory
for root, d_names, f_names in os.walk(raw_dir_name):
    #dir_names = [n for n in d_names]
    file_names = [n for n in f_names]
    for file_name in file_names:
        full_path = os.path.join(root, file_name)
        aws_file_name = aws_dir + root.replace(raw_dir_name, "") + os.sep + file_name

        # upload the file if the file does not exist
        if not key_exists(s3, bucket_name, aws_file_name):
            print("Backing up:", full_path)
            s3.Object(bucket_name, aws_file_name).put(Body=open(full_path, "rb"))

        # else check if the local file has been modified since last backup
        else:
            local_last_mod = os.path.getmtime(full_path)
            local_last_mod_utc = datetime.datetime.utcfromtimestamp(local_last_mod).replace(tzinfo=datetime.timezone.utc)

            object = s3.Object(bucket_name, aws_file_name)
            aws_last_mod_utc = object.last_modified
            
            # if local file's last modified timestamp is later than the last modified timestamp on the cloud, 
            # the file has been modified and we want to upload again
            if aws_last_mod_utc < local_last_mod_utc:
                # upload
                print("Backing up:", full_path)
                s3.Object(bucket_name, aws_file_name).put(Body=open(full_path, "rb"))

print("Back up complete!")

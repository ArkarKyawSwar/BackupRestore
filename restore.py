import sys
import os
import boto3
from botocore.exceptions import ClientError

## helper methods
def create_directories(dir_arr): #offset is 0 if the path is a directory, 1 if the file name is included at the end of the path
    # create the directory structure if the specified directory from the cloud doesn't exist locally
    dir = dir_arr[0] 
    i = 1
    while os.path.exists(dir) and i < len(dir_arr):
        dir += os.sep + dir_arr[i]
        i += 1

    if os.path.exists(dir):
        return

    while i <= len(dir_arr):
        os.mkdir(dir)
        if i >= len(dir_arr):
            break
        dir += os.sep + dir_arr[i]
        i += 1

# Retrieve arguments
try:
    dir_name = sys.argv[2] 
    raw_dir_name = r'{}'.format(dir_name).strip() 
    raw_dir_name = os.path.normpath(raw_dir_name)
    bucket_name, aws_dir = sys.argv[1].split("::") # bucket name and remote directory name
except IndexError as e:
    print("Invalid or missing arguments. Aborting execution..")
    exit()

# Create the local base directory if it doesn't exist
if not os.path.exists(raw_dir_name):
    splitted_dir = raw_dir_name.split(os.sep)
    create_directories(splitted_dir)

s3 = boto3.resource("s3")
bucket = s3.Bucket(bucket_name)
restore_count = 0
# download files
try:
    for object in bucket.objects.all():
        if not object.key.startswith(aws_dir + os.sep): # only restore the specified directory
            continue 
        file_path = object.key.split(aws_dir)
        file_dir = file_path[-1].split(os.sep)[:-1]
        file_name = file_path[-1].split(os.sep)[-1]

        # create directories if they don't exist
        if not os.path.exists(raw_dir_name + file_path[-1]):
            dir = raw_dir_name.split(os.sep) + file_dir
            create_directories(dir)

        # download
        print("Restoring:", object.key)
        s3.Bucket(bucket_name).download_file(object.key, raw_dir_name + file_path[-1])
        restore_count += 1

except ClientError as e:
    print("Specified bucket/directory does not exist on the cloud. Please make sure the bucket/directory is correct. Aborting execution..")
    exit()

if restore_count == 0:
    print("Specified directory does not exist on the cloud. Please make sure the directory input is correct.")
else:
    print("Restoration complete!")




<<comment

-> Run backup using "python backup.py <local-directory-name> <bucket-name>::<remote-directory-name>"

-> Run restore using "python restore.py <bucket-name>::<remote-directory-name> <local-directory-name>"


Important notes:
- Computer's Python must have boto3 package installed
- Computer must have aws credentials configured in the .aws file
- <local-directory-name>, <bucket-name> and <remote-directory-name> must not have spaces in them
- <local-directory-name> and <remote-directory-name> must not have trailing backslashes or forwardshlashes such as 'C:\Users\ArkarKSwar\Desktop\'(incorrect) instead of 'C:\Users\ArkarKSwar\Desktop'




comment
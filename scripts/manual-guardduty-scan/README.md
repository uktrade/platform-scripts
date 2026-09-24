# Manual GuardDuty Scan

## Purpose

This script will send all unscanned objects in an S3 bucket with GuardDuty malware protection enabled to be scanned by GuardDuty. Use it whenever a team enables GuardDuty on a bucket with existing objects in.

## How to Use

Login to AWS with

```
aws sso login
```

Export the profile of the account you want to run this script in

```
export AWS_PROFILE=<aws-sso-profile>
```

Run the script from root with

```
./scripts/manual-guardduty-scan/main.py
```
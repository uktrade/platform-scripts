#!/usr/bin/env -S uv run --quiet

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "boto3>=1.43.101",
#     "boto3-stubs[guardduty,s3]>=1.43.101",
#     "mypy>=2.3.1",
# ]
# ///
from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field

import boto3
from mypy_boto3_guardduty.client import GuardDutyClient
from mypy_boto3_s3.client import S3Client

SCAN_STATUS_TAG: str = "GuardDutyMalwareScanStatus"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@dataclass
class BucketObjects:
    needs_scan: list[str] = field(default_factory=list)
    already_scanned: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.needs_scan) + len(self.already_scanned)


def get_guardduty_client() -> GuardDutyClient:
    return boto3.client("guardduty")


def get_s3_client() -> S3Client:
    return boto3.client("s3")


def get_malware_protection_plan_ids(
    guardduty_client: GuardDutyClient,
) -> list[str]:
    response: dict = guardduty_client.list_malware_protection_plans()
    plans = [
        id["MalwareProtectionPlanId"] for id in response.get("MalwareProtectionPlans")
    ]

    logger.info(f"Found {len(plans)} GuardDuty protection plan(s).")

    return plans


def get_bucket_for_plan(
    guardduty_client: GuardDutyClient,
    plan_id: str,
) -> str:
    response: dict = guardduty_client.get_malware_protection_plan(
        MalwareProtectionPlanId=plan_id,
    )

    return response["ProtectedResource"]["S3Bucket"]["BucketName"]


def get_protected_buckets(
    guardduty_client: GuardDutyClient,
) -> set[str]:
    buckets: set[str] = set()

    for plan_id in get_malware_protection_plan_ids(guardduty_client):
        buckets.add(
            get_bucket_for_plan(
                guardduty_client,
                plan_id,
            )
        )

    logger.info(
        f"The following {len(buckets)} bucket(s) have protection plans: {', '.join(buckets)}"
    )

    return buckets


def list_object_keys(
    s3_client: S3Client,
    bucket_name: str,
) -> Iterator[str]:
    paginator = s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def get_object_tags(
    s3_client: S3Client,
    bucket_name: str,
    key: str,
) -> dict[str, str]:
    response: dict = s3_client.get_object_tagging(
        Bucket=bucket_name,
        Key=key,
    )

    return {tag["Key"]: tag["Value"] for tag in response.get("TagSet", [])}


def needs_scan(
    s3_client: S3Client,
    bucket_name: str,
    key: str,
) -> bool:
    tags: dict[str, str] = get_object_tags(
        s3_client,
        bucket_name,
        key,
    )

    return not any(key == SCAN_STATUS_TAG for key in list(tags.keys()))


def submit_scan(
    guardduty_client: GuardDutyClient,
    bucket_name: str,
    key: str,
) -> None:
    guardduty_client.send_object_malware_scan(
        S3Object={
            "Bucket": bucket_name,
            "Key": key,
        }
    )


def categorise_objects(s3_client: S3Client, bucket_name: str) -> BucketObjects:
    objects = BucketObjects()

    for key in list_object_keys(
        s3_client,
        bucket_name,
    ):
        if needs_scan(
            s3_client,
            bucket_name,
            key,
        ):
            objects.needs_scan.append(key)
        else:
            objects.already_scanned.append(key)

    return objects


def process_bucket(
    guardduty_client: GuardDutyClient,
    s3_client: S3Client,
    bucket_name: str,
) -> int:
    objects = categorise_objects(s3_client, bucket_name)

    logger.info(f"({bucket_name}) Found a total of {objects.total} object(s).")
    logger.info(
        f"({bucket_name}) {len(objects.already_scanned)} object(s) have already been scanned."
    )

    scan_count = 0
    if len(objects.needs_scan) == 0:
        logger.info(
            f"({bucket_name}) No objects need scanning. Skipping GuardDuty scan step."
        )
        return scan_count
    else:
        logger.info(
            f"({bucket_name}) {len(objects.needs_scan)} object(s) need to be scanned. Sending to GuardDuty to be scanned."
        )

    for object_key in objects.needs_scan:
        submit_scan(
            guardduty_client,
            bucket_name,
            object_key,
        )
        scan_count += 1

    logger.info(f"({bucket_name}) Successfully scanned {scan_count} objects.")

    return scan_count


def main() -> None:
    guardduty_client: GuardDutyClient = get_guardduty_client()
    s3_client: S3Client = get_s3_client()

    total_scanned = 0

    for bucket_name in get_protected_buckets(
        guardduty_client,
    ):
        logger.info(f"Scanning bucket: {bucket_name}")
        total_scanned += process_bucket(
            guardduty_client,
            s3_client,
            bucket_name,
        )

    logger.info(
        f"Submitted malware scans for {total_scanned} object(s) across all buckets."
    )


if __name__ == "__main__":
    main()

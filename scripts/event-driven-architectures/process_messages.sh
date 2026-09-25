#!/usr/bin/env bash
export AWS_PAGER=""

if [[ ! -f .env ]]; then
    echo ".env file not found, exiting script"
    exit 1
fi

source .env

source utils/check_aws_profile.sh
check_aws_profile || exit 1

source utils/check_env_variables.sh
check_env_variables "SQS_QUEUE" || exit 1

consume_message() {
    local sqs_queue=$1

    aws sqs receive-message \
        --queue-url "$sqs_queue" \
        --max-number-of-messages 1
}

delete_message () {
    local sqs_queue=$1
    local receipt_handle=$2
    aws sqs delete-message --queue-url "$sqs_queue" --receipt-handle "$receipt_handle"
}

while true; do
    echo "Consuming message"
    response=$(consume_message "$SQS_QUEUE")
    if [[ -z "$response" ]]; then
        echo "No message received; polling again"
        sleep 1
        continue
    fi

    receipt_handle=$(
        jq -r '.Messages[0].ReceiptHandle' <<< "$response"
    )

    message=$(
        jq -r '
            .Messages[0].Body as $body
            | try ($body | fromjson) catch $body
        ' <<< "$response"
    )

    echo "Processing message: $message"

    echo "Deleting message with receipt handle: $receipt_handle"
    delete_message "$SQS_QUEUE" "$receipt_handle"
done
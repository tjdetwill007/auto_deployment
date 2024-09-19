resource "aws_sqs_queue" "coe_queue" {
  content_based_deduplication       = false
    delay_seconds                     = 0
    fifo_queue                        = false
    kms_data_key_reuse_period_seconds = 300
    max_message_size                  = 262144
    message_retention_seconds         = 345600
    name                              = var.queue_name
    policy = jsonencode(
    {
      Id        = "__default_policy_ID"
      Statement = [
        {
          Action    = "SQS:*"
          Effect    = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
          }
          Resource  = "arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.queue_name}"
          Sid       = "__owner_statement"
        },
      ]
      Version   = "2012-10-17"
    }
  )

    receive_wait_time_seconds         = 0
    sqs_managed_sse_enabled           = true
    visibility_timeout_seconds        = 300
}
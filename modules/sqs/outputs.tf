output "sqs_queue_url" {
  value = aws_sqs_queue.coe_queue.id
}

output "sqs_arn" {
  value = aws_sqs_queue.coe_queue.arn
}
output "api_url" {
  description = "websocket invoke url"
  value = aws_apigatewayv2_stage.websocket_stage.invoke_url
}
output "api_id" {
  value = aws_apigatewayv2_api.websocket_api.id
}
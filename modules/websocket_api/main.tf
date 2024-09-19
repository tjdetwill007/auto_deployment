resource "aws_apigatewayv2_api" "websocket_api" {
  name           = var.websocket_name
  protocol_type  = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  for_each = local.lambda_arn
  api_id = aws_apigatewayv2_api.websocket_api.id
  connection_type = "INTERNET"
  content_handling_strategy = "CONVERT_TO_TEXT"
  integration_method = "POST"
  integration_type = "AWS_PROXY"
  integration_uri = each.value.invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_integration" "disconnect_mock" {
  api_id           = aws_apigatewayv2_api.websocket_api.id
  integration_type = "MOCK"
}

resource "aws_apigatewayv2_route" "connect_route" {
  for_each = local.lambda_arn
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = each.value.route_key
  route_response_selection_expression = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration["${each.key}"].id}"
}

resource "aws_apigatewayv2_route" "disconnect_route" {
  api_id    = aws_apigatewayv2_api.websocket_api.id
  route_key = "$disconnect"
  route_response_selection_expression = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect_mock.id}"
}
resource "aws_apigatewayv2_route_response" "websocket_response" {
  for_each = local.lambda_arn
  api_id             = aws_apigatewayv2_api.websocket_api.id
  route_id           = aws_apigatewayv2_route.connect_route["${each.key}"].id
  route_response_key = "$default"
}
resource "aws_apigatewayv2_deployment" "websocket_deployment" {
  api_id = aws_apigatewayv2_api.websocket_api.id

  depends_on = [
    aws_apigatewayv2_route.connect_route,
    aws_apigatewayv2_route.disconnect_route
  ]
}

resource "aws_apigatewayv2_stage" "websocket_stage" {
  api_id      = aws_apigatewayv2_api.websocket_api.id
  name        = var.stage_name
  deployment_id = aws_apigatewayv2_deployment.websocket_deployment.id
}




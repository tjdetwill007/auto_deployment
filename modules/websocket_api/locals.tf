locals {
  lambda_arn={
    connect={
        invoke_arn = var.connect
        route_key= "$connect"
    }
    addqueue={invoke_arn = var.addqueue
    route_key = "addqueue"
    }
    getpresignedurl={invoke_arn = var.getpresignedurl
    route_key = "getpresignedurl" 
    }
  }
}
output "namespace" {
  value       = kubernetes_namespace.main.metadata[0].name
  description = "The namespace where all resources are deployed"
}

output "api_endpoint" {
  value       = "http://localhost:30080"
  description = "API service endpoint (NodePort on Minikube)"
}

output "minikube_status_command" {
  value       = "minikube status"
  description = "Command to check Minikube status"
}

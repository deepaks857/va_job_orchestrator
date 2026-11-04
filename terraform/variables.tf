variable "kube_config_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "va-job-orchestrator"
}

variable "api_replicas" {
  description = "Number of API pod replicas"
  type        = number
  default     = 2
}

variable "worker_replicas" {
  description = "Number of worker pod replicas"
  type        = number
  default     = 2
}

variable "api_image" {
  description = "API Docker image"
  type        = string
  default     = "va-job-orchestrator-api:latest"
}

variable "worker_image" {
  description = "Worker Docker image"
  type        = string
  default     = "va-job-orchestrator-worker:latest"
}

variable "minikube_cpus" {
  description = "Minikube CPU count"
  type        = number
  default     = 4
}

variable "minikube_memory" {
  description = "Minikube memory in MB"
  type        = number
  default     = 8192
}

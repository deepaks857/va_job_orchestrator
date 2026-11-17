resource "null_resource" "ensure_minikube" {
  provisioner "local-exec" {
    command = "minikube status || minikube start --cpus=${var.minikube_cpus} --memory=${var.minikube_memory}mb"
    # interpreter = ["powershell", "-Command"]
  }
}

resource "kubernetes_namespace" "main" {
  metadata {
    name = var.namespace
  }

  depends_on = [null_resource.ensure_minikube]
}

resource "kubernetes_config_map" "va_config" {
  metadata {
    name      = "va-config"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  data = {
    MONGODB_URI = "mongodb://mongodb:27017"
    MONGODB_DB  = "va_jobs"
    REDIS_URI   = "redis://redis:6379/0"
  }
}

resource "kubernetes_persistent_volume_claim" "mongo_data" {
  metadata {
    name      = "mongo-data"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

resource "kubernetes_stateful_set" "mongodb" {
  metadata {
    name      = "mongodb"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    service_name = "mongodb"
    replicas     = 1
    selector {
      match_labels = {
        app = "mongodb"
      }
    }
    template {
      metadata {
        labels = {
          app = "mongodb"
        }
      }
      spec {
        container {
          name  = "mongodb"
          image = "mongo:7"
          port {
            container_port = 27017
          }
          volume_mount {
            name       = "mongo-data"
            mount_path = "/data/db"
          }
        }
      }
    }
    volume_claim_template {
      metadata {
        name = "mongo-data"
      }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "1Gi"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "mongodb" {
  metadata {
    name      = "mongodb"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    selector = {
      app = "mongodb"
    }
    port {
      port        = 27017
      target_port = 27017
    }
  }
}

resource "kubernetes_deployment" "redis" {
  metadata {
    name      = "redis"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "redis"
      }
    }
    template {
      metadata {
        labels = {
          app = "redis"
        }
      }
      spec {
        container {
          name  = "redis"
          image = "redis:7-alpine"
          port {
            container_port = 6379
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "redis" {
  metadata {
    name      = "redis"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    selector = {
      app = "redis"
    }
    port {
      port        = 6379
      target_port = 6379
    }
  }
}

resource "kubernetes_deployment" "api" {
  metadata {
    name      = "api"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    replicas = var.api_replicas
    selector {
      match_labels = {
        app = "api"
      }
    }
    template {
      metadata {
        labels = {
          app = "api"
        }
      }
      spec {
        container {
          name  = "api"
          image = var.api_image
          image_pull_policy = "Never"
          port {
            container_port = 8000
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.va_config.metadata[0].name
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "api" {
  metadata {
    name      = "api"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    type = "NodePort"
    selector = {
      app = "api"
    }
    port {
      port        = 8000
      target_port = 8000
      node_port   = 30080
    }
  }
}

resource "kubernetes_deployment" "worker" {
  metadata {
    name      = "worker"
    namespace = kubernetes_namespace.main.metadata[0].name
  }
  spec {
    replicas = var.worker_replicas
    selector {
      match_labels = {
        app = "worker"
      }
    }
    template {
      metadata {
        labels = {
          app = "worker"
        }
      }
      spec {
        container {
          name  = "worker"
          image = var.worker_image
          image_pull_policy = "Never"
          env_from {
            config_map_ref {
              name = kubernetes_config_map.va_config.metadata[0].name
            }
          }
        }
      }
    }
  }
}

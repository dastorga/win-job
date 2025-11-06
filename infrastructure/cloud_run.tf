# Secret Manager secrets
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "random_password" "jwt_secret" {
  length = 32
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

# Cloud Run service for backend
resource "google_cloud_run_service" "backend" {
  name     = "devops-jobs-backend"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.app_service_account.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/devops-jobs/backend:latest"

        ports {
          container_port = 8000
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database_instance.main.connection_name}/${google_sql_database.database.name}"
        }

        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"      = "0"
        "autoscaling.knative.dev/maxScale"      = "10"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run service for frontend
resource "google_cloud_run_service" "frontend" {
  name     = "devops-jobs-frontend"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.app_service_account.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/devops-jobs/frontend:latest"

        ports {
          container_port = 80
        }

        env {
          name  = "REACT_APP_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis]
}

# IAM policy for frontend (public web access needed)
resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM policy for backend - more restrictive (only authenticated users)
resource "google_cloud_run_service_iam_member" "backend_restricted" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allAuthenticatedUsers"
}

# Allow frontend to access backend
resource "google_cloud_run_service_iam_member" "frontend_to_backend" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.app_service_account.email}"
}

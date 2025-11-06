# Enable Cloud Resource Manager API first (required for managing other APIs)
resource "google_project_service" "resource_manager" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Enable Service Usage API (required for managing other APIs)
resource "google_project_service" "service_usage" {
  project = var.project_id
  service = "serviceusage.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false

  depends_on = [google_project_service.resource_manager]
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "storage-component.googleapis.com",
    "storage.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_dependent_services = false
  disable_on_destroy         = false

  depends_on = [
    google_project_service.resource_manager,
    google_project_service.service_usage
  ]
}

# Cloud SQL Instance
resource "google_sql_database_instance" "main" {
  name             = "devops-jobs-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  deletion_protection = false

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Database
resource "google_sql_database" "database" {
  name     = "devops_jobs"
  instance = google_sql_database_instance.main.name
}

# Database user
resource "google_sql_user" "user" {
  name     = "app_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length = 16
}

# Cloud Storage bucket for static assets
resource "google_storage_bucket" "static_assets" {
  name     = "${var.project_id}-devops-jobs-static"
  location = var.region

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "devops-jobs"
  description   = "Docker repository for DevOps Jobs application"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}

# Service Account for application
resource "google_service_account" "app_service_account" {
  account_id   = "devops-jobs-app"
  display_name = "DevOps Jobs Application Service Account"
  description  = "Service account for DevOps Jobs application services"
}

# IAM roles for the service account
resource "google_project_iam_member" "app_service_account_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectViewer",
    "roles/secretmanager.secretAccessor"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

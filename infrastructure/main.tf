# DevOps Job Scraper Infrastructure - GCP Deployment
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "win-job-terraform-state-bucket"
    prefix = "devops-job-scraper"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "win-job-devops-scraper"
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "southamerica-east1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "southamerica-east1-a"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

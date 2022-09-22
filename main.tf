locals {
  project = "madproject-201813"
}

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
  backend "gcs" {
    bucket  = "cambridge-accommodation"
    prefix  = "accommodations"
  }
}

provider "google" {
  project = local.project
  region  = "europe-west2"
}

data "google_cloudfunctions_function" "scrapper" {
  name = "accommodation-scrapper"
}

resource "google_cloud_scheduler_job" "timer" {
  name             = "accommodation-invoker"
  description      = "Triggers accommodation scrapper once an hour"
  schedule         = "*/30 * * * *"
  attempt_deadline = format("%ds", data.google_cloudfunctions_function.scrapper.timeout)

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "GET"
    uri         = data.google_cloudfunctions_function.scrapper.https_trigger_url

    oidc_token {
      service_account_email = google_service_account.function_invoker.email
    }
  }
}

resource "google_service_account" "function_invoker" {
  account_id   = "function-invoker"
  display_name = "Function Invoker"
  description  = "Service account to invoke functions"
}

resource "google_project_iam_binding" "function_invoker_role" {
  project = local.project
  role    = "roles/cloudfunctions.invoker"

  members = [
    format("serviceAccount:%s", google_service_account.function_invoker.email),
  ]
}

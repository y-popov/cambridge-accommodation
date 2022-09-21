terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  backend "s3" {
    endpoint                    = "storage.yandexcloud.net"
    bucket                      = "mad-bucket"
    key                         = "accommodations.tfstate"
    region                      = "ru-central1-a"
    skip_region_validation      = true
    skip_credentials_validation = true
  }
}

provider "yandex" {
  zone = "ru-central1-a"
}

data "yandex_resourcemanager_folder" "default" {
  folder_id = "b1gg9v30c1mpfe9msdcu"
}

data "yandex_function" "scrapper" {
  function_id = "d4ef3fel1s14vja0fn3k"
}

resource "yandex_iam_service_account" "function_invoker" {
  name        = "function-invoker"
  description = "Service account to invoke functions"
}

resource "yandex_resourcemanager_folder_iam_binding" "function_invoker_role" {
  folder_id = data.yandex_resourcemanager_folder.default.id
  role      = "serverless.functions.invoker"
  members   = [
        format("serviceAccount:%s", yandex_iam_service_account.function_invoker.id),
    ]
}

resource "yandex_function_trigger" "timer" {
  name        = "accommodation-invoker"
  description = "Triggers accommodation scrapper once an hour"
  timer {
    cron_expression = "0 * ? * * *"
  }
  function {
    id                 = data.yandex_function.scrapper.id
    tag                = "$latest"
    service_account_id = yandex_iam_service_account.function_invoker.id
  }
}

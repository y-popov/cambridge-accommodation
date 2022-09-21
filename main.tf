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

data "yandex_function" "scrapper" {
  function_id = "d4ef3fel1s14vja0fn3k"
}

resource "yandex_function_trigger" "timer" {
  name        = "accommodation-invoker"
  description = "Triggers accommodation scrapper once an hour"
  timer {
    cron_expression = "0 * ? * * *"
  }
  function {
    id  = data.yandex_function.scrapper.id
    tag = "$latest"
  }
}

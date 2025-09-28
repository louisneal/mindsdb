group "default" {
  targets = ["louis"]
}

variable "IMAGE" {
  default = "mindsdb"
}

variable "VERSION" {
  default = "1.0.1"
}

variable "PLATFORMS" {
  default = "linux/amd64,linux/arm64"
}

variable "PLATFORM_LIST" {
  default = split(",", PLATFORMS)
}

function "get_tags" {
  params = [image]
  result = [
    "louis/${IMAGE}:${VERSION}"
  ]
}

target "louis" {
  dockerfile = "docker/louis-mindsdb.Dockerfile"
  platforms  = PLATFORM_LIST
  tags       = get_tags("louis")
  args = {
    EXTRAS = ".[lightwood,huggingface,mssql,clickhouse,s3,oracle,hive] transformers"
  }
  output = ["type=docker"]
}
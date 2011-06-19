BROKER_BACKEND = "redis"

BROKER_HOST = "localhost"
BROKER_PORT = 6379 #redis
BROKER_VHOST = "0"

CELERY_IMPORTS = ("message.tasks", )

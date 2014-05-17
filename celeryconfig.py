import os
import sys
sys.path.insert(0, os.getcwd())

BROKER_URL = "redis://192.168.10.6:6379/11"
CELERY_IMPORTS = ("tasks", )
CELERY_RESULT_BACKEND = "redis://192.168.10.6:6379/12"
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TASK_RESULT_EXPIRES = 1*60

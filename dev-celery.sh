#!/bin/sh
exec celery worker -A luohua.tasks.celery --loglevel=INFO

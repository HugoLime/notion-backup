#!/bin/bash
# script to execute notion-backup in docker
# with cronjob or prebackup script

set -eux
dir="$(dirname $(readlink -f $0))"
cd $dir
if [ -t 0 ] ; then
  tty=""
else
  tty="-T"
fi

rm -f exports/*
docker-compose run ${tty} notion_backup

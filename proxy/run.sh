#!/bin/sh

# fail the script if any of the subsequent commands fails
set -e

# substitutes all env variables with values
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
# run the nginx as the foreground process
nginx -g 'daemon off;'

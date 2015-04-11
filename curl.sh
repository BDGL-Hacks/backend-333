#!/bin/bash
curl -X POST -b cookies -c cookies -d $1 Linode-work:8000$2 


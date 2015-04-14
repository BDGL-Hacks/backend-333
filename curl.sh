#!/bin/bash
curl -X POST -b cookies -c cookies -d $1 linode:8000$2 


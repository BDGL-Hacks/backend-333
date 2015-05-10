#!/bin/bash
curl -X POST -b cookies -c cookies -d $1 http://10.9.145.199:8000$2 


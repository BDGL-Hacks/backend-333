#!/bin/bash
curl -X POST -b cookies -c cookies -d $1 http://10.8.7.149:8000$2 


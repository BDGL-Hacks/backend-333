#!/bin/bash
curl -X POST -b cookies -c cookies -d $1 localhost:8000$2 


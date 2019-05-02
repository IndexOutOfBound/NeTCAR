#!/bin/bash

. ./unimelb-comp90024-group-61-openrc.sh < OpenStack_API_key.text; ansible-playbook --fork 1 -u ubuntu --ask-become-pass nectar.yaml 
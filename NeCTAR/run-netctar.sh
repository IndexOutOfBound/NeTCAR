#!/bin/bash

. ./unimelb-comp90024-group-61-openrc.sh; ansible-playbook --fork 1 -u ubuntu --ask-become-pass nectar.yaml 
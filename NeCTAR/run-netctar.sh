#!/bin/bash

. ./unimelb-comp90024-group-61-openrc.sh; ansible-playbook -i hosts -u ubuntu --ask-become-pass nectar.yaml

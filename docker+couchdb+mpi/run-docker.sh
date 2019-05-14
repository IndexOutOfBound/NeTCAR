#!/bin/bash

#used for first time
. ./unimelb-comp90024-group-61-openrc.sh < OpenStack_API_key.text; ansible-playbook -u ubuntu --ask-become-pass deploy.yaml


# . ./unimelb-comp90024-group-61-openrc.sh < OpenStack_API_key.text; ansible-playbook -u ubuntu --ask-become-pass docker.yaml

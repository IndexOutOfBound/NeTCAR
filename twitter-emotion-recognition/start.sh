#!/bin/bash
cd ~/mpi_data_share/twitter-emotion-recognition 
mpirun -np 4 --mca btl_tcp_if_include eth0 -hostfile hostfile python3 twitterharvest_py3.py 500000_

#!/bin/bash

HERE=$(pwd)

time python /IPLlinux/raid0/homes/jforbes/git/BRAINSStandAlone/AutoWorkup/BRAINSTools/ants/btp_exp.py \
   -ExperimentConfig ${1} \
   -pe OSX_ENVIRONMENT \
   -wfrun ${2}
#-wfrun local

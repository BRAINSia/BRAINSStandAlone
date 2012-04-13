#!/bin/bash

FIXED_T1=$1
FIXED_T2=$2
MOVING_T1=$3
MOVING_T2=$4
OUT_PREFIX=$5
AffineRegistrationInput=$6

#OUTPUT_AFFINE=$5
#OUTPUT_DEFORMATION=$6


export DIM=3

   echo antsRegistration \
   -d 3  \
   -m CC[${FIXED_T1},${MOVING_T1},1,5]  \
   -m CC[${FIXED_T2},${MOVING_T2},1,5] \
   -t SyN[0.25,3.0,0.0] \
   -r [${AffineRegistrationInput},0] \
   -o ${OUT_PREFIX} \
   -c [70x70x20,1e-6,10] \
   -f 3x2x1 \
   -s 0x0x0 \
   -u 1

#MxNxO,<convergenceThreshold=1e-6>,<convergenceWindowSize=10
   antsRegistration \
   -d 3  \
   -m CC[${FIXED_T1},${MOVING_T1},1,5]  \
   -m CC[${FIXED_T2},${MOVING_T2},1,5] \
   -t SyN[0.25,3.0,0.0] \
   -r [${AffineRegistrationInput},0] \
   -o ${OUT_PREFIX} \
   -c [70x70x20,1e-6,10] \
   -f 3x2x1 \
   -s 0x0x0 \
   -u 1

#   -c [70x70x20,1e-6,10] \


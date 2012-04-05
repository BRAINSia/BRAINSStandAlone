#!/bin/bash

if [ -d /scratch/PREDICT/johnsonhj/src/ANTS-gcc44/Examples ] ;then
  export ANTSPATH=/scratch/PREDICT/johnsonhj/src/ANTS-gcc44/Examples/
fi
if [ -d /ipldev/scratch/johnsonhj/src/ANTS-Darwin-build/Examples ];then
  export ANTSPATH=/ipldev/scratch/johnsonhj/src/ANTS-Darwin-build/Examples
fi

AFFINE_TRANSFORM=$1
DEFORMATION_FIELD=$2
REFERENCE_IMAGE=$3
MOVING_IMAGE=$4
OUTPUT_IMAGE=$5

#OUTPUT_AFFINE=$5
#OUTPUT_DEFORMATION=$6


export DIM=3

${ANTSPATH}/WarpImageMultiTransform \
    $DIM \
    ${MOVING_IMAGE} \
    ${OUTPUT_IMAGE} \
    ${DEFORMATION_FIELD} \
    ${AFFINE_TRANSFORM} \
   -R ${REFERENCE_IMAGE}


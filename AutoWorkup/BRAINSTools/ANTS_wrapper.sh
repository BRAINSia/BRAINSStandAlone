#!/bin/bash

if [ -d /scratch/PREDICT/johnsonhj/src/ANTS-gcc44/Examples ] ;then
  export ANTSPATH=/scratch/PREDICT/johnsonhj/src/ANTS-gcc44/Examples/
fi
if [ -d /ipldev/scratch/johnsonhj/src/ANTS-Darwin-build/Examples ];then
  export ANTSPATH=/ipldev/scratch/johnsonhj/src/ANTS-Darwin-build/Examples
fi


FIXED_T1=$1
FIXED_T2=$2
MOVING_T1=$3
MOVING_T2=$4
OUT_PREFIX=$5

#OUTPUT_AFFINE=$5
#OUTPUT_DEFORMATION=$6


export DIM=3

#if [ 0 -eq 1 ] ;then
#${ANTSPATH}/ANTS ${DIM}  \
#   -m  CC[${FIXED_T1},${MOVING_T1},1,5]  \
#   -m  CC[${FIXED_T2},${MOVING_T2},1,5] \
#   -t SyN[0.25] \
#   -r Gauss[3,0] \
#   -o ${OUT_PREFIX} \
#   -i 5x7x2 \
#   --use-Histogram-Matching  \
#   --number-of-affine-iterations 10x10x10x10x10 \
#   --MI-option 32x16000
#fi

if [ 1 -eq 1 ] ;then
${ANTSPATH}/ANTS ${DIM}  \
   -m  CC[${FIXED_T1},${MOVING_T1},1,5]  \
   -m  CC[${FIXED_T2},${MOVING_T2},1,5] \
   -t SyN[0.25] \
   -r Gauss[3,0] \
   -o ${OUT_PREFIX} \
   -i 50x70x20 \
   --use-Histogram-Matching  \
   --number-of-affine-iterations 10000x10000x10000x10000x10000 \
   --MI-option 32x16000
fi

#  ${ANTSPATH}/ANTS \
#     $DIM  \
#     -m  ${METRIC}${TMPDIR_FIXED//T1/T2},${TMPDIR_MOVING//T1/T2},${METRICPARAMS}  \
#     -m  ${METRIC}${TMPDIR_FIXED},${TMPDIR_MOVING},${METRICPARAMS} \
#     -t $TRANSFORMATION \
#     -r $REGULARIZATION \
#     -o ${OUT_PREFIX} \
#     -i $MAXITERATIONS \
#     --use-Histogram-Matching  \
#     --number-of-affine-iterations 10000x10000x10000x10000x10000 \
#     --MI-option 32x16000


#  ${ANTSPATH}/WarpImageMultiTransform \
#      $DIM \
#      ${MOVING_T1} \
#      ${OUT_PREFIX}deformed.nii.gz \
#      ${OUT_PREFIX}Warp.nii.gz \
#      ${OUT_PREFIX}Affine.txt \
#     -R ${FIXED_T1}




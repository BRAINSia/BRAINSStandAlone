#!/bin/bash
# \author Hans J. Johnson
# http://surfer.nmr.mgh.harvard.edu/fswiki/MEF
# The idea is to apply the Linear Discriminant Analysis (LDA) technique in
# order to find a optimal set of weights (a projection vector) such that
# the weighted averge volume has the best contrast-to-noise ratio between
# a pair of tissue classes (usually between WM and GM).

BABC_TissueMask=$1
BABC_T1_average=$2
BABC_T2_average=$3
OUTPUT_SYNTHESIZED_IMAGE=$4

WM_LABEL=1
GM_LABEL=2
WeightsFile=ThisSubjectOptimalWeights.txt

## This call has an output of the weights file, and is used in imperically estimate the best weights
## --weight is an OUTPUT in this case
mri_ms_LDA \
  -lda ${WM_LABEL} ${GM_LABEL} \
  -label ${BABC_TissueMask} \
  -weight ${WeightsFile} \
  ${BABC_T1_average} \
  ${BABC_T2_average}

# where "-lda 2 3" indicates optimizing for the two tissue classes with label 2 and 3. "${BABC_TissueMask}" is the manual labeling volume (maybe partially labelled) that should contain voxels with values 2 or 3. "weights.txt" is the output text file containing the computed weights. input_vol# are the MEF volumes (assumed to be already registered and have the same size as the label volume). The number of weights will equal to the number of input volumes.
# Usually, the optimal weighting can be computed from a set of training subjects, and then the optimal weights can be used to process new data.
# Suppose the weights are computed, mri_ms_LDA can be used to apply them to new MEF data as follows:


##  Use the pre-computed weights to create a synthesized output image where the two specidified classes are maximally separated
##  --weight is and INPUT in this case!
mri_ms_LDA \
  -lda ${WM_LABEL} ${GM_LABEL} \
  -weight ${WeightsFile} \
  -W \
  -synth ${OUTPUT_SYNTHESIZED_IMAGE} \
  ${BABC_T1_average} \
  ${BABC_T2_average}


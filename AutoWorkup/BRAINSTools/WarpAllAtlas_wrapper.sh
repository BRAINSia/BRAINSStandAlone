#!/bin/bash

AFFINE_TRANSFORM=$1
DEFORMATION_FIELD=$2
REFERENCE_IMAGE=$3
MOVING_DIRECTORY=$4
OUTPUT_DIRECTORY=$(dirname $5)

#OUTPUT_AFFINE=$5
#OUTPUT_DEFORMATION=$6

export DIM=3
for ref_file in $(find ${MOVING_DIRECTORY} -type f ); do
   OUTPUT_IMAGE=$(echo ${ref_file} |sed "s#${MOVING_DIRECTORY}#${OUTPUT_DIRECTORY}#g")
   if [ "${OUTPUT_IMAGE}" == "${ref_file}" ]; then
     echo "ERROR: OUTPUT IMAGE CAN NOT BE SAME AS INPUT IMAGE."
     echo "${OUTPUT_IMAGE}"
     exit -1
   fi
   mkdir -p $(dirname ${OUTPUT_IMAGE})
   echo ${ref_file} |grep ".nii.gz" > /dev/null
   if [ $? -eq 0 ]; then
     if [ ! -f ${OUTPUT_IMAGE} ]; then
       ## Warp all image files
       WarpImageMultiTransform \
          $DIM \
          ${ref_file} \
          ${OUTPUT_IMAGE} \
          ${DEFORMATION_FIELD} \
          ${AFFINE_TRANSFORM} \
         -R ${REFERENCE_IMAGE}
     else
	echo "ALREADY EXISTS: ${OUTPUT_IMAGE}"
     fi
   else
     ## Just copy files that are not images
     cp ${ref_file} ${OUTPUT_IMAGE}
   fi
done

exit 0

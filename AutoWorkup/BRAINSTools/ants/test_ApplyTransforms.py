from nipype.interfaces.ants.utils import ApplyTransform


at = ApplyTransform()
at.inputs.dimension = 3
at.inputs.input_image = 'SUBJ_B_T1_resampled.nii.gz'
at.inputs.reference_image = 'SUBJ_A_T1_resampled.nii.gz'
at.inputs.interpolation = 'Linear'
at.inputs.default_value = 0
at.inputs.transformation_files = ['20120430_1348_ANTS6_1Warp.nii.gz', '20120430_1348_txfmv2fv_affine.mat']

print at.cmdline
print "--dimensionality 3    --input SUBJ_B_T1_resampled.nii.gz    --reference-image SUBJ_A_T1_resampled.nii.gz    --output antsResampleBtoA.nii.gz    --interpolation Linear    --default-value 0    --transform 20120430_1348_ANTS6_1Warp.nii.gz    --transform 20120430_1348_txfmv2fv_affine.mat"

res = at.run()

print res.outputs



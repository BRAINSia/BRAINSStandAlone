# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsApplyTransforms

test = antsApplyTransforms.AntsApplyTransforms()
test.inputs.input_file_name = '/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_B_T1_resampled.nii.gz'
test.inputs.reference_image = '/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_A_T1_resampled.nii.gz'
test.inputs.output_warped_file_name = 'antsResampleBtoA.nii.gz'
#test.inputs.print_out_composite_warp_file = 0
test.inputs.interpolation ='Linear'
test.inputs.default_value = 0
test.inputs.transforms = ['/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/20120430_1348_ANTS6_1Warp.nii.gz','/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/20120430_1348_txfmv2fv_affine.mat']
test.inputs.invert_transforms_list = [0,0]


#result = test.run()
#print result.outputs

target = "/ipldev/scratch/johnsonhj/src/ANTS-Darwin-clang/bin/antsApplyTransforms --default-value 0"
target += " --dimensionality 3 --input /hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_B_T1_resampled.nii.gz"
target += " --interpolation Linear --output antsResampleBtoA.nii.gz"
target += " --reference-image /hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_A_T1_resampled.nii.gz"
target += " --transform [/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/20120430_1348_ANTS6_1Warp.nii.gz,0]"
target += " --transform [/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/20120430_1348_txfmv2fv_affine.mat,0]"

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()

# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsRegistration

test = antsRegistration.AntsRegistration()
test.inputs.moving_image = ['/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_B_T1_resampled.nii.gz']
test.inputs.fixed_image = ['/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_A_T1_resampled.nii.gz']
test.inputs.metric = "CC"
test.inputs.fixed_image_mask = "SUBJ_A_small_T2_mask.nii.gz"
test.inputs.moving_image_mask = "SUBJ_B_small_T2_mask.nii.gz"
test.inputs.initial_fixed_transform = "20120430_1348_txfmv2fv_affine.mat"
test.inputs.transform = "SyN[0.25,3.0,0.0]"
test.inputs.n_iterations = [100, 70, 20]
test.inputs.convergence_threshold = 1e-6
test.inputs.convergence_window_size = 10
test.inputs.shrink_factors = [3,2,1]
test.inputs.smoothing_sigmas = [0,0,0]
test.inputs.use_histogram_matching = True
test.inputs.output_warped_image = True
test.inputs.output_inverted_warped_image = True


result = test.run()
print result.outputs

target = "antsRegistration --dimensionality 3 --initial-moving-transform 20120430_1348_txfmv2fv_affine.mat --metric 'CC[{0}SUBJ_A_T1_resampled.nii.gz,{0}SUBJ_B_T1_resampled.nii.gz,1,5]' --masks [SUBJ_A_small_T2_mask.nii.gz,SUBJ_B_small_T2_mask.nii.gz] --convergence [100x70x20,1e-06,10] --shrink-factors 3x2x1 --smoothing-sigmas 0x0x0 --transform SyN[0.25,3.0,0.0]".format('/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/')

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()

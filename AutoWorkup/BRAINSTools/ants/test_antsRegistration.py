# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsRegistration

test = antsRegistration.antsRegistration()
test.inputs.fixed_image = ['/Volumes/scratch/antsbuildtemplate/TEST_CACHE_3images_antsReg1/buildtemplateparallel/initAvgWF/InitAvgImages/MYtemplate.nii.gz']
test.inputs.moving_image = ['/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/02_T1_half.nii.gz']
test.inputs.metric = "CC"
test.inputs.output_transform_prefix = "MY"
#test.inputs.fixed_image_mask = "SUBJ_A_small_T2_mask.nii.gz"
#test.inputs.moving_image_mask = "SUBJ_B_small_T2_mask.nii.gz"
#test.inputs.initial_fixed_transform = "20120430_1348_txfmv2fv_affine.mat"
test.inputs.transform = ["Affine[1.0]","SyN[0.25,3.0,0.0]"]
test.inputs.number_of_iterations = [[50, 35, 15], [50, 35, 15]]
#test.inputs.convergence_threshold = 1e-6
#test.inputs.convergence_window_size = 10
test.inputs.shrink_factors = [[3,2,1],[3,2,1]]
test.inputs.smoothing_sigmas = [[0,0,0],[0,0,0]]
test.inputs.use_histogram_matching = True
#test.inputs.output_warped_image = True
#test.inputs.output_warped_image = "BtoA"
#test.inputs.output_inverse_warped_image = True

#result = test.run()
#print result.outputs

target = 'antsRegistration --dimensionality 3 --output MY --metric "CC[/Volumes/scratch/antsbuildtemplate/TEST_CACHE_3images_antsReg1/buildtemplateparallel/initAvgWF/InitAvgImages/MYtemplate.nii.gz,/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/02_T1_half.nii.gz,1,5]" --transform "Affine[1.0]" --convergence "[50x35x15,1e-06,10]" --shrink-factors 3x2x1 --smoothing-sigmas 0x0x0 --metric "CC[/Volumes/scratch/antsbuildtemplate/TEST_CACHE_3images_antsReg1/buildtemplateparallel/initAvgWF/InitAvgImages/MYtemplate.nii.gz,/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/02_T1_half.nii.gz,1,5]" --transform "SyN[0.25,3.0,0.0]" --convergence "[50x35x15,1e-06,10]" --shrink-factors 3x2x1 --smoothing-sigmas 0x0x0 --use-histogram-matching 1'

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()

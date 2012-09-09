# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import BRAINSTools.BTants.ants
import datetime
start_time = datetime.datetime.now()

print start_time

testDir = '/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST'
fixed = testDir + '/SUBJ_A_T1_resampled.nii.gz'
moving = testDir + '/SUBJ_B_T1_resampled.nii.gz'

test = ANTS()
#test.inputs.dimension = 3
#test.inputs.output_transform_prefix = 'OrigANTS_20120430_1348_ANTS6_'
#test.inputs.metric = ['CC']
#test.inputs.fixed_image = [fixed]
#test.inputs.moving_image = [moving]
#test.inputs.metric_weight = [1.0]
#test.inputs.radius = [5]
#test.inputs.affine_gradient_descent_option = [0.25]
#test.inputs.transformation_model = 'SyN'
#test.inputs.gradient_step_length = 0.25
#test.inputs.number_of_time_steps = 3.0
#test.inputs.delta_time = 0.0
#test.inputs.number_of_iterations = [1,1,1]
#test.inputs.subsampling_factors = [3,2,1]
#test.inputs.smoothing_sigmas = [0,0,0]
#test.inputs.use_histogram_matching = False
#test.inputs.mi_option = [32, 16000]
#test.inputs.regularization = 'Gauss'
#test.inputs.regularization_gradient_field_sigma = 3
#test.inputs.regularization_deformation_field_sigma = 0

test.inputs.dimension = 3
test.inputs.output_transform_prefix = 'MY'
test.inputs.metric = ['CC']
test.inputs.fixed_image = [fixed]
test.inputs.moving_image = [moving]
test.inputs.metric_weight = [1.0]
test.inputs.radius = [5]
test.inputs.transformation_model = 'SyN'
test.inputs.gradient_step_length = 0.25
test.inputs.number_of_iterations = [50, 35, 15]
test.inputs.use_histogram_matching = True
test.inputs.mi_option = [32, 16000]
test.inputs.regularization = 'Gauss'
test.inputs.regularization_gradient_field_sigma = 3
test.inputs.regularization_deformation_field_sigma = 0
test.inputs.number_of_affine_iterations = [10000,10000,10000,10000,10000]

target = 'ANTS \
3 \
--affine-gradient-descent-option 0.25x0.5x0.0001x0.0001 \
--gaussian-smoothing-sigmas 0x0x0 \
--image-metric CC[{0}/SUBJ_A_T1_resampled.nii.gz,{0}/SUBJ_B_T1_resampled.nii.gz,1,5] \
--number-of-iterations 100x70x20 \
--output-naming OrigANTS_20120430_1348_ANTS6_ \
--subsampling-factors 3x2x1 \
--transformation-model SyN[0.25,3.0,0.0] \
--use-Histogram-Matching 1 \
'.format(testDir)

print '++++++++++++++++'
print test.cmdline
print '++++++++++++++++'
#print target
#print '++++++++++++++++'
#assert test.cmdline.strip() == target.strip()


result = test.run()
print result.outputs

print "-"*50
print "The program took "
print datetime.datetime.now() - start_time

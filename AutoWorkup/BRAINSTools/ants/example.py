# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import ants

testDir = '/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST'
test = ants.ANTS()
test.inputs.dimension = 3

# test.inputs.outputNaming = 'OrigANTS_20120430_1348_ANTS6_'
# test.inputs.imageMetric = ['CC']
# test.inputs.fixedImage = [testDir+'/SUBJ_A_T1_resampled.nii.gz']
# test.inputs.movingImage = [testDir+'/SUBJ_B_T1_resampled.nii.gz']
# test.inputs.metricWeight = 1.0
# test.inputs.radius = 5
# test.inputs.transformationModel = ['Affine', 'SyN']
# test.inputs.transformationStepLength = [0.25, 0.25]
# test.inputs.transformationNumberOfTimeSteps = [3.0]
# test.inputs.transformationDeltaTime = [0.0]
# test.inputs.numberOfIterations = [100,70,20]
# test.inputs.subsamplingFactors = [3,2,1]
# test.inputs.gaussianSmoothingSigmas = [0,0,0]
# test.inputs.useHistogramMatching = False

# result = test.run()
# print result.outputs

target = 'ANTS \
3'.format(testDir) # \
# --output-naming OrigANTS_20120430_1348_ANTS6_ \
# --image-metric CC[{0}/SUBJ_A_T1_resampled.nii.gz,{0}/SUBJ_B_T1_resampled.nii.gz,1,5] \
# --transform-model Affine[0.25] \
# --transform-model SyN[0.25,3.0,0.0] \
# --number-of-iterations 100x70x20 \
# --subsampling-factors 3x2x1 \
# --gaussian-smoothing-sigmas 0x0x0 \
# --use-Histogram-Matching 1

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()

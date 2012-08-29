# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsAverageImages

imagedir = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/"

test = antsAverageImages.AntsAverageImages()
test.inputs.dimension = 3
test.inputs.output_average_image = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/average.nii.gz"
test.inputs.normalize = 1
test.inputs.images = ["{0}01_T1_half.nii.gz".format(imagedir),"{0}02_T1_half.nii.gz".format(imagedir),"{0}03_T1_half.nii.gz".format(imagedir)]

result = test.run()
print result.outputs

target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/AverageImages 3 average.nii.gz 1 {0}01_T1_half.nii.gz {0}02_T1_half.nii.gz {0}03_T1_half.nii.gz".format(imagedir)

#print test.cmdline
#print '++++++++++++++++'
#print target

#assert test.cmdline.strip() == target.strip()

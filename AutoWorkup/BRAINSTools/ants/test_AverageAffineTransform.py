# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsAverageAffineTransform

imagedir = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/"

test = antsAverageAffineTransform.AntsAverageAffineTransform()

test.inputs.dimension = 3
test.inputs.transforms = ['{0}MY01_T1_halfAffine.txt', '{0}MY02_T1_halfAffine.txt', '{0}MY03_T1_halfAffine.txt']
test.inputs.output_product_image = 'MYtemplatewarp.nii.gz'

result = test.run()
print result.outputs

target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/AverageAffineTransform 3 {0}01_T1_half.nii.gz 0.25 product2.nii.gz".format(imagedir)
#target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/AverageAffineTransform 3 {0}01_T1_half.nii.gz {0}02_T1_half.nii.gz product.nii.gz".format(imagedir)

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()
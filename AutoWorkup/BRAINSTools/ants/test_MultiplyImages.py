# from nipype import config, logging
# config.enable_debug_mode()
# logging.update_logging(config)

import antsMultiplyImages

imagedir = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/"

test = antsMultiplyImages.AntsMultiplyImages()
test.inputs.dimension = 3
test.inputs.first_input = "{0}01_T1_half.nii.gz".format(imagedir)
test.inputs.second_input = 0.25
#test.inputs.second_input = "{0}02_T1_half.nii.gz".format(imagedir)
test.inputs.output_product_image = "product2.nii.gz"

result = test.run()
print result.outputs

target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/MultiplyImages 3 {0}01_T1_half.nii.gz 0.25 product2.nii.gz".format(imagedir)
#target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/MultiplyImages 3 {0}01_T1_half.nii.gz {0}02_T1_half.nii.gz product.nii.gz".format(imagedir)

print test.cmdline
print '++++++++++++++++'
print target

assert test.cmdline.strip() == target.strip()

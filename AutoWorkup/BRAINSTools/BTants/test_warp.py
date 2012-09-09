
import BRAINSTools.BTants.antsWarp

imagedir = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/"

test = antsWarp.WarpImageMultiTransform()

test.inputs.dimension = 3
test.inputs.moving_image = '{0}MY02_T1_halfWarp.nii.gz'.format(imagedir)
test.inputs.reference_image = '{0}MY03_T1_halfdeformed.nii.gz'.format(imagedir)
test.inputs.transformation_series = ['{0}MY01_T1_halfAffine.txt'.format(imagedir), '{0}MY03_T1_halfWarp.nii.gz'.format(imagedir)]
test.inputs.invert_affine = [1]


#'{0}MY02_T1_halfAffine.txt'.format(imagedir),
#result = test.run()
#print result.outputs

#target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/AverageAffineTransform 3 {0}01_T1_half.nii.gz 0.25 product2.nii.gz".format(imagedir)
#target = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/ANTS-Darwin-clang/bin/AverageAffineTransform 3 {0}01_T1_half.nii.gz {0}02_T1_half.nii.gz product.nii.gz".format(imagedir)

print test.cmdline
print '++++++++++++++++'
#print target
#
#assert test.cmdline.strip() == target.strip()

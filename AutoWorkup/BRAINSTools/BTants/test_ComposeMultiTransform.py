
import antsComposeMultiTransform

imagedir = "/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/"

test = antsComposeMultiTransform.ComposeMultiTransform()

test.inputs.dimension = 3
#test.inputs.output_affine_txt = 'outwarp.nii'
test.inputs.reference_affine_txt = '{0}MY03_T1_halfdeformed.nii.gz'.format(imagedir)
test.inputs.transformation_series = ['{0}MY01_T1_halfAffine.txt'.format(imagedir), '{0}MY02_T1_halfAffine.txt'.format(imagedir), '{0}MY03_T1_halfWarp.nii.gz'.format(imagedir)]
test.inputs.invert_affine = [2]


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

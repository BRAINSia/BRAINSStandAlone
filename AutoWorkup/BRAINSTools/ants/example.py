import antsRegistration

test = antsRegistration.AntsRegistration()
test.inputs.moving_image = ['/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_B_T1_resampled.nii.gz']
test.inputs.fixed_image = ['/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/SUBJ_A_T1_resampled.nii.gz']
test.inputs.metric = "CC"
# test.inputs.fixed_image_masks =

target = "antsRegistration --dimensionality 3 --metric 'CC[{0}SUBJ_A_T1_resampled.nii.gz,{0}SUBJ_B_T1_resampled.nii.gz,1,5]'".format('/hjohnson/HDNI/EXPERIEMENTS/ANTS_NIPYPE_SMALL_TEST/')

# -t 'SyN[0.25,3.0,0.0]' \
#     -c '[100x70x20,1e-6,10]' \
#     -f 3x2x1 \
#     -s 0x0x0 \
#     -u 1'

print test.cmdline

print target

assert test.cmdline.strip() == target.strip()

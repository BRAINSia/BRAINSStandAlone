import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import ants
from nipype.interfaces.ants import WarpImageMultiTransform
import antsMultiplyImages

imagedir = '/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/'
images = ['{0}01_T1_half.nii.gz'.format(imagedir), '{0}02_T1_half.nii.gz'.format(imagedir), '{0}03_T1_half.nii.gz'.format(imagedir)]


#WORKFLOW: Creating overall workflow:
buildtemplateparallel = pe.Workflow(name='buildtemplateparallel')

#NODE: InitAvgImages - Average the initial images
InitAvgImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name ='InitAvgImages')
InitAvgImages.inputs.images = images
InitAvgImages.inputs.dimension = 3
InitAvgImages.inputs.output_average_image = 'MYtemplate.nii.gz'
InitAvgImages.inputs.normalize = 1
print InitAvgImages.outputs

#Create ANTSintroduction workflow:
#ANTSintroduction = pe.Workflow(name='ANTSintroduction')


#NODE: BeginANTS - produces warped, inverse warped, and affine images
BeginANTS=pe.Node(interface=ants.ANTS(), name = 'BeginANTS')
BeginANTS.inputs.dimension = 3
BeginANTS.inputs.output_transform_prefix = 'MY'
BeginANTS.inputs.metric = ['CC']
#BeginANTS.inputs.moving_image = images[0]
BeginANTS.inputs.metric_weight = [1.0]
BeginANTS.inputs.radius = [5]
BeginANTS.inputs.affine_gradient_descent_option = [0.25]
BeginANTS.inputs.transformation_model = 'SyN'
BeginANTS.inputs.gradient_step_length = 0.25
BeginANTS.inputs.number_of_time_steps = 3.0
BeginANTS.inputs.delta_time = 0.0
BeginANTS.inputs.number_of_iterations = [1, 1, 1]
BeginANTS.inputs.subsampling_factors = [3, 2, 1]
BeginANTS.inputs.smoothing_sigmas = [0, 0, 0]
BeginANTS.inputs.use_histogram_matching = False
print BeginANTS.inputs

#Introducing iterables:

#initiate the infosource node:
infosource = pe.Node( interface = util.IdentityInterface( fields = ['subject_image'] ), name = "infosource" )
#define the list of subjects your pipeline should be executed on
infosource.iterables = ( 'subject_image', images)


#NODE: wimtdeformed - Forward Warp Image Multi Transform to produce deformed images
wimtdeformed = pe.Node( interface = WarpImageMultiTransform(), name = 'wimtdeformed')
#wimtdeformed.inputs.transformation_series = [BeginANTS.outputs.warp_transform, BeginANTS.outputs.affine_transform]
wimtdeformed.inputs.moving_image = images[0]
print wimtdeformed.outputs

#NODE: AvgHlafDeformedImages -  Creates an average image of the three halfDeformed images
AvgHalfDeformedImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgHalfDeformedImages')
AvgHalfDeformedImages.inputs.dimension = 3
AvgHalfDeformedImages.inputs.output_average_image = 'MYtemplate.nii.gz'
AvgHalfDeformedImages.inputs.normalize = 1
#AvgHalfDeformedImages.inputs.images = ['MY01_T1_halfdeformed.nii.gz', 'MY02_T1_halfdeformed.nii.gz', 'MY03_T1_halfdeformed.nii.gz']

########################
##### CONNECTIONS ######
########################

##Connect InitAvgImages to BeginANTS
buildtemplateparallel.connect( InitAvgImages, "average_image", BeginANTS, "fixed_image" )
buildtemplateparallel.connect( infosource, "subject_image", BeginANTS, 'moving_image' )

#Connections to get inputs to WarpImageMultiTransform Deformed
#buildtemplateparallel.connect( BeginANTS,['warp_transform', BeginANTS.outputs.affine_transform], wimtdeformed, 'transformation_series' )

functionString = 'def func(arg1, arg2): return [arg1, arg2]'
fi = pe.Node(interface=util.Function(input_names=['arg1', 'arg2'], output_names=['out']), name='ListAppender')
fi.inputs.function_str = functionString
fi.inputs.ignore_exception = True

#buildtemplateparallel.connect([( BeginANTS,fi, [((['warp_transform', 'affine_transform']),  'out')]),])
buildtemplateparallel.connect( BeginANTS, 'warp_transform', fi, 'arg1')
buildtemplateparallel.connect( BeginANTS, 'affine_transform', fi, 'arg2')
buildtemplateparallel.connect( fi, 'out', wimtdeformed, 'transformation_series' )
buildtemplateparallel.connect( infosource, "subject_image", wimtdeformed, 'moving_image' )
buildtemplateparallel.connect( InitAvgImages, 'average_image', wimtdeformed, 'reference_image' )

#Connect wimtdeformed to AvgHalfDeformedImages
#buildtemplateparallel.connect( wimtdeformed, 'outputs', AvgHalfDeformedImages, 'images' )

##NODE: wimtinverse - Inverse Warp Image Multi Transform
##NEED TO FIGURE OUT HOW THIS IS USED, ITERABLES PROBABLY NEED TO BE INVOLVED
#wimtinverse = pe.Node( interface = WarpImageMultiTransform(), name = 'wimtinverse' )
#wimtinverse.inputs.moving_image = 'MYtemplate.nii.gz'
#wimtinverse.inputs.reference_image = '01_T1_half.nii.gz'
#wimtinverse.inputs.transformation_series = ['MY01_T1_halfInverseWarp.nii.gz']
#wimtinverse.cmdline

##NODE: AvgHalfWarpImages - Creates an average image of the three halfWarped images
#AvgHalfWarpImages=pe.Node(interface=AverageImages.algorithm(), name='AvgHalfWarpImages')
#AvgHalfWarpImages.inputs.dimension = 3
#AvgHalfWarpImages.inputs.output_average_image = 'MYtemplatewarp.nii.gz'
#AvgHalfWarpImages.inputs.normalize = 1
#AvgHalfWarpImages.inputs.images = ['MY01_T1_halfwarp.nii.gz', 'MY02_T1_halfwarp.nii.gz', 'MY03_T1_halfwarp.nii.gz']
#
##NODE: AvgAffineTransform - Creates an average image of the three Affine Images
#AvgAffineTransform = pe.Node( interface = AverageAffineTransform.algorithm(), name = 'AvgAffineTransform' )
#AvgAffineTransform.inputs.dimension = 3
#AvgAffineTransform.inputs.output_average_image = 'MYtemplateAffine.txt'
#AvgAffineTransform.inputs.normalize = 1
#AvgAffineTransform.inputs.images = ['MY01_T1_halfAffine.txt', 'MY02_T1_halfAffine.txt', 'MY03_T1_halfAffine.txt']
#
##NODE: MultiplyWarpImage - Multiply the image by the gradiant
#MultiplyWarpImage=pe.Node(interface=antsMultiplyImages.AntsMultiplyImages(), name='MultiplyWarpImage')
#MultiplyWarpImage.inputs.dimension = 3
#MultiplyWarpImage.inputs.first_image = #???
#MultiplyWarpImage.inputs.second_image = #???
#
##NODE: Warptemplates - Warps all of the templates to produce a new MYtemplatewarp.nii.gz
#Warptemplates = pe.Node( interface = WarpImageMultiTransform(), name = 'WarpWarpedImages' )
#Warptemplates.inputs.moving_image = 'MYtemplatewarp.nii.gz'
#Warptemplates.inputs.reference_image = 'MYtemplate.nii.gz'
#Warptemplates.inputs.transformation_series = ['MYtemplateAffine.txt']
#Warptemplate.inputst.invert_affine = [1]
#Warptemplates.cmdline
#
##NODE: WarpAll - Warp Everything together...
#WarpAll = pe.Node( interface = WarpImageMultiTransform(), name = 'WarpAll' )
#WarpAll.inputs.moving_image = 'MYtemplatewarp.nii.gz'
#WarpAll.inputs.reference_image = 'MYtemplate.nii.gz'
#WarpAll.inputs.transformation_series = ['MYtemplateAffine.txt', 'MYtemplatewarp.nii.gz', 'MYtemplatewarp.nii.gz', 'MYtemplatewarp.nii.gz', 'MYtemplatewarp.nii.gz']
#WarpAll.inputs.invert_affine = [1]
#WarpAll.cmdline
#
#
#####CONNECTIONS####
#

#
##connect BeginANTS to AvgHalfWarpImages
#workflow.connect( BeginANTS, 'warp_transform', AvgHalfWarpImages, 'images' )
#
##connect BeginANTS to AvgAffineTransform
#workflow.connect( BeginANTS, 'affine_transform', AvgHalfAffineImages, 'images' )
#
##connect AvgHalfWarpImages to MultiplyWarpImage
#workflow.connect( AvgHalfWarpImages, 'average_image', MultiplyWarpImage, 'product_image' )
#
##connect AvgHalfDeformedImages to Warptemplates
#workflow.connect( AvgHalfDeformedImages, 'average_image', Warptemplates, 'reference_image' )
#
##connect AvgHalfWarpImages to Warptemplates
#workflow.connect( AvgHalfWarpImages, 'average_image', Warptemplates, 'moving_image' )
#
##connect AvgAffineTransform to Warptemplates
#workflow.connect( AvgAffineTransform, 'average_image', Warptemplates, 'transformation_series' )
#
##connect AvgHalfDeformedImages to WarpAll
#workflow.connect( AvgHalfDeformedImages, 'average_image', WarpAll, 'moving_image' )
#workflow.connect( AvgHalfDeformedImages, 'average_image', WarpAll, 'reference_image' )
#
##connect AvgHalfWarpImages to WarpAll
#workflow.connect( AvgHalfWarpImages, 'average_image', WarpAll, 'transformation_series' )
#
##connect AvgAffineTransform to WarpAll:
#workflow.connect( AvgAffineTransform, 'average_image', WarpAll, 'transformation_series' )
#
### Perform a second iteration of the entire program...
##    # Set up a while loop for when i=0 or 1.  End the loop after the second iteration.
##i=0
##while i < 2:
##    Run program
##    i=i+1
###Final Output: MYtemplate.gii.nz
#
#
#if __name__ == "__main__":
#    # Create and parse input arguments
#    parser = argparse.ArgumentParser(description='')
#    parser.add_argument('-o', '--outputVolume', dest='outputVolume', help='The ANTS template output volume.')
#    parser.add_argument('-i', '--inputVolumes', nargs='*', dest='inputVolumes', help='The ANTS template input volumes.')
#    args = parser.parse_args()
#    print args.outputVolume
#    print args.inputVolumes

buildtemplateparallel.write_graph(graph2use='exec')

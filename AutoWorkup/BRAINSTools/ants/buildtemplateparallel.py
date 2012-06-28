import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import ants
from nipype.interfaces.ants import WarpImageMultiTransform
import antsMultiplyImages
from nipype.interfaces.io import DataGrabber

imagedir = '/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/'
images = ['{0}01_T1_half.nii.gz'.format(imagedir), '{0}02_T1_half.nii.gz'.format(imagedir), '{0}03_T1_half.nii.gz'.format(imagedir)]


#WORKFLOW: Creating overall workflow:
buildtemplateparallel = pe.Workflow(name='buildtemplateparallel')
ANTSintroduction = pe.Workflow(name='ANTSintroduction')
SUTT = pe.Workflow(name = 'SUTT')

#NODE: InitAvgImages - Average the initial images
InitAvgImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name ='InitAvgImages')
InitAvgImages.inputs.images = images
InitAvgImages.inputs.dimension = 3
InitAvgImages.inputs.output_average_image = '/IPLlinux/raid0/homes/jforbes/git/BRAINSStandAlone/AutoWorkup/BRAINSTools/ants/MYtemplate.nii.gz'
InitAvgImages.inputs.normalize = 1
#InitAvgImages.base_dir = "/IPLlinux/raid0/homes/jforbes/git/BRAINSStandAlone/AutoWorkup/BRAINSTools/ants/"
#print InitAvgImages.inputs
#print InitAvgImages.output_dir()
InitAvgImages.run()
print '-'*50
print InitAvgImages.get_output('average_image')
print '-'*50

#NODE: BeginANTS - produces warped, inverse warped, and affine images
BeginANTS=pe.MapNode(interface=ants.ANTS(), name = 'BeginANTS', iterfield=['moving_image'])
BeginANTS.inputs.dimension = 3
BeginANTS.inputs.output_transform_prefix = 'MY'
BeginANTS.inputs.metric = ['CC']
BeginANTS.inputs.moving_image = images
BeginANTS.inputs.metric_weight = [1.0]
BeginANTS.inputs.radius = [5]
BeginANTS.inputs.transformation_model = 'SyN'
BeginANTS.inputs.gradient_step_length = 0.25
BeginANTS.inputs.number_of_iterations = [50, 35, 15]
BeginANTS.inputs.use_histogram_matching = True
BeginANTS.inputs.mi_option = [32, 16000]
BeginANTS.inputs.regularization = 'Gauss'
BeginANTS.inputs.regularization_gradient_field_sigma = 3
BeginANTS.inputs.regularization_deformation_field_sigma = 0
BeginANTS.inputs.number_of_affine_iterations = [10000,10000,10000,10000,10000]

BeginANTS.outputs.transformList = 'wimtdeformed_transformation_list'
BeginANTS.outputs.warpTransformList = 'warp_transform'
BeginANTS.outputs.affineList = 'affine_transform'
BeginANTS.outputs.inverseList = 'inverse_warp_transform'


##InitAvgImages.run()
#BeginANTS.set_input('fixed_image', InitAvgImages.get_output('average_image'))

#Introducing iterables:

#initiate the infosource node:
infosource = pe.Node( interface = util.IdentityInterface( fields = ['subject_image'] ), name = "infosource" )
#define the list of subjects your pipeline should be executed on
infosource.iterables = ( 'subject_image', images)


#NODE: wimtdeformed - Forward Warp Image Multi Transform to produce deformed images
wimtdeformed = pe.Node( interface = WarpImageMultiTransform(), name = 'wimtdeformed') #iterfield=['transformation_series', 'moving_image']
##wimtdeformed.inputs.moving_image = images


#NODE: AvgHlafDeformedImages -  Creates an average image of the three halfDeformed images
AvgHalfDeformedImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgHalfDeformedImages')
AvgHalfDeformedImages.inputs.dimension = 3
AvgHalfDeformedImages.inputs.output_average_image = '~/MYtemplate.nii.gz'
AvgHalfDeformedImages.inputs.normalize = 1

#functionString = 'def func(arg1, arg2): return [arg1, arg2]'
#fi = pe.Node(interface=util.Function(input_names=['arg1', 'arg2'], output_names=['out']), name='ListAppender')
#fi.inputs.function_str = functionString
#fi.inputs.ignore_exception = True

deform_list = list()
functionString = 'def ListAppender(arg): deform_list.append(arg) return deform_list'
ListAppender = pe.Node(interface=util.Function(input_names=['arg'], output_names=['out']), name='ListAppender')
ListAppender.inputs.function_str = functionString
ListAppender.inputs.ignore_exception = True


########################
##### CONNECTIONS ######
########################
#Connect BeginANTS to wimtdeformed:
#ANTSintroduction.connect( BeginANTS, 'warp_transform', fi, 'arg1')
#ANTSintroduction.connect( BeginANTS, 'affine_transform', fi, 'arg2')
#ANTSintroduction.connect( fi, 'out', wimtdeformed, 'transformation_series' )
ANTSintroduction.connect( BeginANTS, 'wimtdeformed_transformation_list', wimtdeformed, 'transformation_series' )
buildtemplateparallel.connect( infosource, "subject_image", ANTSintroduction, "wimtdeformed.moving_image" )
buildtemplateparallel.connect( InitAvgImages, 'average_image', ANTSintroduction, "wimtdeformed.reference_image" )


##Connect InitAvgImages to BeginANTS
buildtemplateparallel.connect( InitAvgImages, "average_image", ANTSintroduction, "BeginANTS.fixed_image" )
#buildtemplateparallel.connect( infosource, "subject_image", ANTSintroduction, "BeginANTS.moving_image" )


#Connect wimtdeformed to AvgHalfDeformedImages
#buildtemplateparallel.connect(ANTSintroduction, "wimtdeformed.output_images", AvgHalfDeformedImages, 'images' )
####SUTT.connect( ListAppender, 'out', AvgHalfDeformedImages, 'images' )
####buildtemplateparallel.connect( ANTSintroduction, "wimtdeformed.output_images", SUTT, "ListAppender.arg")


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

#dg = DataGrabber(infields=['subject_id'], outfields=['affine','warp','inversewarp'])
#dg.inputs.base_directory = '.'
#dg.inputs.template = '%s/*%s'
#dg.inputs.template_args['affine'] = [['subject_id','Affine.txt']]
#dg.inputs.template_args['warp'] = [['subject_id','warp.nii.gz']]
#dg.inputs.template_args['inversewarp'] = [['subject_id','inversewarp.nii.gz']]
#dg.inputs.subject_id = 's1'

#buildtemplateparallel.run(plugin='MultiProc', plugin_args={'n_procs' : 3})

print 'number of subnodes:'
print BeginANTS.get_subnodes()
print '-'*50

print '*'*50
print BeginANTS.outputs
print '*'*50


buildtemplateparallel.write_graph(graph2use='hierarchical')
buildtemplateparallel.write_graph(graph2use='exec')

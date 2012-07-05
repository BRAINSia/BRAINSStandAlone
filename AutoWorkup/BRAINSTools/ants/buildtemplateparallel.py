import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import antsAverageAffineTransform
import antsMultiplyImages
import ants
import antsWarp
#from nipype.interfaces.ants import WarpImageMultiTransform
import antsMultiplyImages
from nipype.interfaces.io import DataGrabber

imagedir = '/hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/'
images = ['{0}01_T1_half.nii.gz'.format(imagedir), '{0}02_T1_half.nii.gz'.format(imagedir),'{0}03_T1_half.nii.gz'.format(imagedir)]
ExperimentBaseDirectoryCache = '/scratch/antsbuildtemplate/TEST_CACHE2'

#WORKFLOW: Creating overall workflow:
buildtemplateparallel = pe.Workflow( name='buildtemplateparallel')
buildtemplateparallel.config['execution'] = {
                                     'plugin':'Linear',
                                     #'stop_on_first_crash':'true',
                                     #'stop_on_first_rerun': 'true',
                                     'stop_on_first_crash':'true',
                                     'stop_on_first_rerun': 'false',      ## This stops at first attempt to rerun, before running, and before deleting previous results.
                                     'hash_method': 'timestamp',
                                     'single_thread_matlab':'true',       ## Multi-core 2011a  multi-core for matrix multiplication.
                                     'remove_unnecessary_outputs':'false',
                                     'use_relative_paths':'false',         ## relative paths should be on, require hash update when changed.
                                     'remove_node_directories':'false',   ## Experimental
                                     'local_hash_check':'true',           ##
                                     'job_finished_timeout':15            ##
                                     }
buildtemplateparallel.config['logging'] = {
      'workflow_level':'DEBUG',
      'filemanip_level':'DEBUG',
      'interface_level':'DEBUG',
      'log_directory': ExperimentBaseDirectoryCache
    }
buildtemplateparallel.base_dir = ExperimentBaseDirectoryCache

firstRun = pe.Workflow(name = 'firstRun')
firstRun.config['execution'] = {
                                     'keep_inputs':'true',
                                     'plugin':'Linear',
                                     #'stop_on_first_crash':'true',
                                     #'stop_on_first_rerun': 'true',
                                     'stop_on_first_crash':'true',
                                     'stop_on_first_rerun': 'false',      ## This stops at first attempt to rerun, before running, and before deleting previous results.
                                     'hash_method': 'timestamp',
                                     'single_thread_matlab':'true',       ## Multi-core 2011a  multi-core for matrix multiplication.
                                     'remove_unnecessary_outputs':'false',
                                     'use_relative_paths':'false',         ## relative paths should be on, require hash update when changed.
                                     'remove_node_directories':'false',   ## Experimental
                                     'local_hash_check':'true',           ##
                                     'job_finished_timeout':15            ##
                                     }
firstRun.config['logging'] = {
      'workflow_level':'DEBUG',
      'filemanip_level':'DEBUG',
      'interface_level':'DEBUG',
      'log_directory': ExperimentBaseDirectoryCache
    }
firstRun.base_dir = ExperimentBaseDirectoryCache

################# ASSIGNING NODES #################

#NODE: InitAvgImages - Average the initial images
InitAvgImages=pe.Node( interface=antsAverageImages.AntsAverageImages(), name ='InitAvgImages')
InitAvgImages.inputs.images = images
InitAvgImages.inputs.dimension = 3
InitAvgImages.inputs.output_average_image = 'MYtemplate.nii.gz'
InitAvgImages.inputs.normalize = 1

#NODE: BeginANTS - produces warped, inverse warped, and affine images
BeginANTS=pe.MapNode( interface=ants.ANTS(), name = 'BeginANTS', iterfield=['moving_image'])
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

#NODE: wimtdeformed - Forward Warp Image Multi Transform to produce deformed images
wimtdeformed = pe.MapNode( interface = antsWarp.WarpImageMultiTransform(), name ='wimtdeformed', iterfield=['transformation_series', 'moving_image'])
wimtdeformed.inputs.moving_image = images

#NODE: AvgHlafDeformedImages -  Creates an average image of the three halfDeformed images
AvgDeformedImages=pe.Node( interface=antsAverageImages.AntsAverageImages(), name='AvgDeformedImages')
AvgDeformedImages.inputs.dimension = 3
AvgDeformedImages.inputs.output_average_image = 'MYtemplate.nii.gz'
AvgDeformedImages.inputs.normalize = 1

#NODE: AvgAffineTransform - Creates an average image of the three Affine Images
AvgAffineTransform = pe.Node( interface=antsAverageAffineTransform.AntsAverageAffineTransform(), name = 'AvgAffineTransform' )
AvgAffineTransform.inputs.dimension = 3
AvgAffineTransform.inputs.output_affine_transform = 'MYtemplateAffine.txt'

#NODE: AvgWarpImages - Creates an average image of the three halfWarped images
AvgWarpImages=pe.Node( interface=antsAverageImages.AntsAverageImages(), name='AvgWarpImages')
AvgWarpImages.inputs.dimension = 3
AvgWarpImages.inputs.output_average_image = 'MYtemplatewarp.nii.gz'
AvgWarpImages.inputs.normalize = 1

#NODE: MultiplyWarpImage - Multiply the image by the gradiant
MultiplyWarpImage=pe.Node(interface=antsMultiplyImages.AntsMultiplyImages(), name='MultiplyWarpImage')
MultiplyWarpImage.inputs.dimension = 3
MultiplyWarpImage.inputs.second_input = -0.25
MultiplyWarpImage.inputs.output_product_image = 'MYtemplatewarp.nii.gz'

#NODE: Warptemplates - Warps all of the templates to produce a new MYtemplatewarp.nii.gz
Warptemplates = pe.Node( interface = antsWarp.WarpImageMultiTransform(), name = 'Warptemplates' )
Warptemplates.inputs.invert_affine = [1]

#NODE: WarpAll - Warp Everything together...
WarpAll = pe.Node( interface = antsWarp.WarpImageMultiTransform(), name = 'WarpAll' )
WarpAll.inputs.invert_affine = [1]

#NODE: ListAppender1 - creates a list of affines and images for the transformation_series in WarpAll
functionString1 = 'def func(arg1, arg2): return map(list, zip(arg1,arg2))'
ListAppender1 = pe.Node(interface=util.Function(input_names=['arg1', 'arg2'], output_names=['out']), name='ListAppender1')
ListAppender1.inputs.function_str = functionString1
ListAppender1.inputs.ignore_exception = True

#NODE: ListAppender - creates a list of affines and images for the transformation_series in WarpAll
functionString2 = 'def func(arg1, arg2, arg3, arg4, arg5): return [arg1, arg2, arg3, arg4, arg5]'
fi = pe.Node(interface=util.Function(input_names=['arg1', 'arg2', 'arg3', 'arg4', 'arg5'], output_names=['out']), name='ListAppender')
fi.inputs.function_str = functionString2
fi.inputs.ignore_exception = True

################# CONNECTIONS #################

#connect BeginANTS to ListAppender1
firstRun.connect( BeginANTS, 'warp_transform', ListAppender1, 'arg1')
firstRun.connect( BeginANTS, 'affine_transform', ListAppender1, 'arg2')

#connct ListAppender to WarpAll
firstRun.connect( ListAppender1, 'out', wimtdeformed, 'transformation_series' )

#Connect BeginANTS to wimtdeformed:
#firstRun.connect( BeginANTS, 'wimtdeformed_transformation_list', wimtdeformed, 'transformation_series' )
buildtemplateparallel.connect( InitAvgImages, 'average_image', firstRun, "wimtdeformed.reference_image" )

##Connect InitAvgImages to BeginANTS
buildtemplateparallel.connect( InitAvgImages, "average_image", firstRun, "BeginANTS.fixed_image" )

#Connect wimtdeformed to AvgDeformedImages
firstRun.connect( wimtdeformed, "output_image", AvgDeformedImages, 'images' )

#connect BeginANTS to AvgAffineTransform
firstRun.connect( BeginANTS, 'affine_transform', AvgAffineTransform, 'transforms' )

#connect BeginANTS to AvgWarpImages
firstRun.connect( BeginANTS, 'warp_transform', AvgWarpImages, 'images' )

#connect AvgWarpImages to MultiplyWarpImage
firstRun.connect( AvgWarpImages, 'average_image', MultiplyWarpImage, 'first_input' )

#connect AvgDeformedImages to Warptemplates
firstRun.connect( AvgDeformedImages, 'average_image', Warptemplates, 'reference_image' )

#connect AvgWarpImages to Warptemplates
firstRun.connect( MultiplyWarpImage, 'product_image', Warptemplates, 'moving_image' )

#connect AvgAffineTransform to Warptemplates
firstRun.connect( AvgAffineTransform, 'affine_transform', Warptemplates, 'transformation_series' )

#connect AvgAffineTransform and Warptemplates to ListAppender
firstRun.connect( AvgAffineTransform, 'affine_transform', fi, 'arg1')
firstRun.connect( Warptemplates, 'output_image', fi, 'arg2')
firstRun.connect( Warptemplates, 'output_image', fi, 'arg3')
firstRun.connect( Warptemplates, 'output_image', fi, 'arg4')
firstRun.connect( Warptemplates, 'output_image', fi, 'arg5')

#connct ListAppender to WarpAll
firstRun.connect( fi, 'out', WarpAll, 'transformation_series' )

#connect AvgDeformedImages to WarpAll
firstRun.connect( AvgDeformedImages, 'average_image', WarpAll, 'moving_image' )
firstRun.connect( AvgDeformedImages, 'average_image', WarpAll, 'reference_image' )

#Connect clone!!
secondRun = firstRun.clone(name='secondRun')

buildtemplateparallel.connect(firstRun, 'WarpAll.output_image', secondRun, 'BeginANTS.fixed_image')
buildtemplateparallel.connect(firstRun, 'WarpAll.output_image', secondRun, 'wimtdeformed.reference_image')

################### RUN #####################

buildtemplateparallel.run(plugin='MultiProc', plugin_args={'n_procs' : 3})

buildtemplateparallel.write_graph(graph2use='hierarchical')
buildtemplateparallel.write_graph(graph2use='exec')

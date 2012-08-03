#################################################################################
## Program:   Build Template Parallel
## Language:  Python
##
## Authors:  Jessica Forbes, Grace Murray, and Hans Johnson, University of Iowa
##
##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.
##
#################################################################################

import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import antsAverageAffineTransform
import antsMultiplyImages
import ants
import antsWarp
import antsMultiplyImages
from nipype.interfaces.io import DataGrabber

def ANTSTemplateBuildSingleIterationWF(iterationPhasePrefix,CLUSTER_QUEUE):

    antsTemplateBuildSingleIterationWF = pe.Workflow(name = 'ANTSTemplateBuildSingleIterationWF_'+iterationPhasePrefix)

    ## HACK:  Include passive_images_list here for list of images to be passively put into template space.
    inputSpec = pe.Node(interface=util.IdentityInterface(fields=['images', 'fixed_image','passive_images_list']),
                run_without_submitting=True,
                name='InputSpec')
    outputSpec = pe.Node(interface=util.IdentityInterface(fields=['template','transforms_list']),
                run_without_submitting=True,
                name='OutputSpec')

    ### NOTE MAP NODE! warp each of the original images to the provided fixed_image as the template
    BeginANTS=pe.MapNode(interface=ants.ANTS(), name = 'BeginANTS', iterfield=['moving_image'])
    many_cpu_BeginANTS_options_dictionary={'qsub_args': '-S /bin/bash -pe smp1 8-12 -l mem_free=6000M -o /dev/null -e /dev/null '+CLUSTER_QUEUE, 'overwrite': True}
    BeginANTS.plugin_args=many_cpu_BeginANTS_options_dictionary
    BeginANTS.inputs.dimension = 3
    BeginANTS.inputs.output_transform_prefix = iterationPhasePrefix+'_tfm'
    BeginANTS.inputs.metric = ['CC']
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
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'images', BeginANTS, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'fixed_image', BeginANTS, 'fixed_image')

    ## Utility Function
    ## This will make a list of list pairs for defining the concatenation of transforms
    ## wp=['wp1.nii','wp2.nii','wp3.nii']
    ## af=['af1.mat','af2.mat','af3.mat']
    ## ll=map(list,zip(af,wp))
    ## ll
    ##[['af1.mat', 'wp1.nii'], ['af2.mat', 'wp2.nii'], ['af3.mat', 'wp3.nii']]
    def MakeListsOfTransformLists(warpTransformList, AffineTransformList):
        return map(list, zip(warpTransformList,AffineTransformList))
    MakeTransformsLists = pe.Node(interface=util.Function(function=MakeListsOfTransformLists,input_names=['warpTransformList', 'AffineTransformList'], output_names=['out']), 
                    run_without_submitting=True,
                    name='MakeTransformsLists')
    MakeTransformsLists.inputs.ignore_exception = True
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'warp_transform', MakeTransformsLists, 'warpTransformList')
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'affine_transform', MakeTransformsLists, 'AffineTransformList')

    ## Now warp all the images
    wimtdeformed = pe.MapNode(interface = antsWarp.WarpImageMultiTransform(), name ='wimtdeformed', iterfield=['transformation_series', 'moving_image'])
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'images', wimtdeformed, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(MakeTransformsLists, 'out', wimtdeformed, 'transformation_series')

    ## Now average all affine transforms together
    AvgAffineTransform = pe.Node(interface=antsAverageAffineTransform.AntsAverageAffineTransform(), name = 'AvgAffineTransform')
    AvgAffineTransform.inputs.dimension = 3
    AvgAffineTransform.inputs.output_affine_transform = iterationPhasePrefix+'Affine.mat'
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'affine_transform', AvgAffineTransform, 'transforms')

    ## Now average the warp fields togther
    AvgWarpImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgWarpImages')
    AvgWarpImages.inputs.dimension = 3
    AvgWarpImages.inputs.output_average_image = iterationPhasePrefix+'warp.nii.gz'
    AvgWarpImages.inputs.normalize = 1
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'warp_transform', AvgWarpImages, 'images')

    ## Now average the images together
    ## HACK:  For now GradientStep is set to 0.25 as a hard coded default value.
    GradientStep = 0.25
    GradientStepWarpImage=pe.Node(interface=antsMultiplyImages.AntsMultiplyImages(), name='GradientStepWarpImage')
    GradientStepWarpImage.inputs.dimension = 3
    GradientStepWarpImage.inputs.second_input = -1.0 * GradientStep
    GradientStepWarpImage.inputs.output_product_image = iterationPhasePrefix+'warp.nii.gz'
    antsTemplateBuildSingleIterationWF.connect(AvgWarpImages, 'average_image', GradientStepWarpImage, 'first_input')

    ## Now  Average All inte deformed images together to create an updated template average
    AvgDeformedImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgDeformedImages')
    AvgDeformedImages.inputs.dimension = 3
    AvgDeformedImages.inputs.output_average_image = iterationPhasePrefix+'.nii.gz'
    AvgDeformedImages.inputs.normalize = 1
    antsTemplateBuildSingleIterationWF.connect(wimtdeformed, "output_image", AvgDeformedImages, 'images')

    ## Now create the new template shape based on the average of all deformed images
    UpdateTemplateShape = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'UpdateTemplateShape')
    UpdateTemplateShape.inputs.invert_affine = [1]
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', UpdateTemplateShape, 'reference_image')
    antsTemplateBuildSingleIterationWF.connect(AvgAffineTransform, 'affine_transform', UpdateTemplateShape, 'transformation_series')
    antsTemplateBuildSingleIterationWF.connect(GradientStepWarpImage, 'product_image', UpdateTemplateShape, 'moving_image')

    def MakeTransformListWithGradientWarps(averageAffineTranform, gradientStepWarp):
        return [averageAffineTranform, gradientStepWarp, gradientStepWarp, gradientStepWarp, gradientStepWarp]
    ApplyInvAverageAndFourTimesGradientStepWarpImage = pe.Node(interface=util.Function(function=MakeTransformListWithGradientWarps,
                                         input_names=['averageAffineTranform', 'gradientStepWarp'],
                                         output_names=['TransformListWithGradientWarps']),
                 run_without_submitting=True,
                 name='MakeTransformListWithGradientWarps')
    ApplyInvAverageAndFourTimesGradientStepWarpImage.inputs.ignore_exception = True

    antsTemplateBuildSingleIterationWF.connect(AvgAffineTransform, 'affine_transform', ApplyInvAverageAndFourTimesGradientStepWarpImage, 'averageAffineTranform')
    antsTemplateBuildSingleIterationWF.connect(UpdateTemplateShape, 'output_image', ApplyInvAverageAndFourTimesGradientStepWarpImage, 'gradientStepWarp')

    WarpAll = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'WarpAll')
    WarpAll.inputs.invert_affine = [1]
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'reference_image')
    antsTemplateBuildSingleIterationWF.connect(ApplyInvAverageAndFourTimesGradientStepWarpImage, 'TransformListWithGradientWarps', WarpAll, 'transformation_series')

    antsTemplateBuildSingleIterationWF.connect(WarpAll, 'output_image', outputSpec, 'template')
    return antsTemplateBuildSingleIterationWF

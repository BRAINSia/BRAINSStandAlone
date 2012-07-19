#!/usr/bin/python
#################################################################################
## Program:   Build Template Parallel
## Language:  Python
##
## Authors:  Jessica Forbes and Grace Murray, University of Iowa
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

def initAvgWF(ExperimentBaseDirectoryCache):
    initAvgWF = pe.Workflow(name= 'initAvgWF')

    inputSpec = pe.Node(interface=util.IdentityInterface(fields=['images']), name='InputSpec')
    outputSpec = pe.Node(interface=util.IdentityInterface(fields=['average_image']), name='OutputSpec')

    InitAvgImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name ='InitAvgImages')
    InitAvgImages.inputs.dimension = 3
    InitAvgImages.inputs.output_average_image = 'MYtemplate.nii.gz'
    InitAvgImages.inputs.normalize = 1

    initAvgWF.connect(inputSpec, 'images', InitAvgImages, 'images')
    initAvgWF.connect(InitAvgImages, 'average_image', outputSpec, 'average_image')

    return initAvgWF

def mainWF(ExperimentBaseDirectoryCache):

    mainWF = pe.Workflow(name = 'mainWF')

    inputSpec = pe.Node(interface=util.IdentityInterface(fields=['images', 'fixed_image']), name='InputSpec')
    outputSpec = pe.Node(interface=util.IdentityInterface(fields=['template']), name='OutputSpec')

    BeginANTS=pe.MapNode(interface=ants.ANTS(), name = 'BeginANTS', iterfield=['moving_image'])
    BeginANTS.inputs.dimension = 3
    BeginANTS.inputs.output_transform_prefix = 'MY'
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

    wimtdeformed = pe.MapNode(interface = antsWarp.WarpImageMultiTransform(), name ='wimtdeformed', iterfield=['transformation_series', 'moving_image'])

    AvgDeformedImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgDeformedImages')
    AvgDeformedImages.inputs.dimension = 3
    AvgDeformedImages.inputs.output_average_image = 'MYtemplate.nii.gz'
    AvgDeformedImages.inputs.normalize = 1

    AvgAffineTransform = pe.Node(interface=antsAverageAffineTransform.AntsAverageAffineTransform(), name = 'AvgAffineTransform')
    AvgAffineTransform.inputs.dimension = 3
    AvgAffineTransform.inputs.output_affine_transform = 'MYtemplateAffine.txt'

    AvgWarpImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgWarpImages')
    AvgWarpImages.inputs.dimension = 3
    AvgWarpImages.inputs.output_average_image = 'MYtemplatewarp.nii.gz'
    AvgWarpImages.inputs.normalize = 1

    MultiplyWarpImage=pe.Node(interface=antsMultiplyImages.AntsMultiplyImages(), name='MultiplyWarpImage')
    MultiplyWarpImage.inputs.dimension = 3
    MultiplyWarpImage.inputs.second_input = -0.25
    MultiplyWarpImage.inputs.output_product_image = 'MYtemplatewarp.nii.gz'

    Warptemplates = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'Warptemplates')
    Warptemplates.inputs.invert_affine = [1]

    WarpAll = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'WarpAll')
    WarpAll.inputs.invert_affine = [1]

    functionString1 = 'def func(arg1, arg2): return map(list, zip(arg1,arg2))'
    ListAppender1 = pe.Node(interface=util.Function(input_names=['arg1', 'arg2'], output_names=['out']), name='ListAppender1')
    ListAppender1.inputs.function_str = functionString1
    ListAppender1.inputs.ignore_exception = True

    functionString2 = 'def func(arg1, arg2, arg3, arg4, arg5): return [arg1, arg2, arg3, arg4, arg5]'
    fi = pe.Node(interface=util.Function(input_names=['arg1', 'arg2', 'arg3', 'arg4', 'arg5'], output_names=['out']), name='ListAppender2')
    fi.inputs.function_str = functionString2
    fi.inputs.ignore_exception = True

    mainWF.connect(inputSpec, 'images', BeginANTS, 'moving_image')
    mainWF.connect(inputSpec, 'images', wimtdeformed, 'moving_image')
    mainWF.connect(inputSpec, 'fixed_image', BeginANTS, 'fixed_image')

    mainWF.connect(BeginANTS, 'warp_transform', ListAppender1, 'arg1')
    mainWF.connect(BeginANTS, 'affine_transform', ListAppender1, 'arg2')
    mainWF.connect(BeginANTS, 'warp_transform', AvgWarpImages, 'images')
    mainWF.connect(BeginANTS, 'affine_transform', AvgAffineTransform, 'transforms')

    mainWF.connect(ListAppender1, 'out', wimtdeformed, 'transformation_series')

    mainWF.connect(wimtdeformed, "output_image", AvgDeformedImages, 'images')

    mainWF.connect(AvgWarpImages, 'average_image', MultiplyWarpImage, 'first_input')

    mainWF.connect(AvgDeformedImages, 'average_image', Warptemplates, 'reference_image')
    mainWF.connect(MultiplyWarpImage, 'product_image', Warptemplates, 'moving_image')
    mainWF.connect(AvgAffineTransform, 'affine_transform', Warptemplates, 'transformation_series')

    mainWF.connect(AvgAffineTransform, 'affine_transform', fi, 'arg1')
    mainWF.connect(Warptemplates, 'output_image', fi, 'arg2')
    mainWF.connect(Warptemplates, 'output_image', fi, 'arg3')
    mainWF.connect(Warptemplates, 'output_image', fi, 'arg4')
    mainWF.connect(Warptemplates, 'output_image', fi, 'arg5')

    mainWF.connect(fi, 'out', WarpAll, 'transformation_series')

    mainWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'moving_image')
    mainWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'reference_image')

    mainWF.connect(WarpAll, 'output_image', outputSpec, 'template')

    return mainWF

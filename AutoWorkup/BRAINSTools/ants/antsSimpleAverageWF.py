import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import antsAverageAffineTransform
import antsMultiplyImages
import antsRegistration
import antsWarp
#from nipype.interfaces.ants import WarpImageMultiTransform
import antsMultiplyImages
from nipype.interfaces.io import DataGrabber

def antsSimpleAverageWF():
    antsSimpleAverageWF = pe.Workflow(name= 'antsSimpleAverageWF')

    inputSpec = pe.Node(interface=util.IdentityInterface(fields=['images']), name='InputSpec')
    outputSpec = pe.Node(interface=util.IdentityInterface(fields=['average_image']), name='OutputSpec')

    InitAvgImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name ='InitAvgImages')
    InitAvgImages.inputs.dimension = 3
    InitAvgImages.inputs.output_average_image = 'MYtemplate.nii.gz'
    InitAvgImages.inputs.normalize = 1

    antsSimpleAverageWF.connect(inputSpec, 'images', InitAvgImages, 'images')
    antsSimpleAverageWF.connect(InitAvgImages, 'average_image', outputSpec, 'average_image')

    return antsSimpleAverageWF

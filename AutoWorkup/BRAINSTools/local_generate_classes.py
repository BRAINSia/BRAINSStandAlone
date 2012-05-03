## \author Hans J. Johnson
## This file contains the code necessary to build the python module
## nodes for SEM compliant tools
##

# export PATH=/ipldev/scratch/johnsonhj/src/BRAINSStandAlone-Darwin-clang/lib:${PATH}
# export PYTHONPATH=/ipldev/sharedopt/20120201/Darwin_i386/PYTHON_MODULES/lib/python2.7/site-packages
# export PYTHONPATH=/ipldev/sharedopt/20120201/Darwin_i386/PYTHON_MODULES
# nipype/interfaces/slicer/generate_classes.py
from nipype.interfaces.slicer.generate_classes import generate_all_classes

modules_list = [
  'BRAINSABC',
  'BRAINSAlignMSP',
  'BRAINSClipInferior',
  'BRAINSConstellationDetector',
  'BRAINSConstellationModeler',
  'BRAINSDemonWarp',
  'BRAINSFit',
  'BRAINSMush',
  'BRAINSROIAuto',
  'BRAINSResample',
  'BRAINSLandmarkInitializer',
  'GradientAnisotropicDiffusionImageFilter',
  'GenerateSummedGradientImage',
  'BRAINSInitializedControlPoints',
  'BRAINSLmkTransform',
  'BRAINSMultiModeSegment',
  'BRAINSROIAuto',
  'BRAINSResample',
  'BRAINSTrimForegroundInDirection',
  'ESLR',
  'VBRAINSDemonWarp',
  'extractNrrdVectorIndex',
  'gtractAnisotropyMap',
  'gtractAverageBvalues',
  'gtractClipAnisotropy',
  'gtractCoRegAnatomy',
  'gtractConcatDwi',
  'gtractCopyImageOrientation',
  'gtractCoregBvalues',
  'gtractCostFastMarching',
  'gtractImageConformity',
  'gtractInvertBSplineTransform',
  'gtractInvertDisplacementField',
  'gtractInvertRigidTransform',
  'gtractResampleAnisotropy',
  'gtractResampleB0',
  'gtractResampleCodeImage',
  'gtractResampleDWIInPlace',
  'gtractTensor',
  'gtractTransformToDisplacementField',
  'GenerateLabelMapFromProbabilityMap',
  'BRAINSLinearModelerEPCA',
  'BRAINSCut',
]



launcher=['']
generate_all_classes(modules_list=modules_list, launcher=[])


#! /usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Date:          2012-05-30
Author:        hans-johnson@uiowa.edu
Purpose:       Wrap a convenience function for the BRAINSCut program in Nipype

Requirements:  <<< Interface specifications >>>


"""
from nipype.interfaces.base import ( File, TraitedSpec, Interface, CommandLineInputSpec, CommandLine, traits )
import sys

### CommandLine
class RF12BRAINSCutWrapperCLInputSpec(CommandLineInputSpec):
    ### subject specific
    inputSubjectT1Filename = File( desc="Subject T1 Volume", exists=True, mandatory=True, rgstr="--inputSubjectT1Filename %s")
    inputSubjectT2Filename = File( desc="Subject T2 Volume", exists=True, mandatory=True, rgstr="--inputSubjectT2Filename %s")
    inputSubjectSGFilename = File( desc="Subject SG Volume", exists=True, mandatory=True, rgstr="--inputSubjectSGFilename %s")

    ### model specific
    modelFilename = File( desc="modelFilename", exists=True, mandatory=True, rgstr="--modelFilename %s")
    trainingVectorFilename = File( desc="training vectof file name", exists=False, mandatory=False, rgstr="--trainingVectorFilename %s")
    inputTemplateT1 = File( desc="Atlas Template T1 image", exists=False, mandatory=False, rgstr="--inputTemplateT1 %s")
    inputTemplateRhoFilename = File( desc="Atlas Template rho image", exists=False, mandatory=False, rgstr="--inputTemplateRhoFilename %s")
    inputTemplatePhiFilename = File( desc="Atlas Template phi image", exists=False, mandatory=False, rgstr="--inputTemplatePhiFilename %s")
    inputTemplateThetaFilename = File( desc="Atlas Template theta image", exists=False, mandatory=False, rgstr="--inputTemplateThetaFilename %s")
    deformationFromTemplateToSubject = File( desc="Atlas To subject Deformation", exists=False, mandatory=False, rgstr="--deformationFromTemplateToSubject %s")

    ### probability maps
    probabilityMapsLeftAccumben = File( desc="Spatial probability map of left accumben", exists=True, mandatory=True, rgstr="--probabilityMapsLeftAccumben %s")
    probabilityMapsRightAccumben = File( desc="Spatial probability map of right accumben", exists=True, mandatory=True, rgstr="--probabilityMapsRightAccumben %s")

    probabilityMapsLeftCaudate = File( desc="Spatial probability map of left caudate", exists=True, mandatory=True, rgstr="--probabilityMapsLeftCaudate %s")
    probabilityMapsRightCaudate = File( desc="Spatial probability map of right caudate", exists=True, mandatory=True, rgstr="--probabilityMapsRightCaudate %s")

    probabilityMapsLeftGlobus = File( desc="Spatial probability map of left globus", exists=True, mandatory=True, rgstr="--probabilityMapsLeftGlobus %s")
    probabilityMapsRightGlobus = File( desc="Spatial probability map of right globus", exists=True, mandatory=True, rgstr="--probabilityMapsRightGlobus %s")

    probabilityMapsLeftHippocampus = File( desc="Spatial probability map of left hippocampus", exists=True, mandatory=True, rgstr="--probabilityMapsLeftHippocampus %s")
    probabilityMapsRightHippocampus = File( desc="Spatial probability map of right hippocampus", exists=True, mandatory=True, rgstr="--probabilityMapsRightHippocampus %s")

    probabilityMapsLeftPutamen = File( desc="Spatial probability map of left putamen", exists=True, mandatory=True, rgstr="--probabilityMapsLeftPutamen %s")
    probabilityMapsRightPutamen = File( desc="Spatial probability map of right putamen", exists=True, mandatory=True, rgstr="--probabilityMapsRightPutamen %s")

    probabilityMapsLeftThalamus = File( desc="Spatial probability map of left thalamus", exists=True, mandatory=True, rgstr="--probabilityMapsLeftThalamus %s")
    probabilityMapsRightThalamus = File( desc="Spatial probability map of right thalamus", exists=True, mandatory=True, rgstr="--probabilityMapsRightThalamus %s")

    xmlFilename = File( desc = "Net configuration xml file", exists = False, mandatory = False, rgstr="--xmlFilename %s")

    outputBinaryLeftAccumben = File( desc = "Output binary file of left accumben", exists = False, mandatory = True, rgstr="--outputBinaryLeftAccumben %s")
    outputBinaryRightAccumben = File( desc = "Output binary file of right accumben", exists = False, mandatory = True, rgstr="--outputBinaryRightAccumben %s")

    outputBinaryLeftCaudate = File( desc = "Output binary file of left caudate", exists = False, mandatory = True, rgstr="--outputBinaryLeftCaudate %s")
    outputBinaryRightCaudate = File( desc = "Output binary file of right caudate", exists = False, mandatory = True, rgstr="--outputBinaryRightCaudate %s")

    outputBinaryLeftGlobus = File( desc = "Output binary file of left globus", exists = False, mandatory = True, rgstr="--outputBinaryLeftGlobus %s")
    outputBinaryRightGlobus = File( desc = "Output binary file of right globus", exists = False, mandatory = True, rgstr="--outputBinaryRightGlobus %s")

    outputBinaryLeftHippocampus = File( desc = "Output binary file of left hippocampus", exists = False, mandatory = True, rgstr="--outputBinaryLeftHippocampus %s")
    outputBinaryRightHippocampus = File( desc = "Output binary file of right hippocampus", exists = False, mandatory = True, rgstr="--outputBinaryRightHippocampus %s")

    outputBinaryLeftPutamen = File( desc = "Output binary file of left putamen", exists = False, mandatory = True, rgstr="--outputBinaryLeftPutamen %s")
    outputBinaryRightPutamen = File( desc = "Output binary file of right putamen", exists = False, mandatory = True, rgstr="--outputBinaryRightPutamen %s")

    outputBinaryLeftThalamus = File( desc = "Output binary file of left thalamus", exists = False, mandatory = True, rgstr="--outputBinaryLeftThalamus %s")
    outputBinaryRightThalamus = File( desc = "Output binary file of right thalamus", exists = False, mandatory = True, rgstr="--outputBinaryRightThalamus %s")

class RF12BRAINSCutWrapperCLOutputSpec(CommandLineInputSpec):
    xmlFilename = File( desc = "Net configuration xml file", exists = True, mandatory = True)

    outputBinaryLeftAccumben = File( desc = "Output binary file of left accumben", exists = True, mandatory = True)
    outputBinaryRightAccumben = File( desc = "Output binary file of right accumben", exists = True, mandatory = True)

    outputBinaryLeftCaudate = File( desc = "Output binary file of left caudate", exists = True, mandatory = True)
    outputBinaryRightCaudate = File( desc = "Output binary file of right caudate", exists = True, mandatory = True)

    outputBinaryLeftGlobus = File( desc = "Output binary file of left globus", exists = True, mandatory = True)
    outputBinaryRightGlobus = File( desc = "Output binary file of right globus", exists = True, mandatory = True)

    outputBinaryLeftHippocampus = File( desc = "Output binary file of left hippocampus", exists = True, mandatory = True)
    outputBinaryRightHippocampus = File( desc = "Output binary file of right hippocampus", exists = True, mandatory = True)

    outputBinaryLeftPutamen = File( desc = "Output binary file of left putamen", exists = True, mandatory = True)
    outputBinaryRightPutamen = File( desc = "Output binary file of right putamen", exists = True, mandatory = True)

    outputBinaryLeftThalamus = File( desc = "Output binary file of left thalamus", exists = True, mandatory = True)
    outputBinaryRightThalamus = File( desc = "Output binary file of right thalamus", exists = True, mandatory = True)


class RF12BRAINSCutWrapper(CommandLine):
    _cmd = sys.executable + ' BRAINSCutCMD.py'
    input_spec = RF12BRAINSCutWrapperCLInputSpec
    output_spec = RF12BRAINSCutWrapperCLOutputSpec

if __name__ == '__main__':
    RF12Test = RF12BRAINSCutWrapper(sys.argv)
    RF12Test.run()

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

### CommandLine
class RF12BRAINSCutWrapperCLInputSpec(CommandLineInputSpec):
    ### subject specific
    subjectT1Filename = File( desc="Subject T1 Volume", exists=True, mandatory=True, rgstr="--inputSubjectT1Filename %s")
    subjectT2Filename = File( desc="Subject T2 Volume", exists=True, mandatory=True, rgstr="--inputSubjectT2Filename %s")
    subjectSGFilename = File( desc="Subject SG Volume", exists=True, mandatory=True, rgstr="--inputSubjectSGFilename %s")
    
    ### model specific
    modelFilename = File( desc="modelFilename", exists=True, mandatory=True, rgstr="--modelFilename %s")
    trainingVectorFilename = File( desc="training vectof file name", exists=False, mandatory=False, rgstr="--trainingVectorFilename %s")

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


class RF12BRAINSCutWrapperCLOutputSpec(CommandLineInputSpec):
    xmlFilename = File( desc = "Net configuration xml file", exists = True, mandatory = True)

    binaryLeftAccumben = File( desc = "Output binary file of left accumben", exists = True, mandatory = True)
    binaryRightAccumben = File( desc = "Output binary file of right accumben", exists = True, mandatory = True)

    binaryLeftCaudate = File( desc = "Output binary file of left caudate", exists = True, mandatory = True)
    binaryRightCaudate = File( desc = "Output binary file of right caudate", exists = True, mandatory = True)

    binaryLeftGlobus = File( desc = "Output binary file of left globus", exists = True, mandatory = True)
    binaryRightGlobus = File( desc = "Output binary file of right globus", exists = True, mandatory = True)

    binaryLeftHippocampus = File( desc = "Output binary file of left hippocampus", exists = True, mandatory = True)
    binaryRightHippocampus = File( desc = "Output binary file of right hippocampus", exists = True, mandatory = True)

    binaryLeftPutamen = File( desc = "Output binary file of left putamen", exists = True, mandatory = True)
    binaryRightPutamen = File( desc = "Output binary file of right putamen", exists = True, mandatory = True)

    binaryLeftThalamus = File( desc = "Output binary file of left thalamus", exists = True, mandatory = True)
    binaryRightThalamus = File( desc = "Output binary file of right thalamus", exists = True, mandatory = True)


class RF12BRAINSCutWrapper(CommandLine):
    _cmd = 'BRAINSCutCMD.sh'
    input_spec = RF12BRAINSCutWrapperCLInputSpec
    output_spec = RF12BRAINSCutWrapperCLOutputSpec

if __name__ == '__main__':
    RF12Test = RF12BRAINSCutWrapper(sys.argv)
    RF12Test.run()

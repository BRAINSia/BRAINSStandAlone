#!/usr/bin/env python

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory
from nipype.interfaces.base import traits, isdefined, BaseInterface
from nipype.interfaces.utility import Merge, Split, Function, Rename, IdentityInterface
import nipype.interfaces.io as nio   # Data i/o
import nipype.pipeline.engine as pe  # pypeline engine
from nipype.interfaces.freesurfer import ReconAll

from nipype.interfaces.freesurfer.model import MS_LDA

"""
    from WorkupT1T2FreeSurfer import CreateFreeSurferWorkflow
    myLocalFSWF= CreateFreeSurferWorkflow("HansFSTest")
    baw200.connect(uidSource,'uid',myLocalFSWF,'inputspec.subject_id')
    baw200.connect(SplitAvgBABC,'avgBABCT1',myLocalFSWF,'inputspec.T1_files')
"""

def MakeFreesurferOutputDirectory(subjects_dir,subject_id):
    return subjects_dir+'/'+subject_id

def GenerateWFName(projectid, subjectid, sessionid,WFName):
    return WFName+'_'+str(subjectid)+"_"+str(sessionid)+"_"+str(projectid)

def CreateFreeSurferWorkflow(projectid, subjectid, sessionid,WFname,CLUSTER_QUEUE,RunAllFSComponents=True,RunMultiMode=True):
    freesurferWF= pe.Workflow(name=GenerateWFName(projectid, subjectid, sessionid,WFname))

    inputsSpec = pe.Node(interface=IdentityInterface(fields=['FreeSurfer_ID','T1_files','T2_files',
                                                             'label_file','mask_file']), name='inputspec' )
    outputsSpec = pe.Node(interface=IdentityInterface(fields=['subject_id','subjects_dir',
                                     'FreesurferOutputDirectory','cnr_optimal_image']), name='outputspec' )

    if RunMultiMode:
        mergeT1T2 = pe.Node(interface=Merge(2),name="Merge_T1T2")
        freesurferWF.connect(inputsSpec,'T1_files',  mergeT1T2,'in1')
        freesurferWF.connect(inputsSpec,'T2_files',  mergeT1T2,'in2')

        #Some constants based on assumpts about the label_file from BRAINSABC
        white_label = 1
        grey_label = 2

        msLDA_GenerateWeights = pe.Node(interface=MS_LDA(),name="MS_LDA")
        MSLDA_sge_options_dictionary={'qsub_args': '-S /bin/bash -pe smp1 1 -l h_vmem=12G,mem_free=2G -o /dev/null -e /dev/null '+CLUSTER_QUEUE, 'overwrite': True}
        msLDA_GenerateWeights.plugin_args=MSLDA_sge_options_dictionary
        msLDA_GenerateWeights.inputs.lda_labels=[white_label,grey_label]
        msLDA_GenerateWeights.inputs.weight_file = 'weights.txt'
        msLDA_GenerateWeights.inputs.use_weights=False
        msLDA_GenerateWeights.inputs.output_synth = 'synth_out.nii.gz'
        #msLDA_GenerateWeights.inputs.vol_synth_file = 'synth_out.nii.gz'
        #msLDA_GenerateWeights.inputs.shift = 0 # value to shift by

        freesurferWF.connect(mergeT1T2,'out',  msLDA_GenerateWeights,'images')
        freesurferWF.connect(inputsSpec,'label_file',  msLDA_GenerateWeights,'label_file')
        #freesurferWF.connect(inputsSpec,'mask_file',  msLDA_GenerateWeights,'mask_file') ## Mask file MUST be unsigned char
        freesurferWF.connect(msLDA_GenerateWeights,'vol_synth_file',outputsSpec,'cnr_optimal_image')

    if RunAllFSComponents == True:
        print("""Run Freesurfer ReconAll at""")
        fs_reconall = pe.Node(interface=ReconAll(),name="FS510")
        freesurfer_sge_options_dictionary={'qsub_args': '-S /bin/bash -pe smp1 4 -l h_vmem=18G,mem_free=8 -o /dev/null -e /dev/null '+CLUSTER_QUEUE, 'overwrite': True}
        fs_reconall.plugin_args=freesurfer_sge_options_dictionary
        fs_reconall.inputs.directive = 'all'
        freesurferWF.connect(inputsSpec,'subject_id',fs_reconall,'subject_id')
        if RunMultiMode:
            ## Use the output of the synthesized T1 with maximized contrast
            freesurferWF.connect(msLDA_GenerateWeights,'vol_synth_file',  fs_reconall,'T1_files')
        else:
            ## Use the output of the T1 only image
            freesurferWF.connect(inputsSpec,'T1_files', fs_reconall,'T1_files')


        computeFinalDirectory = pe.Node( Function(function=MakeFreesurferOutputDirectory, input_names = ['subjects_dir','subject_id'], output_names = ['FreesurferOutputDirectory']), run_without_submitting=True, name="99_computeFreesurferOutputDirectory")
        freesurferWF.connect(fs_reconall,'subjects_dir',computeFinalDirectory,'subjects_dir')
        freesurferWF.connect(fs_reconall,'subject_id',computeFinalDirectory,'subject_id')

        freesurferWF.connect(fs_reconall,'subject_id',outputsSpec,'subject_id')
        freesurferWF.connect(fs_reconall,'subjects_dir',outputsSpec,'subjects_dir')
        freesurferWF.connect(computeFinalDirectory,'FreesurferOutputDirectory',outputsSpec,'FreesurferOutputDirectory')
    return freesurferWF

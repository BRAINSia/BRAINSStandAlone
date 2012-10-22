#!/usr/bin/python
#################################################################################
## Program:   BRAINS (Brain Research: Analysis of Images, Networks, and Systems)
## Language:  Python
##
## Author:  Hans J. Johnson
##
##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.
##
#################################################################################

import os
import csv
import sys
import string
import argparse
#"""Import necessary modules from nipype."""
#from nipype.utils.config import config
#config.set('logging', 'log_to_file', 'false')
#config.set_log_dir(os.getcwd())
#--config.set('logging', 'workflow_level', 'DEBUG')
#--config.set('logging', 'interface_level', 'DEBUG')
#--config.set('execution','remove_unnecessary_outputs','false')

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory
from nipype.interfaces.base import traits, isdefined, BaseInterface
from nipype.interfaces.utility import Merge, Split, Function, Rename, IdentityInterface
import nipype.interfaces.io as nio   # Data i/o
import nipype.pipeline.engine as pe  # pypeline engine
from nipype.interfaces.freesurfer import ReconAll

from nipype.utils.misc import package_check
#package_check('nipype', '5.4', 'tutorial1') ## HACK: Check nipype version
package_check('numpy', '1.3', 'tutorial1')
package_check('scipy', '0.7', 'tutorial1')
package_check('networkx', '1.0', 'tutorial1')
package_check('IPython', '0.10', 'tutorial1')

from BRAINSTools import *

from WorkupT1T2AtlasNode import MakeAtlasNode

def getListIndex( imageList, index):
    return imageList[index]

#HACK:  [('buildTemplateIteration2', 'SUBJECT_TEMPLATES/0249/buildTemplateIteration2')]
def GenerateSubjectOutputPattern(subjectid):
    """ This function generates output path substitutions for workflows and nodes that conform to a common standard.
HACK:  [('ANTSTemplate/Iteration02_Reshaped.nii.gz', 'SUBJECT_TEMPLATES/0668/T1_RESHAPED.nii.gz'),
('ANTSTemplate/_ReshapeAveragePassiveImageWithShapeUpdate[0-9]*', 'SUBJECT_TEMPLATES/0668')]
subs=r'test/\g<project>/\g<subject>/\g<session>'
pe.sub(subs,test)
pat=r'foo/_uid_(?P<project>PHD_[0-9][0-9][0-9])_(?P<subject>[0-9][0-9][0-9][0-9])_(?P<session>[0-9][0-9][0-9][0-9][0-9])'
pe=re.compile(pat)
pe.sub(subs,test)
test
test='foo/_uid_PHD_024_0003_12345'
pe.sub(subs,test)
pat=r'(?P<modulename>[^/]*)/_uid_(?P<project>PHD_[0-9][0-9][0-9])_(?P<subject>[0-9][0-9][0-9][0-9])_(?P<session>[0-9][0-9][0-9][0-9][0-9])'
subs=r'test/\g<project>/\g<subject>/\g<session>/\g<modulename>'
pe.sub(subs,test)
pe=re.compile(pat)
pe.sub(subs,test)

/nfsscratch/PREDICT/johnsonhj/ExpandedExperiment/20120801.SubjectOrganized_Results/ANTSTemplate/CLIPPED_AVG_CSFWARP_AVG_CSF.nii.gz
-> /nfsscratch/PREDICT/johnsonhj/ExpandedExperiment/20120801.SubjectOrganized_Results/SUBJECT_TEMPLATES/2013/AVG_CSF.nii.gz
"""
    patternList=[]


    find_pat=os.path.join('ANTSTemplate','Iteration02_Reshaped.nii.gz')
    replace_pat=os.path.join('SUBJECT_TEMPLATES',subjectid,r'AVG_T1.nii.gz')
    patternList.append( (find_pat,replace_pat) )

    find_pat=os.path.join('ANTSTemplate',r'_ReshapeAveragePassiveImageWithShapeUpdate[0-9]*/AVG_[A-Z0-9]*WARP_(?P<structure>AVG_[A-Z0-9]*.nii.gz)')
    replace_pat=os.path.join('SUBJECT_TEMPLATES',subjectid,r'\g<structure>')
    patternList.append( (find_pat,replace_pat) )

    find_pat=os.path.join('ANTSTemplate',r'CLIPPED_AVG_[A-Z]*WARP_(?P<structure>AVG_[A-Z]*.nii.gz)')
    replace_pat=os.path.join('SUBJECT_TEMPLATES',subjectid,r'\g<structure>')
    patternList.append( (find_pat,replace_pat) )

    print "HACK: ", patternList
    return patternList

def GenerateOutputPattern(projectid, subjectid, sessionid,DefaultNodeName):
    """ This function generates output path substitutions for workflows and nodes that conform to a common standard.
    """
    patternList=[]
    find_pat=os.path.join(DefaultNodeName)
    replace_pat=os.path.join(projectid,subjectid,sessionid,DefaultNodeName)
    patternList.append( (find_pat,replace_pat) )
    print "HACK: ", patternList
    return patternList

def GenerateAccumulatorImagesOutputPattern(projectid, subjectid, sessionid):
    """ This function generates output path substitutions for workflows and nodes that conform to a common standard.
    """
    patternList=[]
    find_pat="POSTERIOR_"
    replace_pat=os.path.join(projectid,subjectid,sessionid)+"/POSTERIOR_"
    patternList.append( (find_pat,replace_pat) )
    print "HACK: ", patternList
    return patternList

## This takes several lists and merges them, but it also removes all empty values from the lists
def MergeByExtendListElements(t1_averageList,t2_averageList,pd_averageList,fl_averageList,outputLabels_averageList,ListOfPosteriorImagesDictionary):
    """
ListOfImagesDictionaries=[
{'T1':os.path.join(mydatadir,'01_T1_half.nii.gz'),'INV_T1':os.path.join(mydatadir,'01_T1_inv_half.nii.gz'),'LABEL_MAP':os.path.join(mydatadir,'01_T1_inv_half.nii
  .gz')},
{'T1':os.path.join(mydatadir,'02_T1_half.nii.gz'),'INV_T1':os.path.join(mydatadir,'02_T1_inv_half.nii.gz'),'LABEL_MAP':os.path.join(mydatadir,'02_T1_inv_half.nii
  .gz')},
{'T1':os.path.join(mydatadir,'03_T1_half.nii.gz'),'INV_T1':os.path.join(mydatadir,'03_T1_inv_half.nii.gz'),'LABEL_MAP':os.path.join(mydatadir,'03_T1_inv_half.nii
  .gz')}
]

outputLabels_averageList = ['brain_label_seg.nii.gz', 'brain_label_seg.nii.gz']
pd_averageList = [None, None]
t1_averageList = ['t1_average_BRAINSABC.nii.gz', 't1_average_BRAINSABC.nii.gz']
t2_averageList = ['t2_average_BRAINSABC.nii.gz', 't2_average_BRAINSABC.nii.gz']

"""
    print "t1_averageList",t1_averageList
    print "t2_averageList",t2_averageList
    print "pd_averageList",pd_averageList
    print "fl_averageList",fl_averageList
    print "outputLabels_averageList",outputLabels_averageList
    print "$$$$$$$$$$$$$$$$$$$$$$$"
    print "ListOfPosteriorImagesDictionary",ListOfPosteriorImagesDictionary

    ## Initial list with empty dictionaries
    ListOfImagesDictionaries=[dict() for i in range(0,len(t1_averageList))]

    registrationImageTypes=['T1'] ## ['T1','T2'] someday.
    #DefaultContinuousInterpolationType='LanczosWindowedSinc' ## Could also be Linear for speed.
    DefaultContinuousInterpolationType='Linear'
    interpolationMapping={'T1':DefaultContinuousInterpolationType,
                          'T2':DefaultContinuousInterpolationType,
                          'PD':DefaultContinuousInterpolationType,
                          'FL':DefaultContinuousInterpolationType,
                          'BRAINMASK':'NearestNeighbor'
                         }
    ## NOTE:  ALl input lists MUST have the same number of elements (even if they are null)
    for list_index in range(0,len(t1_averageList)):
        if t1_averageList[list_index] is not None:
            ListOfImagesDictionaries[list_index]['T1']=t1_averageList[list_index]
        if t2_averageList[list_index] is not None:
            ListOfImagesDictionaries[list_index]['T2']=t2_averageList[list_index]
        if pd_averageList[list_index] is not None:
            ListOfImagesDictionaries[list_index]['PD']=pd_averageList[list_index]
        if fl_averageList[list_index] is not None:
            ListOfImagesDictionaries[list_index]['FL']=fl_averageList[list_index]
        if outputLabels_averageList[list_index] is not None:
            ListOfImagesDictionaries[list_index]['BRAINMASK']=outputLabels_averageList[list_index]
        this_subj_posteriors=ListOfPosteriorImagesDictionary[list_index]
        for post_items in this_subj_posteriors.items():
            print "post_items",post_items
            ListOfImagesDictionaries[list_index][post_items[0]] = post_items[1]

    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print "ListOfImagesDictionaries",ListOfImagesDictionaries
    print "registrationImageTypes",registrationImageTypes
    print "interpolationMapping",interpolationMapping
    return ListOfImagesDictionaries,registrationImageTypes,interpolationMapping

def MakeNewAtlasTemplate(t1_image,deformed_list,
            AtlasTemplate,outDefinition):
    import os
    import sys
    import SimpleITK as sitk
    patternDict= {
        'AVG_AIR.nii.gz':'@ATLAS_DIRECTORY@/EXTENDED_AIR.nii.gz',
        'AVG_BGM.nii.gz':'@ATLAS_DIRECTORY@/EXTENDED_BASALTISSUE.nii.gz',
        'AVG_CRBLGM.nii.gz':'@ATLAS_DIRECTORY@/EXTENDED_CRBLGM.nii.gz',
        'AVG_CRBLWM.nii.gz':'@ATLAS_DIRECTORY@/EXTENDED_CRBLWM.nii.gz',
        'AVG_CSF.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_CSF.nii.gz',
        'AVG_NOTCSF.nii.gz' :'@ATLAS_DIRECTORY@/EXTENDED_NOTCSF.nii.gz',
        'AVG_NOTGM.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_NOTGM.nii.gz',
        'AVG_NOTVB.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_NOTVB.nii.gz',
        'AVG_NOTWM.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_NOTWM.nii.gz',
        'AVG_SURFGM.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_SURFGM.nii.gz',
        'AVG_VB.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_VB.nii.gz',
        'AVG_WM.nii.gz':'@ATLAS_DIRECTORY@/EXTENDED_WM.nii.gz',
        'AVG_ACCUMBEN.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_ACCUMBEN.nii.gz',
        'AVG_CAUDATE.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_CAUDATE.nii.gz',
        'AVG_PUTAMEN.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_PUTAMEN.nii.gz',
        'AVG_GLOBUS.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_GLOBUS.nii.gz',
        'AVG_THALAMUS.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_THALAMUS.nii.gz',
        'AVG_HIPPOCAMPUS.nii.gz': '@ATLAS_DIRECTORY@/EXTENDED_HIPPOCAMPUS.nii.gz',
        'AVG_BRAINMASK.nii.gz':'@ATLAS_DIRECTORY@/template_brain.nii.gz',
        'T1_RESHAPED.nii.gz':'@ATLAS_DIRECTORY@/template_t1.nii.gz',
        'AVG_T2.nii.gz':'@ATLAS_DIRECTORY@/template_t2.nii.gz',
        'AVG_PD.nii.gz':'@ATLAS_DIRECTORY@/template_t2.nii.gz',
        'AVG_FL.nii.gz':'@ATLAS_DIRECTORY@/template_t2.nii.gz'
        }
    templateFile = open(AtlasTemplate,'r')
    content = templateFile.read()              # read entire file into memory
    templateFile.close()

    ## Now clean up the posteriors based on anatomical knowlege.
    ## sometimes the posteriors are not relevant for priors
    ## due to anomolies around the edges.
    print("\n\n\nALL_FILES: {0}\n\n\n".format(deformed_list))
    load_images_list=dict()
    for full_pathname in deformed_list:
        base_name=os.path.basename(full_pathname)
        if base_name in patternDict.keys():
            load_images_list[base_name]=sitk.ReadImage(full_pathname)
        else:
            print("MISSING FILE FROM patternDict: {0}".format(base_name))
    ## Make binary dilated mask
    binmask=sitk.BinaryThreshold(load_images_list['AVG_BRAINMASK.nii.gz'],1,1000000)
    dilated5=sitk.DilateObjectMorphology(binmask,5)
    dilated5=sitk.Cast(dilated5,sitk.sitkFloat32) # Convert to Float32 for multiply
    ## Now clip the interior brain mask with dilated5
    interiorPriors = [
        'AVG_BGMWARP_AVG_BGM.nii.gz',
        'AVG_CRBLGMWARP_AVG_CRBLGM.nii.gz',
        'AVG_CRBLWMWARP_AVG_CRBLWM.nii.gz',
        'AVG_CSFWARP_AVG_CSF.nii.gz',
        'AVG_SURFGMWARP_AVG_SURFGM.nii.gz',
        'AVG_VBWARP_AVG_VB.nii.gz',
        'AVG_WMWARP_AVG_WM.nii.gz',
        'AVG_ACCUMBENWARP_AVG_ACCUMBEN.nii.gz',
        'AVG_CAUDATEWARP_AVG_CAUDATE.nii.gz',
        'AVG_PUTAMENWARP_AVG_PUTAMEN.nii.gz',
        'AVG_GLOBUSWARP_AVG_GLOBUS.nii.gz',
        'AVG_THALAMUSWARP_AVG_THALAMUS.nii.gz',
        'AVG_HIPPOCAMPUSWARP_AVG_HIPPOCAMPUS.nii.gz',
        ]
    clean_deformed_list=deformed_list
    T2File=None
    PDFile=None
    for index in range(0,len(deformed_list)):
        full_pathname=deformed_list[index]
        base_name=os.path.basename(full_pathname)
        if base_name == 'AVG_BRAINMASK.nii.gz':
            ### Make Brain Mask Binary
            clipped_name='CLIPPED_'+base_name
            patternDict[clipped_name]=patternDict[base_name]
            sitk.WriteImage(binmask,clipped_name)
            clean_deformed_list[index]=os.path.realpath(clipped_name)
        if base_name == 'AVG_T2WARP_AVG_T2.nii.gz':
            T2File=full_pathname
        if base_name == 'AVG_PDWARP_AVG_PD.nii.gz':
            PDFile=full_pathname
        if base_name in interiorPriors:
            ### Make clipped posteriors for brain regions
            curr=sitk.Cast(sitk.ReadImage(full_pathname),sitk.sitkFloat32)
            curr=curr*dilated5
            clipped_name='CLIPPED_'+base_name
            patternDict[clipped_name]=patternDict[base_name]
            sitk.WriteImage(curr,clipped_name)
            clean_deformed_list[index]=os.path.realpath(clipped_name)
            print "HACK: ", clean_deformed_list[index]
            curr=None
    binmask=None
    dilated5=None

    for full_pathname in clean_deformed_list:
        base_name=os.path.basename(full_pathname)
        if base_name in patternDict.keys():
            content=content.replace(patternDict[base_name],full_pathname)
    ## If there is no T2, then use the PD image
    if T2File is not None:
        content=content.replace('@ATLAS_DIRECTORY@/template_t2.nii.gz',T2File)
    elif PDFile is not None:
        content=content.replace('@ATLAS_DIRECTORY@/template_t2.nii.gz',PDFile)
    content=content.replace('@ATLAS_DIRECTORY@/template_t1.nii.gz',t1_image)
    ## NOTE:  HEAD REGION CAN JUST BE T1 image.
    content=content.replace('@ATLAS_DIRECTORY@/template_headregion.nii.gz',t1_image)
    ## NOTE:  BRAIN REGION CAN JUST BE the label images.
    outAtlasFullPath=os.path.realpath(outDefinition)
    newFile = open(outAtlasFullPath, 'w')
    newFile.write(content)  # write the file with the text substitution
    newFile.close()
    return outAtlasFullPath,clean_deformed_list

def AccumulateLikeTissuePosteriors(posteriorImages):
    import os
    import sys
    import SimpleITK as sitk
    ## Now clean up the posteriors based on anatomical knowlege.
    ## sometimes the posteriors are not relevant for priors
    ## due to anomolies around the edges.
    load_images_list=dict()
    for full_pathname in posteriorImages.values():
        base_name=os.path.basename(full_pathname)
        load_images_list[base_name]=sitk.ReadImage(full_pathname)
    GM_ACCUM=[
              'POSTERIOR_ACCUMBEN.nii.gz',
              'POSTERIOR_CAUDATE.nii.gz',
              'POSTERIOR_CRBLGM.nii.gz',
              'POSTERIOR_HIPPOCAMPUS.nii.gz',
              'POSTERIOR_PUTAMEN.nii.gz',
              'POSTERIOR_THALAMUS.nii.gz',
              'POSTERIOR_SURFGM.nii.gz',
             ]
    WM_ACCUM=[
              'POSTERIOR_CRBLWM.nii.gz',
              'POSTERIOR_WM.nii.gz'
              ]
    CSF_ACCUM=[
              'POSTERIOR_CSF.nii.gz',
              ]
    VB_ACCUM=[
              'POSTERIOR_VB.nii.gz',
              ]
    GLOBUS_ACCUM=[
              'POSTERIOR_GLOBUS.nii.gz',
              ]
    BACKGROUND_ACCUM=[
              'POSTERIOR_AIR.nii.gz',
              'POSTERIOR_NOTCSF.nii.gz',
              'POSTERIOR_NOTGM.nii.gz',
              'POSTERIOR_NOTVB.nii.gz',
              'POSTERIOR_NOTWM.nii.gz',
              ]
    ## The next 2 items MUST be syncronized
    AccumulatePriorsNames=['POSTERIOR_GM_TOTAL.nii.gz','POSTERIOR_WM_TOTAL.nii.gz',
                        'POSTERIOR_CSF_TOTAL.nii.gz','POSTERIOR_VB_TOTAL.nii.gz',
                        'POSTERIOR_GLOBUS_TOTAL.nii.gz','POSTERIOR_BACKGROUND_TOTAL.nii.gz']
    ForcedOrderingLists=[GM_ACCUM,WM_ACCUM,CSF_ACCUM,VB_ACCUM,GLOBUS_ACCUM,BACKGROUND_ACCUM]
    AccumulatePriorsList=list()
    for index in range(0,len(ForcedOrderingLists)):
        outname=AccumulatePriorsNames[index]
        inlist=ForcedOrderingLists[index]
        accum_image= load_images_list[ inlist[0] ] # copy first image
        for curr_image in range(1,len(inlist)):
            accum_image=accum_image + load_images_list[ inlist[curr_image] ]
        sitk.WriteImage(accum_image,outname)
        AccumulatePriorsList.append(os.path.realpath(outname))
    print "HACK \n\n\n\n\n\n\n HACK \n\n\n: {APL}\n".format(APL=AccumulatePriorsList)
    print ": {APN}\n".format(APN=AccumulatePriorsNames)
    return AccumulatePriorsList,AccumulatePriorsNames
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
## WorkupT1T2 is the main workflow to be run
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def WorkupT1T2(subjectid,mountPrefix,ExperimentBaseDirectoryCache, ExperimentBaseDirectoryResults, ExperimentDatabase, atlas_fname_wpath, BCD_model_path,
               InterpolationMode="Linear", Mode=10,DwiList=[],WORKFLOW_COMPONENTS=[],CLUSTER_QUEUE=''):
    """
    Run autoworkup on all subjects data defined in the ExperimentDatabase

    This is the main function to call when processing a data set with T1 & T2
    data.  ExperimentBaseDirectoryPrefix is the base of the directory to place results, T1Images & T2Images
    are the lists of images to be used in the auto-workup. atlas_fname_wpath is
    the path and filename of the atlas to use.
    """

    print "Building Pipeline"
    ########### PIPELINE INITIALIZATION #############
    baw200 = pe.Workflow(name="BAW_20120813")
    baw200.config['execution'] = {
                                     'plugin':'Linear',
                                     #'stop_on_first_crash':'true',
                                     #'stop_on_first_rerun': 'true',
                                     'stop_on_first_crash':'false',
                                     'stop_on_first_rerun': 'false',      ## This stops at first attempt to rerun, before running, and before deleting previous results.
                                     'hash_method': 'timestamp',
                                     'single_thread_matlab':'true',       ## Multi-core 2011a  multi-core for matrix multiplication.
                                     'remove_unnecessary_outputs':'false',
                                     'use_relative_paths':'false',         ## relative paths should be on, require hash update when changed.
                                     'remove_node_directories':'false',   ## Experimental
                                     'local_hash_check':'true',           ##
                                     'job_finished_timeout':30            ##
                                     }
    baw200.config['logging'] = {
      'workflow_level':'DEBUG',
      'filemanip_level':'DEBUG',
      'interface_level':'DEBUG',
      'log_directory': ExperimentBaseDirectoryCache
    }
    baw200.base_dir = ExperimentBaseDirectoryCache


    import WorkupT1T2Single
    MergeT1s=dict()
    MergeT2s=dict()
    MergePDs=dict()
    MergeFLs=dict()
    MergeOutputLabels=dict()
    MergePosteriors=dict()
    BAtlas=dict()
    FREESURFER_ID=dict()
    if True:
        print("===================== SUBJECT: {0} ===========================".format(subjectid))
        PHASE_1_oneSubjWorkflow=dict()
        PHASE_1_subjInfoNode=dict()
        allSessions = ExperimentDatabase.getSessionsFromSubject(subjectid)
        print("Running sessions: {ses} for subject {sub}".format(ses=allSessions,sub=subjectid))
        BAtlas[subjectid] = MakeAtlasNode(atlas_fname_wpath,"BAtlas_"+str(subjectid)) ## Call function to create node


        for sessionid in allSessions:
            global_AllT1s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T1-30','T1-15'])
            global_AllT2s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T2-30','T2-15'])
            global_AllPDs=ExperimentDatabase.getFilenamesByScantype(sessionid,['PD-30','PD-15'])
            global_AllFLs=ExperimentDatabase.getFilenamesByScantype(sessionid,['FL-30','FL-15'])
            global_AllOthers=ExperimentDatabase.getFilenamesByScantype(sessionid,['OTHER-30','OTHER-15'])
            print("HACK:  all T1s: {0} {1}".format(global_AllT1s, len(global_AllT1s) ))
            print("HACK:  all T2s: {0} {1}".format(global_AllT2s, len(global_AllT2s) ))
            print("HACK:  all PDs: {0} {1}".format(global_AllPDs, len(global_AllPDs) ))
            print("HACK:  all FLs: {0} {1}".format(global_AllFLs, len(global_AllFLs) ))
            print("HACK:  all Others: {0} {1}".format(global_AllOthers, len(global_AllOthers) ))

            projectid = ExperimentDatabase.getProjFromSession(sessionid)
            print("PROJECT: {0} SUBJECT: {1} SESSION: {2}".format(projectid,subjectid,sessionid))
            PHASE_1_subjInfoNode[sessionid] = pe.Node(interface=IdentityInterface(fields=
                    ['sessionid','subjectid','projectid',
                     'allT1s',
                     'allT2s',
                     'allPDs',
                     'allFLs',
                     'allOthers']),
                    run_without_submitting=True,
                    name='99_PHASE_1_SubjInfoNode_'+str(subjectid)+"_"+str(sessionid) )
            PHASE_1_subjInfoNode[sessionid].inputs.projectid=projectid
            PHASE_1_subjInfoNode[sessionid].inputs.subjectid=subjectid
            PHASE_1_subjInfoNode[sessionid].inputs.sessionid=sessionid
            PHASE_1_subjInfoNode[sessionid].inputs.allT1s=global_AllT1s
            PHASE_1_subjInfoNode[sessionid].inputs.allT2s=global_AllT2s
            PHASE_1_subjInfoNode[sessionid].inputs.allPDs=global_AllPDs
            PHASE_1_subjInfoNode[sessionid].inputs.allFLs=global_AllFLs
            PHASE_1_subjInfoNode[sessionid].inputs.allOthers=global_AllOthers

            PROCESSING_PHASE='PHASE_1'
            PHASE_1_WORKFLOW_COMPONENTS =  ['BASIC','TISSUE_CLASSIFY']
            PHASE_1_oneSubjWorkflow[sessionid]=WorkupT1T2Single.MakeOneSubWorkFlow(
                              projectid, subjectid, sessionid,PROCESSING_PHASE,
                              PHASE_1_WORKFLOW_COMPONENTS,
                              BCD_model_path, InterpolationMode, CLUSTER_QUEUE)
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'projectid',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.projectid')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'subjectid',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.subjectid')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'sessionid',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.sessionid')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'allT1s',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.allT1s')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'allT2s',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.allT2s')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'allPDs',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.allPDs')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'allFLs',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.allFLs')
            baw200.connect(PHASE_1_subjInfoNode[sessionid],'allOthers',PHASE_1_oneSubjWorkflow[sessionid],'inputspec.allOthers')

            baw200.connect(BAtlas[subjectid],'template_landmarks_31_fcsv', PHASE_1_oneSubjWorkflow[sessionid],'inputspec.template_landmarks_31_fcsv')
            baw200.connect(BAtlas[subjectid],'template_landmark_weights_31_csv', PHASE_1_oneSubjWorkflow[sessionid],'inputspec.template_landmark_weights_31_csv')
            baw200.connect(BAtlas[subjectid],'template_t1', PHASE_1_oneSubjWorkflow[sessionid],'inputspec.template_t1')
            baw200.connect(BAtlas[subjectid],'ExtendedAtlasDefinition_xml', PHASE_1_oneSubjWorkflow[sessionid],'inputspec.atlasDefinition')

        numSessions=len(allSessions)
        if True or numSessions > 1: ## Merge all BCD_Results into a global average
            mergeSubjectSessionNamesT1="99_MergeAllSessions_T1_"+str(subjectid)
            MergeT1s[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesT1)
            mergeSubjectSessionNamesT2="99_MergeAllSessions_T2_"+str(subjectid)
            MergeT2s[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesT2)
            mergeSubjectSessionNamesPD="99_MergeAllSessions_PD_"+str(subjectid)
            MergePDs[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesPD)
            mergeSubjectSessionNamesFL="99_MergeAllSessions_FL_"+str(subjectid)
            MergeFLs[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesFL)
            mergeSubjectSessionNamesoutputLabels="99_MergeAllSessions_outputLabels_"+str(subjectid)
            MergeOutputLabels[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesoutputLabels)
            mergeSubjectSessionNamesPosteriors="99_MergeAllSessions_Posteriors_"+str(subjectid)
            MergePosteriors[subjectid] = pe.Node(interface=Merge(numSessions),
                                          run_without_submitting=True,
                                          name=mergeSubjectSessionNamesPosteriors)
            index=1
            #print("HACK: HACK: HACK:  {0}".format(allSessions))
            for sessionid in allSessions:
                index_name='in'+str(index)
                index+=1
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.t1_average',MergeT1s[subjectid],index_name)
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.t2_average',MergeT2s[subjectid],index_name)
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.pd_average',MergePDs[subjectid],index_name)
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.fl_average',MergeFLs[subjectid],index_name)
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.outputLabels',MergeOutputLabels[subjectid],index_name)
                baw200.connect(PHASE_1_oneSubjWorkflow[sessionid],'outputspec.posteriorImages',MergePosteriors[subjectid],index_name)

            MergeByExtendListElementsNode = pe.Node( Function(function=MergeByExtendListElements,
                                          input_names = ['t1_averageList','t2_averageList',
                                            'pd_averageList','fl_averageList',
                                            'outputLabels_averageList','ListOfPosteriorImagesDictionary'],
                                          output_names = ['ListOfImagesDictionaries','registrationImageTypes','interpolationMapping']),
                                          run_without_submitting=True, name="99_MergeByExtendListElements")
            baw200.connect( MergeT1s[subjectid],'out', MergeByExtendListElementsNode, 't1_averageList' )
            baw200.connect( MergeT2s[subjectid],'out', MergeByExtendListElementsNode, 't2_averageList' )
            baw200.connect( MergePDs[subjectid],'out', MergeByExtendListElementsNode, 'pd_averageList' )
            baw200.connect( MergeFLs[subjectid],'out', MergeByExtendListElementsNode, 'fl_averageList' )
            baw200.connect( MergeOutputLabels[subjectid],'out', MergeByExtendListElementsNode, 'outputLabels_averageList' )
            baw200.connect( MergePosteriors[subjectid],'out', MergeByExtendListElementsNode, 'ListOfPosteriorImagesDictionary' )


            ### USE ANTS
            import nipype.interfaces.ants as ants
            myInitAvgWF = pe.Node(interface=ants.AverageImages(), name ='Phase1_antsSimpleAverage')
            myInitAvgWF.inputs.dimension = 3
            myInitAvgWF.inputs.normalize = True
            baw200.connect(MergeT1s[subjectid], 'out', myInitAvgWF, "images")

            TEMPLATE_BUILD_RUN_MODE='MULTI_IMAGE'
            if numSessions == 1:
                TEMPLATE_BUILD_RUN_MODE='SINGLE_IMAGE'

            ### USE ANTS REGISTRATION
            #from nipype.workflows.smri.ants import antsRegistrationTemplateBuildSingleIterationWF
            from BAWantsRegistrationBuildTemplate import BAWantsRegistrationTemplateBuildSingleIterationWF
            buildTemplateIteration1=BAWantsRegistrationTemplateBuildSingleIterationWF('iteration01')
            ## TODO:  Change these parameters
            BeginANTS = buildTemplateIteration1.get_node("BeginANTS")
            BeginANTS.plugin_args={'qsub_args': '-S /bin/bash -pe smp1 8-12 -l mem_free=6000M -o /dev/null -e /dev/null queue_name', 'overwrite': True}

            baw200.connect(myInitAvgWF, 'output_average_image', buildTemplateIteration1, 'inputspec.fixed_image')
            baw200.connect(MergeByExtendListElementsNode, 'ListOfImagesDictionaries', buildTemplateIteration1, 'inputspec.ListOfImagesDictionaries')
            baw200.connect(MergeByExtendListElementsNode, 'registrationImageTypes', buildTemplateIteration1, 'inputspec.registrationImageTypes')
            baw200.connect(MergeByExtendListElementsNode, 'interpolationMapping', buildTemplateIteration1, 'inputspec.interpolationMapping')

            buildTemplateIteration2 = buildTemplateIteration1.clone(name='buildTemplateIteration2')
            buildTemplateIteration2 = BAWantsRegistrationTemplateBuildSingleIterationWF('Iteration02')
            baw200.connect(buildTemplateIteration1, 'outputspec.template', buildTemplateIteration2, 'inputspec.fixed_image')
            baw200.connect(MergeByExtendListElementsNode, 'ListOfImagesDictionaries', buildTemplateIteration2, 'inputspec.ListOfImagesDictionaries')
            baw200.connect(MergeByExtendListElementsNode, 'registrationImageTypes', buildTemplateIteration2, 'inputspec.registrationImageTypes')
            baw200.connect(MergeByExtendListElementsNode, 'interpolationMapping', buildTemplateIteration2, 'inputspec.interpolationMapping')

            ### Now define where the final organized outputs should go.
            SubjectTemplate_DataSink=pe.Node(nio.DataSink(),name="SubjectTemplate_DS")
            SubjectTemplate_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
            SubjectTemplate_DataSink.inputs.regexp_substitutions = GenerateSubjectOutputPattern(subjectid)
            baw200.connect(buildTemplateIteration2,'outputspec.template',SubjectTemplate_DataSink,'ANTSTemplate.@template')

            MakeNewAtlasTemplateNode = pe.Node(interface=Function(function=MakeNewAtlasTemplate,
                    input_names=['t1_image', 'deformed_list','AtlasTemplate','outDefinition'],
                    output_names=['outAtlasFullPath','clean_deformed_list']),
                    # This is a lot of work, so submit it run_without_submitting=True,
                    name='99_MakeNewAtlasTemplate')
            MakeNewAtlasTemplateNode.inputs.outDefinition='AtlasDefinition_'+subjectid+'.xml'
            baw200.connect(BAtlas[subjectid],'ExtendedAtlasDefinition_xml_in',MakeNewAtlasTemplateNode,'AtlasTemplate')
            baw200.connect(buildTemplateIteration2,'outputspec.template',MakeNewAtlasTemplateNode,'t1_image')
            baw200.connect(buildTemplateIteration2,'outputspec.passive_deformed_templates',MakeNewAtlasTemplateNode,'deformed_list')
            baw200.connect(MakeNewAtlasTemplateNode,'clean_deformed_list',SubjectTemplate_DataSink,'ANTSTemplate.@passive_deformed_templates')

            ###### Starting Phase II
            PHASE_2_oneSubjWorkflow=dict()
            PHASE_2_subjInfoNode=dict()
            BASIC_DataSink=dict()
            TC_DataSink=dict()
            AddLikeTissueSink=dict()
            AccumulateLikeTissuePosteriorsNode=dict()
            for sessionid in allSessions:
                projectid = ExperimentDatabase.getProjFromSession(sessionid)
                print("PHASE II PROJECT: {0} SUBJECT: {1} SESSION: {2}".format(projectid,subjectid,sessionid))
                PHASE_2_subjInfoNode[sessionid] = pe.Node(interface=IdentityInterface(fields=
                        ['sessionid','subjectid','projectid',
                         'allT1s',
                         'allT2s',
                         'allPDs',
                         'allFLs',
                         'allOthers']),
                        run_without_submitting=True,
                        name='99_PHASE_2_SubjInfoNode_'+str(subjectid)+"_"+str(sessionid) )
                PHASE_2_subjInfoNode[sessionid].inputs.projectid=projectid
                PHASE_2_subjInfoNode[sessionid].inputs.subjectid=subjectid
                PHASE_2_subjInfoNode[sessionid].inputs.sessionid=sessionid
                PHASE_2_subjInfoNode[sessionid].inputs.allT1s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T1-30','T1-15'])
                PHASE_2_subjInfoNode[sessionid].inputs.allT2s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T2-30','T2-15'])
                PHASE_2_subjInfoNode[sessionid].inputs.allPDs=ExperimentDatabase.getFilenamesByScantype(sessionid,['PD-30','PD-15'])
                PHASE_2_subjInfoNode[sessionid].inputs.allFLs=ExperimentDatabase.getFilenamesByScantype(sessionid,['FL-30','FL-15'])
                PHASE_2_subjInfoNode[sessionid].inputs.allOthers=ExperimentDatabase.getFilenamesByScantype(sessionid,['OTHER-30','OTHER-15'])

                PROCESSING_PHASE='PHASE_2'
                PHASE_2_oneSubjWorkflow[sessionid]=WorkupT1T2Single.MakeOneSubWorkFlow(
                                  projectid, subjectid, sessionid,PROCESSING_PHASE,
                                  WORKFLOW_COMPONENTS,
                                  BCD_model_path, InterpolationMode, CLUSTER_QUEUE)
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'projectid',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.projectid')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'subjectid',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.subjectid')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'sessionid',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.sessionid')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'allT1s',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.allT1s')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'allT2s',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.allT2s')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'allPDs',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.allPDs')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'allFLs',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.allFLs')
                baw200.connect(PHASE_2_subjInfoNode[sessionid],'allOthers',PHASE_2_oneSubjWorkflow[sessionid],'inputspec.allOthers')

                baw200.connect(BAtlas[subjectid],'template_landmarks_31_fcsv', PHASE_2_oneSubjWorkflow[sessionid],'inputspec.template_landmarks_31_fcsv')
                baw200.connect(BAtlas[subjectid],'template_landmark_weights_31_csv', PHASE_2_oneSubjWorkflow[sessionid],'inputspec.template_landmark_weights_31_csv')
                baw200.connect(buildTemplateIteration2,'outputspec.template', PHASE_2_oneSubjWorkflow[sessionid],'inputspec.template_t1')
                baw200.connect(MakeNewAtlasTemplateNode,'outAtlasFullPath', PHASE_2_oneSubjWorkflow[sessionid],'inputspec.atlasDefinition')

                ### Now define where the final organized outputs should go.
                BASIC_DataSink[sessionid]=pe.Node(nio.DataSink(),name="BASIC_DS_"+str(subjectid)+"_"+str(sessionid))
                BASIC_DataSink[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                BASIC_DataSink[sessionid].inputs.regexp_substitutions = GenerateOutputPattern(projectid, subjectid, sessionid,'ACPCAlign')

                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputLandmarksInACPCAlignedSpace',BASIC_DataSink[sessionid],'ACPCAlign.@outputLandmarksInACPCAlignedSpace')
#                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.BCD_ACPC_T1',BASIC_DataSink[sessionid],'ACPCAlign.@BCD_ACPC_T1')
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.BCD_ACPC_T1_CROPPED',BASIC_DataSink[sessionid],'ACPCAlign.@BCD_ACPC_T1_CROPPED')
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputLandmarksInInputSpace',BASIC_DataSink[sessionid],'ACPCAlign.@outputLandmarksInInputSpace')
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputTransform',BASIC_DataSink[sessionid],'ACPCAlign.@outputTransform')
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.LMIatlasToSubjectTransform',BASIC_DataSink[sessionid],'ACPCAlign.@LMIatlasToSubjectTransform')
                #baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.TissueClassifyatlasToSubjectTransform',BASIC_DataSink[sessionid],'ACPCAlign.@TissueClassifyatlasToSubjectTransform')

                ### Now define where the final organized outputs should go.
                TC_DataSink[sessionid]=pe.Node(nio.DataSink(),name="TISSUE_CLASSIFY_DS_"+str(subjectid)+"_"+str(sessionid))
                TC_DataSink[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                TC_DataSink[sessionid].inputs.regexp_substitutions = GenerateOutputPattern(projectid, subjectid, sessionid,'TissueClassify')
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid], 'outputspec.TissueClassifyOutputDir', TC_DataSink[sessionid],'TissueClassify.@TissueClassifyOutputDir')

                ### Now clean up by adding together many of the items PHASE_2_oneSubjWorkflow
                currentAccumulateLikeTissuePosteriorsName='AccumulateLikeTissuePosteriors_'+str(subjectid)+"_"+str(sessionid)
                AccumulateLikeTissuePosteriorsNode[sessionid] = pe.Node(interface=Function(function=AccumulateLikeTissuePosteriors,
                     input_names=['posteriorImages'],
                     output_names=['AccumulatePriorsList','AccumulatePriorsNames']),
                     name=currentAccumulateLikeTissuePosteriorsName)
                baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.posteriorImages',
                               AccumulateLikeTissuePosteriorsNode[sessionid],'posteriorImages')

                ### Now define where the final organized outputs should go.
                AddLikeTissueSink[sessionid]=pe.Node(nio.DataSink(),name="ACCUMULATED_POSTERIORS_"+str(subjectid)+"_"+str(sessionid))
                AddLikeTissueSink[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                #AddLikeTissueSink[sessionid].inputs.regexp_substitutions = GenerateAccumulatorImagesOutputPattern(projectid, subjectid, sessionid)
                AddLikeTissueSink[sessionid].inputs.regexp_substitutions = GenerateOutputPattern(projectid, subjectid, sessionid,'ACCUMULATED_POSTERIORS')
                baw200.connect(AccumulateLikeTissuePosteriorsNode[sessionid], 'AccumulatePriorsList', AddLikeTissueSink[sessionid],'ACCUMULATED_POSTERIORS.@AccumulateLikeTissuePosteriorsOutputDir')

                ClipT1ImageWithBrainMaskNode=dict()
                AtlasToSubjectantsRegistration=dict()
                myLocalSegWF=dict()
                SEGMENTATION_DataSink=dict()
                myLocalFSWF=dict()
                FSPREP_DataSink=dict()
                FS_DS=dict()

                if 'SEGMENTATION' in WORKFLOW_COMPONENTS: ## Run the ANTS Registration from Atlas to Subject for BCut spatial priors propagation.
                    import PipeLineFunctionHelpers

                    ## Second clip to brain tissue region
                    ### Now clean up by adding together many of the items PHASE_2_oneSubjWorkflow
                    currentClipT1ImageWithBrainMaskName='ClipT1ImageWithBrainMask_'+str(subjectid)+"_"+str(sessionid)
                    ClipT1ImageWithBrainMaskNode[sessionid] = pe.Node(interface=Function(function=PipeLineFunctionHelpers.ClipT1ImageWithBrainMask,
                          input_names=['t1_image','brain_labels','clipped_file_name'],
                          output_names=['clipped_file']),
                          name=currentClipT1ImageWithBrainMaskName)
                    ClipT1ImageWithBrainMaskNode[sessionid].inputs.clipped_file_name = 'clipped_from_BABC_labels_t1.nii.gz'
                    baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.t1_average',ClipT1ImageWithBrainMaskNode[sessionid],'t1_image')
                    baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputLabels',ClipT1ImageWithBrainMaskNode[sessionid],'brain_labels')

                    from nipype.interfaces.ants import ( Registration, ApplyTransforms)
                    currentAtlasToSubjectantsRegistration='AtlasToSubjectantsRegistration_'+str(subjectid)+"_"+str(sessionid)
                    AtlasToSubjectantsRegistration[subjectid]=pe.Node(interface=Registration(), name = currentAtlasToSubjectantsRegistration)
                    AtlasToSubjectantsRegistration[subjectid].inputs.dimension = 3
                    AtlasToSubjectantsRegistration[subjectid].inputs.transforms =               ["Rigid",         "Affine",            "SyN"]
                    AtlasToSubjectantsRegistration[subjectid].inputs.transform_parameters =     [[0.1],           [0.1],               [0.15,3.0,0.0]]
                    AtlasToSubjectantsRegistration[subjectid].inputs.metric =                   ['Mattes',        'Mattes',            'CC']
                    AtlasToSubjectantsRegistration[subjectid].inputs.sampling_strategy =        ['Regular',       'Regular',           None]
                    AtlasToSubjectantsRegistration[subjectid].inputs.sampling_percentage =      [0.1,              0.1,                1.0]
                    AtlasToSubjectantsRegistration[subjectid].inputs.metric_weight =            [1.0,              1.0,                1.0]
                    AtlasToSubjectantsRegistration[subjectid].inputs.radius_or_number_of_bins = [32,               32,                 4]
                    AtlasToSubjectantsRegistration[subjectid].inputs.number_of_iterations =     [[2000,2000,2000], [1000, 1000, 1000], [10000,500,500,200]]
                    AtlasToSubjectantsRegistration[subjectid].inputs.convergence_threshold =    [1e-9,             1e-9,               1e-9]
                    AtlasToSubjectantsRegistration[subjectid].inputs.convergence_window_size =  [15,               15,                 15]
                    AtlasToSubjectantsRegistration[subjectid].inputs.use_histogram_matching =   [True,             True,               True]
                    AtlasToSubjectantsRegistration[subjectid].inputs.shrink_factors =           [[4,2,1],          [4,2,1],            [6,4,2,1]]
                    AtlasToSubjectantsRegistration[subjectid].inputs.smoothing_sigmas =         [[4,2,0],          [4,2,0],            [6,4,2,0]]
                    AtlasToSubjectantsRegistration[subjectid].inputs.use_estimate_learning_rate_once = [False,     False,              False]
                    AtlasToSubjectantsRegistration[subjectid].inputs.write_composite_transform=True
                    AtlasToSubjectantsRegistration[subjectid].inputs.output_transform_prefix = 'AtlasToSubject_'

                    baw200.connect(BAtlas[subjectid],'template_t1_clipped',AtlasToSubjectantsRegistration[subjectid], 'moving_image')
                    baw200.connect(ClipT1ImageWithBrainMaskNode[sessionid], 'clipped_file', AtlasToSubjectantsRegistration[subjectid], 'fixed_image')
                    ## To be tested baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.LMIatlasToSubjectTransform',AtlasToSubjectantsRegistration[subjectid],'initial_moving_transform')

                global_AllT1s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T1-30','T1-15'])
                global_AllT2s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T2-30','T2-15'])
                global_AllPDs=ExperimentDatabase.getFilenamesByScantype(sessionid,['PD-30','PD-15'])
                global_AllFLs=ExperimentDatabase.getFilenamesByScantype(sessionid,['FL-30','FL-15'])
                global_AllOthers=ExperimentDatabase.getFilenamesByScantype(sessionid,['OTHER-30','OTHER-15'])
                print("HACK2:  all T1s: {0} {1}".format(global_AllT1s, len(global_AllT1s) ))
                print("HACK2:  all T2s: {0} {1}".format(global_AllT2s, len(global_AllT2s) ))
                print("HACK2:  all PDs: {0} {1}".format(global_AllPDs, len(global_AllPDs) ))
                print("HACK2:  all FLs: {0} {1}".format(global_AllFLs, len(global_AllFLs) ))
                print("HACK2:  all Others: {0} {1}".format(global_AllOthers, len(global_AllOthers) ))
                if ( 'SEGMENTATION' in WORKFLOW_COMPONENTS ) : # Currently only works with multi-modal_data
                    print("HACK SEGMENTATION IN  WORKFLOW_COMPONENTS {0}".format(WORKFLOW_COMPONENTS))
                if ( len(global_AllT2s) > 0 ): # Currently only works with multi-modal_data
                    print("HACK len(global_AllT2s) > 0 : {0}".format(len(global_AllT2s) ))
                print("HACK")
                if ( 'SEGMENTATION' in WORKFLOW_COMPONENTS ) and ( len(global_AllT2s) > 0 ): # Currently only works with multi-modal_data
                    from WorkupT1T2BRAINSCut import CreateBRAINSCutWorkflow
                    myLocalSegWF[sessionid] = CreateBRAINSCutWorkflow(projectid, subjectid, sessionid,'Segmentation',CLUSTER_QUEUE,BAtlas[subjectid]) ##Note:  Passing in the entire BAtlas Object here!
                    baw200.connect( PHASE_2_oneSubjWorkflow[sessionid], 'outputspec.t1_average', myLocalSegWF[sessionid], "inputspec.T1Volume" )
                    baw200.connect( PHASE_2_oneSubjWorkflow[sessionid], 'outputspec.t2_average', myLocalSegWF[sessionid], "inputspec.T2Volume")
                    baw200.connect( PHASE_2_oneSubjWorkflow[sessionid], 'outputspec.outputLabels', myLocalSegWF[sessionid],"inputspec.RegistrationROI")
                    ## NOTE: Element 0 of AccumulatePriorsList is the accumulated GM tissue
                    baw200.connect( [ ( AccumulateLikeTissuePosteriorsNode[sessionid], myLocalSegWF[sessionid], [ (( 'AccumulatePriorsList', getListIndex, 0 ), "inputspec.TotalGM")] ),
                                    ] )
                    baw200.connect( AtlasToSubjectantsRegistration[subjectid],'composite_transform',myLocalSegWF[sessionid],'inputspec.atlasToSubjectTransform')

                    ### Now define where the final organized outputs should go.
                    SEGMENTATION_DataSink[sessionid]=pe.Node(nio.DataSink(),name="SEGMENTATION_DS_"+str(subjectid)+"_"+str(sessionid))
                    SEGMENTATION_DataSink[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                    #SEGMENTATION_DataSink[sessionid].inputs.regexp_substitutions = GenerateOutputPattern(projectid, subjectid, sessionid,'BRAINSCut')
                    #SEGMENTATION_DataSink[sessionid].inputs.regexp_substitutions = GenerateBRAINSCutImagesOutputPattern(projectid, subjectid, sessionid)
                    SEGMENTATION_DataSink[sessionid].inputs.substitutions = [ ( 'BRAINSCut',os.path.join(projectid, subjectid, sessionid,'BRAINSCut') ),
                                                                              ( 'subjectANNLabel_', '' ),
                                                                              ( '.nii.gz', '_seg.nii.gz')
                                                                            ]
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryLeftCaudate',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryLeftCaudate')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryRightCaudate',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryRightCaudate')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryLeftHippocampus',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryLeftHippocampus')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryRightHippocampus',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryRightHippocampus')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryLeftPutamen',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryLeftPutamen')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryRightPutamen',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryRightPutamen')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryLeftThalamus',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryLeftThalamus')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputBinaryRightThalamus',SEGMENTATION_DataSink[sessionid], 'BRAINSCut.@outputBinaryRightThalamus')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputLabelImageName', SEGMENTATION_DataSink[sessionid],'BRAINSCut.@outputLabelImageName')
                    baw200.connect(myLocalSegWF[sessionid], 'outputspec.outputCSVFileName', SEGMENTATION_DataSink[sessionid],'BRAINSCut.@outputCSVFileName')
                else:
                    print("SKIPPING SEGMENTATION PHASE FOR {0} {1} {2}, lenT2s {3}".format(projectid, subjectid, sessionid, len(global_AllT2s) ))


                ## Synthesized images are only valid for 3T where the T2 and T1 have approximately the same resolution.
                global_All3T_T1s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T1-30'])
                global_All3T_T2s=ExperimentDatabase.getFilenamesByScantype(sessionid,['T2-30'])
                RunAllFSComponents=False ## A hack to avoid 26 hour run of freesurfer
                #RunAllFSComponents=True ## A hack to avoid 26 hour run of freesurfer
                if False: #( 'FREESURFER' in WORKFLOW_COMPONENTS ) and ( ( len(global_All3T_T2s) > 0 ) or RunAllFSComponents == True ):
                    from WorkupT1T2FreeSurfer import CreateFreeSurferWorkflow
                    if ( len(global_All3T_T2s) > 0 ): # If multi-modal, then create synthesized image before running
                        print("HACK  FREESURFER len(global_All3T_T2s) > 0 ")
                        myLocalFSWF[sessionid]= CreateFreeSurferWorkflow(projectid, subjectid, sessionid,"Level1_FSTest",
                                                CLUSTER_QUEUE,RunAllFSComponents,True)
                    else:
                        myLocalFSWF[sessionid]= CreateFreeSurferWorkflow(projectid, subjectid, sessionid,"Level1_FSTest",
                                                CLUSTER_QUEUE,RunAllFSComponents,False)
                    FREESURFER_ID[sessionid]= pe.Node(interface=IdentityInterface(fields=['FreeSurfer_ID']),
                                                      run_without_submitting=True,
                                                      name='99_FSNodeName'+str(subjectid)+"_"+str(sessionid) )
                    FREESURFER_ID[sessionid].inputs.FreeSurfer_ID=str(subjectid)+"_"+str(sessionid)

                    baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.t1_average',myLocalFSWF[sessionid],'inputspec.T1_files')
                    baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.t2_average',myLocalFSWF[sessionid],'inputspec.T2_files')
                    baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputLabels',myLocalFSWF[sessionid],'inputspec.label_file')
                    baw200.connect(FREESURFER_ID[sessionid],'FreeSurfer_ID',myLocalFSWF[sessionid],'inputspec.FreeSurfer_ID')
                    #baw200.connect(PHASE_2_oneSubjWorkflow[sessionid],'outputspec.outputLabels',myLocalFSWF[sessionid],'inputspec.mask_file') #Yes, the same file as label_file!

                    ### Now define where the final organized outputs should go.
                    if RunAllFSComponents == True:
                        FS_DS[sessionid]=pe.Node(nio.DataSink(),name="FREESURFER_DS_"+str(subjectid)+"_"+str(sessionid))
                        FS_DS[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                        FS_DS[sessionid].inputs.regexp_substitutions = [
                            ('/_uid_(?P<myuid>[^/]*)',r'/\g<myuid>')
                            ]
                        baw200.connect(myLocalFSWF[sessionid], 'outputspec.FreesurferOutputDirectory', FS_DS[sessionid],'FREESURFER_SUBJ.@FreesurferOutputDirectory')
                    ### Now define where the final organized outputs should go.
                    FSPREP_DataSink[sessionid]=pe.Node(nio.DataSink(),name="FREESURFER_PREP_"+str(subjectid)+"_"+str(sessionid))
                    FSPREP_DataSink[sessionid].inputs.base_directory=ExperimentBaseDirectoryResults
                    FREESURFER_PREP_PATTERNS = GenerateOutputPattern(projectid, subjectid, sessionid,'FREESURFER_PREP')
                    FSPREP_DataSink[sessionid].inputs.regexp_substitutions = FREESURFER_PREP_PATTERNS
                    print "========================="
                    print "========================="
                    print "========================="
                    print FREESURFER_PREP_PATTERNS
                    print "========================="
                    print "========================="
                    print "========================="
                    baw200.connect(myLocalFSWF[sessionid], 'outputspec.cnr_optimal_image', FSPREP_DataSink[sessionid],'FREESURFER_PREP.@cnr_optimal_image')

                else:
                    print "Skipping freesurfer"
    return baw200

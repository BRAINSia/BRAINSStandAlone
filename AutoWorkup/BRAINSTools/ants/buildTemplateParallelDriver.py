from buildtemplateparallel import initAvgWF, mainWF
import nipype.pipeline.engine as pe
import argparse
import nipype.interfaces.utility as util
import textwrap
import os
import sys

def BuildTemplateParallelWorkFlow(ExperimentBaseDirectoryCache, ExperimentBaseDirectoryResults, subject_data_file):

    print "Building Pipeline"
    ########### PIPELINE INITIALIZATION #############
    btp = pe.Workflow( name='buildtemplateparallel')
    btp.config['execution'] = {
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
    btp.config['logging'] = {
          'workflow_level':'DEBUG',
          'filemanip_level':'DEBUG',
          'interface_level':'DEBUG',
          'log_directory': ExperimentBaseDirectoryCache
        }
    btp.base_dir = ExperimentBaseDirectoryCache

    myInitAvgWF = initAvgWF(ExperimentBaseDirectoryCache)
    myMainWF = mainWF(ExperimentBaseDirectoryCache)

    Handle = open(subject_data_file, 'r')
    image_string = Handle.read()
    Handle.close()
    image_list = image_string.strip().split('\n')

    infosource = pe.Node(interface=util.IdentityInterface(fields=['images']), name='infoSource' )
    infosource.inputs.images = image_list

    btp.connect(infosource, 'images', myInitAvgWF, 'InputSpec.images')
    btp.connect(infosource, 'images', myMainWF, 'InputSpec.images')
    btp.connect(myInitAvgWF, 'OutputSpec.average_image', myMainWF, 'InputSpec.fixed_image')

    secondRun = myMainWF.clone(name='secondRun')
    btp.connect(infosource, 'images', secondRun, 'InputSpec.images')
    btp.connect(myMainWF, 'OutputSpec.template', secondRun, 'InputSpec.fixed_image')

    return btp

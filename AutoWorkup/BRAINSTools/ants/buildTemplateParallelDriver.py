from buildtemplateparallel import initAvgWF, mainWF
import nipype.pipeline.engine as pe
import argparse
import nipype.interfaces.utility as util
import textwrap

def BuildTemplateParallelWorkFlow():

    ExperimentBaseDirectoryCache = '/scratch/antsbuildtemplate/TEST_CACHE4'

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
    infosource = pe.Node(interface=util.IdentityInterface(fields=['images']), name='infoSource' )
    infosource.inputs.images = args.inputVolumes

    btp.connect(infosource, 'images', myInitAvgWF, 'InputSpec.images')
    btp.connect(infosource, 'images', myMainWF, 'InputSpec.images')
    btp.connect(myInitAvgWF, 'OutputSpec.average_image', myMainWF, 'InputSpec.fixed_image')

    secondRun = myMainWF.clone(name='secondRun')
    btp.connect(infosource, 'images', secondRun, 'InputSpec.images')
    btp.connect(myMainWF, 'OutputSpec.template', secondRun, 'InputSpec.fixed_image')

    #btp.run(plugin='MultiProc', plugin_args={'n_procs' : 3})

    btp.write_graph(graph2use='hierarchical')
    #btp.write_graph(graph2use='exec')

if __name__ == "__main__":
    # Create and parse input arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent("""
  This program is used to generate a template image from initial images using
  the ANTS build template parallel scheme. \n

Common Usage:
  $ python buildTemplateParallelDriver.py -i
  /hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/01_T1_half.nii.gz
  /hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/02_T1_half.nii.gz
  /hjohnson/HDNI/ANTS_TEMPLATE_BUILD/run_dir/03_T1_half.nii.gz
 \n
"""))
    #parser.add_argument('-o', '--outputVolume', dest='outputVolume', help='The ANTS template output volume.')
    parser.add_argument('-i', '--inputVolumes', nargs='*', dest='inputVolumes', help='The ANTS template input volumes.')
    args = parser.parse_args()
    BuildTemplateParallelWorkFlow()

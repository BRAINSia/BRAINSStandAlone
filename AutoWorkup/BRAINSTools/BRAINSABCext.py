from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from BRAINSABC import BRAINSABCOutputSpec,BRAINSABC

from xml.etree import ElementTree as et
class GetPosteriorsFromAtlasXML():
    
    def __init__(self, xmlFile):
        self.xmlFile = xmlFile
        self.xmlString = self.getXMLstring(self.xmlFile)
        self.priorTypeNameList = self.getPriorTypeNameList(xmlString)
    
    def main(self):
        self.getPosteriorFileNameList(priorTypeNameList)
    
    def getXMLstring(self, xmlFile):
        Handle = open(xmlFile)
        xmlString = Handle.read()
        Handle.close()
        return xmlString
    
    def getPriorTypeNameList(self, xmlString):
        myelem = et.fromstring(xmlString)
        elementsList = myelem.getiterator()
        iterator = range(len(elementsList))
        priorTypeNameList = list()
        for i in iterator:
            ## the Prior type is the next item in elementsList after a Prior tag:
            if elementsList[i].tag == "Prior" and elementsList[i + 1].tag == "type":
                priorTypeNameList.append(elementsList[i + 1].text)
        return priorTypeNameList

    def getPosteriorFileNameList(self, priorTypeNameList):
        posteriorFileNameList = list()
        for priorType in priorTypeNameList:
            posteriorFileNameList.append("POSTERIOR_{priorT}.nii.gz".format(priorT=priorType))
        return posteriorFileNameList
    

class BRAINSABCextOutputSpec(BRAINSABCOutputSpec):
    outputDir = Directory( exists = True)
    atlasToSubjectTransform = File( exists = True)
    atlasToSubjectInitialTransform = File( exists = True)
    outputVolumes = OutputMultiPath(File(exists=True), exists = True)
    outputLabels = File( exists = True)
    outputDirtyLabels = File( exists = True)
    implicitOutputs = OutputMultiPath(File(exists=True), exists = True)
    outputAverageImages = OutputMultiPath(File(exists=True), exists = True)

class BRAINSABCext(BRAINSABC):
    output_spec = BRAINSABCextOutputSpec

    def _list_outputs(self):
        outputs=super(BRAINSABCext)._list_outputs()
        
        ### HACK:  this is a quick hack for now
        templist=[]
        if 'T1' in self.inputs.inputVolumeTypes:
            templist.append('t1_average.nii.gz')
        if 'T2' in self.inputs.inputVolumeTypes:
            templist.append('t2_average.nii.gz')
        if 'FL' in self.inputs.inputVolumeTypes:
            templist.append('fl_average.nii.gz')
        outputs['outputAverageImages'] = templist
        ##  outputs['outputAverageImages'] = [ os.path.abspath('{imageType}_average.nii.gz'.format(imageType=test)) for test in set(self.inputs.inputVolumeTypes) ]

        PosteriorOutputs = GetPosteriorsFromAtlasXML(inputArguments.xmlFile)
        outputs['posteriorImages']= PosteriorOutputs.getPosteriorFileNameList()
        return outputs

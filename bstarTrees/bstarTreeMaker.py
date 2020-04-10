#!/usr/bin/env python
import os, sys, math, subprocess, fnmatch, tempfile
from optparse import OptionParser

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
#from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *#UncertaintiesFactorized import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
# import add_DAK8
# from add_DAK8 import *

parser = OptionParser()
parser.add_option('-s', '--set', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'set',
                help      =   'Set name')
parser.add_option('-j', '--job', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'job',
                help      =   'Job number')
parser.add_option('-n', '--njobs', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'njobs',
                help      =   'Number of jobs')
parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')

(options, args) = parser.parse_args()

# Setup setname
setname = options.set
if setname == None:
    print 'Setname not given to PostProcessor. Quitting'
    quit()

# Setup modules to use
isMC = False if 'data' in setname else True
year = '20' + options.year
if not isMC: period = setname.split('data')[1][0]
else: period = False
jesUncertainty = "Total"
redojec = True
jettype = "AK8PFPuppi"

corrector = createJMECorrector(isMC, year, period, jesUncertainty, redojec, jettype)

if not isMC: mymodules = [corrector()]
else:
    if options.year == '16': mymodules =  [corrector(),puAutoWeight_2016(),PrefCorr_2016()]
            
    elif options.year == '17': mymodules = [corrector(),puAutoWeight_2017(),PrefCorr_2017()]

    elif options.year == '18': mymodules = [corrector(),puAutoWeight_2018()]

    else:
        raise ValueError('ERROR: '+ options.year+' not supported yet.')

# Setup possible job splitting 
ijob = int(options.job)
njobs = int(options.njobs)

# Open list of all files for this set
list_of_files = open('NanoAOD'+options.year+'_lists/'+setname+'_loc.txt','r').readlines()
new_list = []
nfiles = len(list_of_files)

# Check there aren't more jobs than files
if njobs > nfiles:
    print "ERROR: More jobs than files (%i jobs, %i files)" %(njobs,nfiles)
    quit() 

# Creating the splitting
split_start = (ijob-1)*int(math.floor(float(nfiles)/float(njobs)))
if ijob != njobs:
    split_end = split_start+int(math.floor(float(nfiles)/float(njobs)))
else:
    split_end = nfiles

print 'Splitting into '+str(njobs)+ ' jobs - Indices ['+ str(split_start)+':'+str(split_end)+']'

# Only grab the files in the spliti
tempfolder = tempfile.mkdtemp()
for l in list_of_files[split_start:split_end]:
    n = l.rstrip('\n')
    #if options.year == '17':
    #if not (options.year == '16' and 'signal' in options.set):
    #    n = 'root://cms-xrd-global.cern.ch/'+n 
    #if options.year == '18' and options.set == 'dataB' and ijob == 85:
    #    n = 'rawNano_dataB_18_85-93.root'
    file_name = n.split('/')[-1]
    if '/store/user' not in n:
        full_path = 'root://cms-xrd-global.cern.ch/'+n
    else:
        full_path = n
    print 'xrdcp '+full_path+' '+tempfolder+'/'+file_name
    subprocess.call('xrdcp '+full_path+' '+tempfolder+'/'+file_name,shell=True)
    new_list.append(tempfolder+'/'+file_name)

output_dir = setname+'-'+options.year+'_'+str(ijob)+'-'+str(njobs)
hadded_file = "bstarTrees"+options.year+"_"+setname+'_'+str(ijob)+'-'+str(njobs)+'.root'
cutstring = "(FatJet_pt[0]>350)&&(FatJet_pt[1]>350)&&(FatJet_eta[0]<2.5)&&(FatJet_eta[1]<2.5)"
# Postprocessor
if (split_end - split_start) > 1:
    p=PostProcessor(output_dir+'/',new_list,
                cutstring,
                branchsel='keep_and_drop'+options.year+'.txt',
                outputbranchsel='keep_and_drop'+options.year+'.txt',
                modules=mymodules,
                provenance=True,haddFileName=hadded_file)#,fwkJobReport=True,jsonInput=runsAndLumis())
# Need to skip haddnano step if there's only one file processed
else:
    p=PostProcessor(output_dir+'/',new_list,
                cutstring,
                branchsel='keep_and_drop'+options.year+'.txt',
                outputbranchsel='keep_and_drop'+options.year+'.txt',
                modules=mymodules,
                provenance=True)

p.run()

print "DONE"
#os.system("ls -lR")

# If only one file, change the name to the name it would've taken if hadded
if (split_end - split_start) == 1 and len(fnmatch.filter(os.listdir(output_dir), '*.root')) == 1:
    print "mv "+output_dir+'/*.root '+hadded_file
    subprocess.call(["mv "+output_dir+'/*.root '+hadded_file], shell=True)    
    
subprocess.call(["xrdcp -f "+hadded_file+" root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/"+hadded_file], shell=True)

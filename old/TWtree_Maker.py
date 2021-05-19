#! /usr/bin/env python



###################################################################
##								 ##
## Name: TWrate.py						 ##
## Author: Kevin Nash 						 ##
## Date: 6/5/2012						 ##
## Purpose: This program creates eta binned tags and probes 	 ##
##          as a function of Pt for data and MC for use with 	 ##
##          TWrate_Maker.py.					 ##
##								 ##
###################################################################

import os
import glob
import math
from math import sqrt,exp, log
import ROOT
from ROOT import std,ROOT,TFile,TLorentzVector,TMath,gROOT, TF1,TH1F,TH1D,TH2F,TH2D,TTree
from ROOT import TVector
from ROOT import TFormula

import sys
from DataFormats.FWLite import Events, Handle
from optparse import OptionParser
from array import *


parser = OptionParser()

parser.add_option('-s', '--set', metavar='F', type='string', action='store',
				  default	=	'data',
				  dest		=	'set',
				  help		=	'dataset (ie data,ttbar etc)')
parser.add_option('-J', '--JES', metavar='F', type='string', action='store',
				  default	=	'nominal',
				  dest		=	'JES',
				  help		=	'nominal, up, or down')
parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
				  default	=	'nominal',
				  dest		=	'JER',
				  help		=	'nominal, up, or down')
parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
				  default	=	'nominal',
				  dest		=	'JMS',
				  help		=	'nominal, up, or down')
parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
				  default	=	'nominal',
				  dest		=	'JMR',
				  help		=	'nominal, up, or down')
parser.add_option('-t', '--tname', metavar='F', type='string', action='store',
				   default	=	'HLT_PFHT900,HLT_PFHT800,HLT_AK8PFJet450',
				   dest		=	'tname',
				   help		=	'trigger name')
# parser.add_option('-y', '--modmass', metavar='F', type='string', action='store',
# 				  default	=	'nominal',
# 				  dest		=	'modmass',
# 				  help		=	'nominal up or down')
# parser.add_option('-p', '--pdfweights', metavar='F', type='string', action='store',
# 				  default	=	'nominal',
# 				  dest		=	'pdfweights',
# 				  help		=	'nominal, up, or down')
parser.add_option('-x', '--pileup', metavar='F', type='string', action='store',
				  default	=	'on',
				  dest		=	'pileup',
				  help		=	'If not data do pileup reweighting?')
parser.add_option('-g', '--grid', metavar='F', type='string', action='store',
				  default	=	'off',
				  dest		=	'grid',
				  help		=	'running on grid off or on')
parser.add_option('-m', '--modulesuffix', metavar='F', type='string', action='store',
				  default	=	'none',
				  dest		=	'modulesuffix',
				  help		=	'ex. PtSmearUp')
parser.add_option('-n', '--num', metavar='F', type='string', action='store',
                  default	=	'all',
                  dest		=	'num',
                  help		=	'job number')
parser.add_option('-j', '--jobs', metavar='F', type='string', action='store',
                  default	=	'1',
                  dest		=	'jobs',
                  help		=	'number of jobs')
parser.add_option('-S', '--split', metavar='F', type='string', action='store',
                  default	=	'file',
                  dest		=	'split',
                  help		=	'split by event of file') #EVENT SPLITTING DOESN'T CURRENTLY WORK

(options, args) = parser.parse_args()

#------------------Jet energy mods--------------------------------
# Post2 is used for softdrop mass (JMR/S), post is used for LV (JER/S)
mod = ''
post = ''
post2 = ''
if options.JES!='nominal':
	mod = mod + 'JES' + '_' + options.JES
	post='jes'+options.JES
if options.JER!='nominal':
	mod = mod + 'JER' + '_' + options.JER
	post='jer'+options.JER
if options.JMS!='nominal':
	mod = mod + 'JMS' + '_' + options.JMS
	post2='jes'+options.JMS
if options.JMR!='nominal':
	mod = mod + 'JMR' + '_' + options.JMR
	post2='jer'+options.JMR


#--------------------- Trigger------------------------------------
# We check that the data passes the trigger
tname = options.tname.split(',')
tnamestr = ''
for iname in range(0,len(tname)):
	tnamestr+=tname[iname]
	if iname!=len(tname)-1:
		tnamestr+='OR'
		
trig='none'
if options.set!= 'data' and options.tname!='none': 
	if options.tname=='HLT_PFHT900,HLT_AK8PFJet450':
		trig = 'nominal'
	elif options.tname!= []:
		trig = 'tnamestr'
		
if tnamestr=='HLT_PFHT900ORHLT_PFHT800ORHLT_AK8PFJet450':
	tnameformat='nominal'
elif tnamestr=='':
	tnameformat='none'
else:
	tnameformat=tnamestr
#----------- PDFs - Removed since it's auto on----------------------
# Currently commented out since we don't use it
pstr = ""
# if options.pdfweights!="nominal":
# 	print "using pdf uncertainty"
# 	pstr = "_pdf_"+options.pdfset+"_"+options.pdfweights

#---------------------Pileup----------------------------------------
# Need to grab a pileBin for each hemi
pustr = ""
if options.pileup=='off':
	pustr = "pileup_unweighted"
if options.pileup=='up':
	pustr = "pileup_up"
if options.pileup=='down':
	pustr = "pileup_down"
mod = mod+pustr
if mod == '':
	mod = options.modulesuffix

print "mod = " + mod

#---------------------Mod mass----------------------------------------
# Not used because a mod mass plot hasn't been made yet!
# mmstr = ""
# if options.modmass!="nominal":
# 	print "using modm uncertainty"
# 	mmstr = "_modm_"+options.modmass
#------------------------------------------------------------------------
#If running on the grid we access the script within a tarred directory
di = ""
if options.grid == 'on':
	di = "tardir/"
	sys.path.insert(0, 'tardir/')

gROOT.Macro(di+"rootlogon.C")
import Bstar_Functions	
from Bstar_Functions import *

import Bstar_Functions_EDM	
from Bstar_Functions_EDM import *


jobs=int(options.jobs)
if jobs != 1:
	num=int(options.num)
	jobs=int(options.jobs)
	print "Running over " +str(jobs)+ " jobs"
	print "This will process job " +str(num)
else:
	print "Running over all events"

#Based on what set we want to analyze, we find all Ntuple root files 

files = Load_Ntuples(options.set,di)


# We select all the events:    
events = Events (files)

#For event counting
jobiter = 0
splitfiles = []

if jobs != 1 and options.split=="file":
	for ifile in range(1,len(files)+1):
		if (ifile-1) % jobs == 0:
			jobiter+=1
		count_index = ifile  - (jobiter-1)*jobs
		if count_index==num:
			splitfiles.append(files[ifile-1])

	events = Events(splitfiles)
	runs = Runs(splitfiles)

if options.split=="event" or jobs == 1:	  
	events = Events(files)
	runs = Runs(files)



nevHandle 	= 	Handle (  "vector<int> "  )
nevLabel  	= 	( "counter" , "nevr")

totnev = 0
for run in runs:
	run.getByLabel (nevLabel,nevHandle )
	nev 		= 	nevHandle.product() 
	totnev+=nev[0]
print "Total unfiltered events in selection: ",totnev


#Here we load up handles and labels.
#These are used to grab entries from the Ntuples.
#To see all the current types in an Ntuple use edmDumpEventContent /PathtoNtuple/Ntuple.root

AK8HL = Initlv("jetsAK8",post)

looseJetIDHandle = Handle("vector<float>")
looseJetIDLabel = ("jetsAK8", "jetAK8PuppiLoose")

filtersHandle = Handle("vector<bool>")
filtersLabel = ('Filter','filtersbit')

GenHandle 	= 	Handle (  "vector<reco::GenParticle>")
GenLabel  	= 	( "filteredPrunedGenParticles" , "")

flavorHandle = Handle("vector<float>")
flavorLabel = ('jetsAK8','jetAK8PuppiPartonFlavour')

puHandle    	= 	Handle("int")
puLabel     	= 	( "eventUserData", "puNtrueInt" )

pdfHandle = Handle("vector<float>")
pdfLabel = ("weights","pdfWeights")

topMassHandle		=	Handle (  "vector<float> "  )
topMassLabel		=	( "jetsAK8"+post2 , "jetAK8PuppisoftDropMassForTopPUPPIAK8JEC")

wMassHandle		= Handle("vector<float>")
wMassLabel		= ( "jetsAK8"+post2 , "jetAK8PuppiCorrectedsoftDropMass")

vsubjets0indexHandle 	= 	Handle (  "vector<float> "  )
vsubjets0indexLabel  	= 	( "jetsAK8", "jetAK8PuppivSubjetIndex0")

vsubjets1indexHandle 	= 	Handle (  "vector<float> "  )
vsubjets1indexLabel  	= 	( "jetsAK8", "jetAK8PuppivSubjetIndex1")

subjetsAK8CSVHandle 	= 	Handle (  "vector<float> "  )
subjetsAK8CSVLabel  	= 	( "subjetsAK8Puppi" , "subjetAK8PuppiCSVv2")

tau1Handle 	= 	Handle (  "vector<float> "  )
tau1Label  	= 	( "jetsAK8" , "jetAK8Puppitau1")

tau2Handle 	= 	Handle (  "vector<float> "  )
tau2Label  	= 	( "jetsAK8" , "jetAK8Puppitau2")

tau3Handle 	= 	Handle (  "vector<float> "  )
tau3Label  	= 	( "jetsAK8" , "jetAK8Puppitau3")

HT800Handle	=	Handle ( "vector<bool>" )
HT800Label	=	( "Filter" , "HT800bit" )

HT900Handle = Handle ( "vector<bool>" )
HT900Label = ("Filter", "HT900bit")

JET450Handle	=	Handle ( "vector<bool>" )
JET450Label = ("Filter","JET450bit")


#---------------------------------------------------------------------------------------------------------------------#

#Create the output file
if jobs != 1:
	f = TFile( "TWtreefile_"+options.set+"_Trigger_"+tnameformat+"_"+mod+pstr+"_job"+options.num+"of"+options.jobs+".root", "recreate" )
else:
	f = TFile( "TWtreefile_"+options.set+"_Trigger_"+tnameformat+"_"+mod+pstr+".root", "recreate" )


f.cd()
nev = TH1F("nev",	"nev",		1, 0, 1 )
nev.SetBinContent(1,totnev)


#---------------------------------------------------------------------------------------------------------------------#

# loop over events
#---------------------------------------------------------------------------------------------------------------------#

count = 0
passedNev = 0
print "Start looping"
#initialize the ttree variables
#Only store nev in regular tree now
# Commented out since it's stored in a histo
# tree_vars = {"nev":array('d',[totnev])}#,"nsubjets":array('d',[0.])
# Tree = Make_Trees(tree_vars)
# Tree.Fill()

# totevents = events.size()
# print "Total events in slim form: " + str(totevents)

# This tree is done now

# Now book a tree for each of the jets (leading and subleading) 
# These jets can be identified based on hemisphere. Hemi0 has the leading jet
treeVars = {
	"topSDmass_leading":array('d',[0]),
	"wSDmass_leading":array('d',[0]),
	"tau1_leading":array('d',[0]),
	"tau2_leading":array('d',[0]),
	"tau3_leading":array('d',[0]),
	"sjbtag_leading":array('d',[0]),
	"pt_leading":array('d',[0]),
	"eta_leading":array('d',[0]),
	"phi_leading":array('d',[0]),
	"mass_leading":array('d',[0]),
	"flavor_leading":array('d',[0]),

	"topSDmass_subleading":array('d',[0]),
	"wSDmass_subleading":array('d',[0]),
	"tau1_subleading":array('d',[0]),
	"tau2_subleading":array('d',[0]),
	"tau3_subleading":array('d',[0]),
	"sjbtag_subleading":array('d',[0]),
	"pt_subleading":array('d',[0]),
	"eta_subleading":array('d',[0]),
	"phi_subleading":array('d',[0]),
	"mass_subleading":array('d',[0]),
	"flavor_subleading":array('d',[0]),

	"topSDmass_subsubleading":array('d',[0]),
	"wSDmass_subsubleading":array('d',[0]),
	"tau1_subsubleading":array('d',[0]),
	"tau2_subsubleading":array('d',[0]),
	"tau3_subsubleading":array('d',[0]),
	"pt_subsubleading":array('d',[0]),
	"eta_subsubleading":array('d',[0]),
	"phi_subsubleading":array('d',[0]),
	"mass_subsubleading":array('d',[0]),
	"flavor_subsubleading":array('d',[0]),

	"WJetMatchingRequirement":array('i',[0])
	}

Tree = TTree("Tree", "Tree")
for v in treeVars.keys():
	if v == 'WJetMatchingRequirement':
		Tree.Branch(v, treeVars[v], v+"/I")
	else:
		Tree.Branch(v, treeVars[v], v+"/D")
Tree.AutoSave("Overwrite")

# Initialize some set specific branches
if options.set != 'data':
	treeVars['pileBin'] = array('i',[0])
	Tree.Branch('pileBin',treeVars['pileBin'],'pileBin/I')

	if options.set.find("singletop_tW") == -1:
		treeVars['pdf_weightUp'] = array('d',[0])
		treeVars['pdf_weightDown'] = array('d',[0])
		Tree.Branch('pdf_weightUp',treeVars['pdf_weightUp'],'pdf_weightUp/D')
		Tree.Branch('pdf_weightDown',treeVars['pdf_weightDown'],'pdf_weightDown/D')


if options.set.find('ttbar') != -1:
	treeVars['pt_reweight'] = array('d',[0])
	Tree.Branch('pt_reweight',treeVars['pt_reweight'],'pt_reweight/D')

# Grab pilefile and plot if not data
if options.set != 'data':
	PileFile = TFile(di+"PileUp_Ratio_ttbar.root")
	if options.pileup=='up':
		PilePlot = PileFile.Get("Pileup_Ratio_up")
	elif options.pileup=='down':
		PilePlot = PileFile.Get("Pileup_Ratio_down")
	else:	
		PilePlot = PileFile.Get("Pileup_Ratio")

# Now we can loop
# We check for the trigger on data, do pt cuts on the jets, and eta cuts
jfailCount = 0
ffailCount = 0
subsubleadingCount = 0
for event in events:
	count	= 	count + 1

	if count % 10000 == 0 :
	  print  '--------- Processing Event ' + str(count) #+'   -- percent complete ' + str(100*count/totevents) + '% -- '
	
	# Need to ask Kevin about the indices here
	if options.set == 'data':
		event.getByLabel (HT900Label, HT900Handle)
		HT900bit = HT900Handle.product()
		event.getByLabel (HT800Label, HT800Handle)
		HT800bit = HT800Handle.product()
		event.getByLabel (JET450Label, JET450Handle)
		JET450bit = JET450Handle.product()

		try:
			trigbits = [JET450bit[-1],HT900bit[-1],HT800bit[-1]]
		except:
			trigbits = [HT800bit[-1],HT900bit[-1]]

		passt = False
		for t in trigbits:
			if t:
				passt = True
		if not passt:
			continue

	AK8LV = Makelv(AK8HL,event)

	# Do some quick basic checks
	if len(AK8LV)==0:
		continue

	event.getByLabel(looseJetIDLabel, looseJetIDHandle)
	looseJetID = looseJetIDHandle.product()

	looseJetIDFailed = 0
	for i in range(2):
		try:
			if looseJetID[i] != 1.0:
				looseJetIDFailed += 1
		except:
			continue

	if looseJetIDFailed > 0:
		#print str(looseJetIDFailed) + " looseJetIDs failed"
		jfailCount += 1
		continue

	event.getByLabel(filtersLabel, filtersHandle)
	filters = filtersHandle.product()

	filterFails = 0
	for thisFilter in filters:
	 	if not thisFilter:
	 		filterFails += 1
	 		
	if filterFails > 0:
		#print str(filterFails)+ " filters failed"
		ffailCount += 1
		continue

	# Only need one of these since they are identical
	tindex,windex = Hemispherize(AK8LV,AK8LV)
	index = tindex

	Jetsh1=[]
	Jetsh0=[]
	
	for i in range(0,len(index[1])):
		Jetsh1.append(AK8LV[index[1][i]])
	for i in range(0,len(index[0])):
		Jetsh0.append(AK8LV[index[0][i]])
	
	jh0 = 0
	jh1 = 0
	
	#Require 1 pt>400 jet in each hemisphere
	for jet in Jetsh0:
		if jet.Perp() > 400.0:
			jh0+=1
	for jet in Jetsh1:
		if jet.Perp() > 400.0:
			jh1+=1

	njetsBit 	= 	((jh1 >= 1) and (jh0 >= 1))


	if njetsBit:
		leadingJet = Jetsh0[0]
		subleadingJet = Jetsh1[0]

		leadingIndexVal = index[0][0]
		subleadingIndexVal = index[1][0]

		# MANUAL HT CUT -- TAKE OUT WHEN TRIGGER CORRECTION FINALIZED
		ht = leadingJet.Perp() + subleadingJet.Perp()
		# if ht < 1100.0:
		# 	continue


		if abs(leadingJet.Eta())<2.40 and abs(subleadingJet.Eta())<2.40:
			# Grab ntuple value vectors
			event.getByLabel (topMassLabel, topMassHandle)
			topJetMass 	= 	topMassHandle.product()

			event.getByLabel (wMassLabel, wMassHandle)
			wJetMass 	= 	wMassHandle.product()

			event.getByLabel (flavorLabel, flavorHandle)
			flavor = flavorHandle.product()

			event.getByLabel (tau3Label, tau3Handle)
			Tau3		= 	tau3Handle.product() 

			event.getByLabel (tau2Label, tau2Handle)
			Tau2		= 	tau2Handle.product() 

			event.getByLabel (tau1Label, tau1Handle)
			Tau1		= 	tau1Handle.product() 

			event.getByLabel (vsubjets0indexLabel,vsubjets0indexHandle )
			vsubjets0index 		= 	vsubjets0indexHandle.product() 

			event.getByLabel (vsubjets1indexLabel,vsubjets1indexHandle )
			vsubjets1index 		= 	vsubjets1indexHandle.product() 

			event.getByLabel (subjetsAK8CSVLabel,subjetsAK8CSVHandle )
			subjetsAK8CSV		= 	subjetsAK8CSVHandle.product() 

			WJetMatchingRequirement = 0
			if options.set != 'data':
				event.getByLabel ( GenLabel, GenHandle )
				GenParticles = GenHandle.product()

				WJetMatchingRequirement = WJetMatching(GenParticles)

			# print 'WJetMatchingRequirement is ' + str(WJetMatchingRequirement)

			if len(subjetsAK8CSV)==0:
				continue
			if len(subjetsAK8CSV)<2:
				leadSJ_csvvals = [subjetsAK8CSV[int(vsubjets0index[leadingIndexVal])]]
				subSJ_csvvals = [subjetsAK8CSV[int(vsubjets0index[subleadingIndexVal])]]
			else:
				leadSJ_csvvals = [subjetsAK8CSV[int(vsubjets0index[leadingIndexVal])],subjetsAK8CSV[int(vsubjets1index[leadingIndexVal])]]
				subSJ_csvvals = [subjetsAK8CSV[int(vsubjets0index[subleadingIndexVal])],subjetsAK8CSV[int(vsubjets1index[subleadingIndexVal])]]


			if leadSJ_csvvals != [] and subSJ_csvvals != []: #added this because files with no SJ_csvvals would cause the entire thing to fail			
				leadSJ_csvmax = max(leadSJ_csvvals)
				subSJ_csvmax = max(subSJ_csvvals)


				if len(AK8LV) > 2:
					subsubleadingJet = AK8LV[2]
					subsubleadingIndexVal = 2

					subsubleadingCount +=1

					Temp_vars = {
						"topSDmass_leading":topJetMass[leadingIndexVal],
						"wSDmass_leading":wJetMass[leadingIndexVal],
						"tau1_leading":Tau1[leadingIndexVal],
						"tau2_leading":Tau2[leadingIndexVal],
						"tau3_leading":Tau3[leadingIndexVal],		
						"sjbtag_leading":leadSJ_csvmax,
						"pt_leading":leadingJet.Perp(),
						"eta_leading":leadingJet.Eta(),
						"phi_leading":leadingJet.Phi(),
						"mass_leading":leadingJet.M(),
						"flavor_leading":flavor[leadingIndexVal],

						"topSDmass_subleading":topJetMass[subleadingIndexVal],
						"wSDmass_subleading":wJetMass[subleadingIndexVal],
						"tau1_subleading":Tau1[subleadingIndexVal],
						"tau2_subleading":Tau2[subleadingIndexVal],
						"tau3_subleading":Tau3[subleadingIndexVal],		
						"sjbtag_subleading":subSJ_csvmax,
						"pt_subleading":subleadingJet.Perp(),
						"eta_subleading":subleadingJet.Eta(),
						"phi_subleading":subleadingJet.Phi(),
						"mass_subleading":subleadingJet.M(),
						"flavor_subleading":flavor[subleadingIndexVal],

						"topSDmass_subsubleading":topJetMass[subsubleadingIndexVal],
						"wSDmass_subsubleading":wJetMass[subsubleadingIndexVal],
						"tau1_subsubleading":Tau1[subsubleadingIndexVal],
						"tau2_subsubleading":Tau2[subsubleadingIndexVal],
						"tau3_subsubleading":Tau3[subsubleadingIndexVal],		
						"pt_subsubleading":subsubleadingJet.Perp(),
						"eta_subsubleading":subsubleadingJet.Eta(),
						"phi_subsubleading":subsubleadingJet.Phi(),
						"mass_subsubleading":subsubleadingJet.M(),
						"flavor_subsubleading":flavor[subsubleadingIndexVal],

						"WJetMatchingRequirement":WJetMatchingRequirement}
				else:

					Temp_vars = {
						"topSDmass_leading":topJetMass[leadingIndexVal],
						"wSDmass_leading":wJetMass[leadingIndexVal],
						"tau1_leading":Tau1[leadingIndexVal],
						"tau2_leading":Tau2[leadingIndexVal],
						"tau3_leading":Tau3[leadingIndexVal],		
						"sjbtag_leading":leadSJ_csvmax,
						"pt_leading":leadingJet.Perp(),
						"eta_leading":leadingJet.Eta(),
						"phi_leading":leadingJet.Phi(),
						"mass_leading":leadingJet.M(),
						"flavor_leading":flavor[leadingIndexVal],

						"topSDmass_subleading":topJetMass[subleadingIndexVal],
						"wSDmass_subleading":wJetMass[subleadingIndexVal],
						"tau1_subleading":Tau1[subleadingIndexVal],
						"tau2_subleading":Tau2[subleadingIndexVal],
						"tau3_subleading":Tau3[subleadingIndexVal],		
						"sjbtag_subleading":subSJ_csvmax,
						"pt_subleading":subleadingJet.Perp(),
						"eta_subleading":subleadingJet.Eta(),
						"phi_subleading":subleadingJet.Phi(),
						"mass_subleading":subleadingJet.M(),
						"flavor_subleading":flavor[subleadingIndexVal],

						"topSDmass_subsubleading":0,
						"wSDmass_subsubleading":0,
						"tau1_subsubleading":0,
						"tau2_subsubleading":0,
						"tau3_subsubleading":0,		
						"pt_subsubleading":0,
						"eta_subsubleading":0,
						"phi_subsubleading":0,
						"mass_subsubleading":0,
						"flavor_subsubleading":0,

						"WJetMatchingRequirement":WJetMatchingRequirement}


				# Get pileup info if not data
				if options.set != 'data':
					event.getByLabel (puLabel, puHandle)
					PileUp 		= 	puHandle.product()
					Temp_vars['pileBin'] = PilePlot.FindBin(PileUp[0])

					# Missing weights from singletop_tW(B) because of slimtuple reason
					if options.set.find("singletop_tW") == -1:
						event.getByLabel( pdfLabel, pdfHandle )
						pdfs = pdfHandle.product()
						if len(pdfs) <= 0:
							print "pdfs empty"
						PDF_weightUp = PDF_Lookup( pdfs , 'up' )
						PDF_weightDown = PDF_Lookup( pdfs , 'down' )	

						Temp_vars['pdf_weightUp'] = PDF_weightUp
						Temp_vars['pdf_weightDown'] = PDF_weightDown
				

				if options.set.find('ttbar') != -1:
					# For pt reweighting
					PTW = PTW_Lookup( GenParticles )
					Temp_vars['pt_reweight'] = PTW

				passedNev += 1

				for key in treeVars.keys():
					treeVars[key][0] = Temp_vars[key]
				# try:
				Tree.Fill()
				# except:
					# print "Failure at " + str(count)

print "Events in slim form: " + str(count)
print "Events that passed: " + str(passedNev)
print "Percent lost to JetID: " + str(float(jfailCount)/float(count))
print "Percent lost to filters: " + str(float(ffailCount)/float(count))
print "3rd jet count in passed selection: " + str(subsubleadingCount)

f.cd()
f.Write()
f.Close()

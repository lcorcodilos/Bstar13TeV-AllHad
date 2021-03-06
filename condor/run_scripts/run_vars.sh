#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/10XwithNano.tgz ./
export SCRAM_ARCH=slc6_amd64_gcc700
scramv1 project CMSSW CMSSW_10_2_13
tar xzf 10XwithNano.tgz
rm 10XwithNano.tgz

mkdir tardir; cp tarball.tgz tardir/; cd tardir
tar xzvf tarball.tgz
mkdir CMSSW_10_2_13/src/BStar13TeV/
cp -r * ../CMSSW_10_2_13/src/BStar13TeV/
cd ../CMSSW_10_2_13/src/BStar13TeV/
eval `scramv1 runtime -sh`

echo make_nminusone.py $*
python make_nminusone.py $* #-s $1 -r $2 -d $3 -n $4 -j $5
cp TWvariables*.root ../../../


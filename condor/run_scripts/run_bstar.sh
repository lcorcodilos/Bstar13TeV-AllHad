#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/10XwithNano.tgz ./
export SCRAM_ARCH=slc6_amd64_gcc700
scramv1 project CMSSW CMSSW_10_2_13
tar -xzf 10XwithNano.tgz
rm 10XwithNano.tgz

mkdir CMSSW_10_2_13/src/BStar13TeV
mkdir CMSSW_10_2_13/src/BStar13TeV/bstarTrees
mkdir tardir; cp tarball.tgz tardir/; cd tardir
tar -xzvf tarball.tgz
cp -r bstarTrees/* ../CMSSW_10_2_13/src/BStar13TeV/bstarTrees/
cd ../CMSSW_10_2_13/src/BStar13TeV/bstarTrees
echo ls bstarTrees/
ls -trlh
eval `scramv1 runtime -sh`

echo bstarTreeMaker.py $*
python bstarTreeMaker.py $*

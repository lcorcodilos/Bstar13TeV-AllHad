#! /bin/sh
tar czvf tarball.tgz env4condor.csh run_bstar.sh bstarTreeMaker.py #bstarTrees/keep_and_drop.txt bstarTrees/JHitos16_lists/*_loc.txt 
./development/runManySections.py --createCommandFile --envString "mv tardir/env4condor.csh ./; source env4condor.csh" --addLog --setTarball=tarball.tgz \treeMaker.listOfJobs commands.cmd
./runManySections.py --submitCondor commands.cmd
condor_q lcorcodi

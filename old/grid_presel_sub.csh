#! /bin/sh
tar czvf tarball.tgz env4condor_nosrc.csh run_presel.sh make_preselection.py Triggerweight_2jethack_data.root PileUp_Ratio_ttbar.root TopSFs.root Bstar_Functions_local.py bstarTrees/JHitos16Info_v0p1.p
./development/runManySections.py --createCommandFile --envString "mv tardir/env4condor_nosrc.csh ./; source env4condor_nosrc.csh" --addLog --setTarball=tarball.tgz \presel.listOfJobs commands.cmd
./runManySections.py --submitCondor commands.cmd
condor_q lcorcodi

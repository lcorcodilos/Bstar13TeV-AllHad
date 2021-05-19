import glob,os
base = '-s TEMPSET -y TEMPYEAR -j IJOB -n NJOB \n'
out = open('../args/bstar_trig_args.txt','w')
for year in ['16','17','18']:
    for loc_file in glob.glob('../../bstarTrees/NanoAOD'+year+'_lists/*_loc.txt'):
        setname = loc_file.split('/')[-1].split('_loc')[0]

        if 'data' in setname:
    # if y == '16':
    #     trigs = 'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450'
    #     pretrigs = ['HLT_PFHT475','HLT_Mu50']
    #     subsets = ['B2','C','D','E','F','G','H']
    # else:
    #     trigs = 'HLT_PFHT1050,HLT_PFJet500'
    #     pretrigs = ['HLT_PFHT510','HLT_Mu50']
    #     if y == '17':
    #         subsets = ['B','C','D','E','F']
    #     elif y == '18':
    #         subsets = ['A','B','C','D']

    # for s in subsets:
    #     for p in pretrigs:
            # Get njobs by counting how many GB in each file (1 job if file size < 1 GB)
            bitsize = os.path.getsize('/eos/uscms/store/user/lcorcodi/bstar_nano/rootfiles/'+setname+'_bstar'+year+'.root')
            if bitsize/float(10**9) < 1:  set_njobs = 1
            else: set_njobs = int(round(bitsize/float(10**9)))

            this_string = base.replace('TEMPYEAR',year).replace('TEMPSET',setname).replace('NJOB',str(set_njobs))
            for i in range(1,set_njobs+1):
                out.write(this_string.replace('IJOB',str(i)))

out.close()

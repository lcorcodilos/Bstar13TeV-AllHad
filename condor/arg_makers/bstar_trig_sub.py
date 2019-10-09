import glob
base = '-s TEMPSET -y TEMPYEAR -j TEMPJOB -n 25 \n'
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
            this_string = base.replace('TEMPYEAR',year).replace('TEMPSET',setname)
            #out.write(this_string)
            for j in range(1,26):
                out.write(this_string.replace('TEMPJOB',str(j)))

out.close()

base = '-s dataTEMPSET -y TEMPYEAR -n TEMPJOB -j 25 -t TEMPTRIGS -p TEMPPRETRIG \n'
out = open('../args/bstar_trig_args.txt','w')
for y in ['16','17','18']:
    if y == '16':
        trigs = 'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450'
        pretrigs = ['HLT_PFHT475','HLT_Mu50']
        subsets = ['B2','C','D','E','F','G','H']
    else:
        trigs = 'HLT_PFHT1050,HLT_PFJet500'
        pretrigs = ['HLT_PFHT510','HLT_Mu50']
        if y == '17':
            subsets = ['B','C','D','E','F']
        elif y == '18':
            subsets = ['A','B','C','D']

    for s in subsets:
        for p in pretrigs:
            this_string = base.replace('TEMPYEAR',y).replace('TEMPTRIGS',trigs).replace('TEMPPRETRIG',p).replace('TEMPSET',s)
            #out.write(this_string)
            for j in range(1,26):
                out.write(this_string.replace('TEMPJOB',str(j)))

out.close()

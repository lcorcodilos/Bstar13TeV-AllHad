missing = []
for l in open('eos.txt','r').readlines():
    try: 
        year = l.split('bstarTrees')[1].split('_')[0]
        if 'singletop' in l:    
            setname = l.split('_')[1]+'_'+l.split('_')[2]
        else: setname = l.split('_')[1]
    
        ijob = l.split(setname+'_')[1].split('-')[0]
        njobs = l.split(setname+'_')[1].split('-')[1].split('.root')[0]

        command = '-s %s -j %s -n %s -y %s' %(setname,ijob,njobs,year) 
        if command in open('../condor/args/bstar_nano_args.txt','r').read(): continue
        else: missing.append(l)
    except:
        missing.append(l)

print missing       

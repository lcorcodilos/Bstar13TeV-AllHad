missing = []
eos = open('eos.txt','r').read()
#condor = open('condor.txt','r').read()

for l in open('bstar_nano_prefire_args.txt','r').readlines():
    if 'ttbar-semilep' in l or 'scale' in l: continue

    pieces = l.split('-')
    attributes = {}

    for p in pieces:
        if p == '': continue
        if p[0] == 's': attributes['set'] = p[2:].strip()
        elif p[0] == 'y': attributes['year'] = p[2:].strip()
        elif p[0] == 'j': attributes['job'] = p[2:].strip()
        elif p[0] == 'n': attributes['njobs'] = p[2:].strip()

    filename = 'bstarTrees%s_%s_%s-%s.root'%(attributes['year'],attributes['set'],attributes['job'],attributes['njobs'])

    if filename in eos: continue
    #if l in condor: continue
    else: missing.append(l)

out = open('rerun.txt','w')
for m in missing: out.write(m)

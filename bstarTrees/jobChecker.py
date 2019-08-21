import sys
files = sys.argv[1:]

writeout = False
if '--write' in files:
    writeout = True

jobsToReRun = []
log = []
outfiles = []
for f in files:
    if f == '--write':
        continue
    thisF = open(f,'r')
    stdoutFile = open(f.replace('notneeded/','').replace('.stderr','.stdout'),'r')

    hasError = False 
    for line in thisF:
        if 'error' in line.lower():
            if 'SetBranchStatus' not in line:
                hasError = True
                print f+': '+line
                log.append(f+': '+line)
    
    if hasError:
        for l in stdoutFile:
            if 'bstarTreeMaker.py ' in l:
                outfiles.append(f.replace('notneeded/','').replace('.stderr','.stdout'))
                jobsToReRun.append(l.replace('bstarTreeMaker.py ',''))
                break 

with open('jobsToReRun.txt', 'w') as f:
    for job in jobsToReRun:
        print job
        if writeout:
            f.write("%s" % job)

with open('jobsToReRun.log', 'w') as f:
    for job in log:
        f.write("%s" % job)

for o in outfiles: print o

import sys
args = sys.argv[1]
files = sys.argv[2:]

writeout = False
if '--write' in files:
    writeout = True

arg_file = open(args,'r')
arg_lines = arg_file.readlines()

jobsToReRun = []
log = []
outfiles = []
for f in files:
    if f == '--write':
        continue
    thisF = open(f,'r')
   
    log_string = thisF.read()
    if 'LPC job removed' in log_string:
        log_number = f.split('_')[-1].split('.')[0]
        print 'Job removed for memory: %s\n\t%s'%(arg_lines[int(log_number)],f)
        jobsToReRun.append(arg_lines[int(log_number)])
        continue
    elif 'Normal termination' not in log_string:
        continue

    stdoutFile_name = f.replace('notneeded/','').replace('.log','.stdout')
    stderrFile_name = f.replace('.log','.stderr')
    stdoutFile = open(stdoutFile_name,'r')
    stderrFile = open(stderrFile_name,'r')
    
    hasError = False 
    for line in stderrFile:
        if 'error' in line.lower():
            if 'SetBranchStatus' not in line:
                hasError = True
                print stderrFile_name+': '+line
                log.append(stderrFile_name+': '+line)
    
    if hasError:
        for l in stdoutFile:
            if 'bstarTreeMaker.py ' in l:
                outfiles.append(f.replace('notneeded/','').replace('.log','.stdout'))
                jobsToReRun.append(l.replace('bstarTreeMaker.py ',''))
                break 
   
if writeout: 
    outf = open('jobsToReRun.txt', 'w')
for job in jobsToReRun:
    print job
    if writeout:
        outf.write("%s" % job)

logf = open('jobsToReRun.log', 'w')
for job in log:
    logf.write("%s" % job)

logf.close()

for o in outfiles: print o

import subprocess
import sys
import pprint 
pp = pprint.PrettyPrinter(indent=4)

year = sys.argv[1]

candidate_files = subprocess.check_output('ls -1 TWpreselection'+year+'_*.root',shell=True).split('\n')

to_remove = [i for i,x in enumerate(candidate_files) if x == '']

for r in to_remove:
    candidate_files.pop(r)

done_files = []

# Just move files that don't need to be hadded
for f in candidate_files:
    if 'job' not in f:
        print 'Executing: mv '+f+' rootfiles/'
        subprocess.call(['mv '+f+' rootfiles/'],shell=True)
        done_files.append(f)
        
# Get a dictionary with all processes that need to be hadded
commands = []
for f in candidate_files:
    if (f not in done_files) and ('_job1of' in f):

        #proc = f.split('_')[1]
        #dak8_string = f.split('_')[2]

        #if len(f.split('_')) > 4:   # has mod
        #    mod_string = '_'+f.split('_')[3]+f.split('_')[4]
        #    reg_string = f.split('_')[5].split('.')[0]
        #else:   # doesn't have mod
        #    mod_string = ''
        #    reg_string = f.split('_')[4].split('.')[0]
        
        
        #key_name = reg_string+'_'+proc+'_'+dak8_string+mod_string
        #proc_dict[key_name] = {
        #                        'haddname':f.replace('_'+f.split('_')[2],''),
        #                        'files_to_add':f.replace('_job1of','_job*of')
        #                    }
        jobstringToReplace = ''
        for i in f.split('_'):
            if 'job1of' in i:
                jobstringToReplace = i
        haddname = f.replace('_'+jobstringToReplace,'')
        filesToHadd = f.replace('_job1of','_job*of')
        commands.append('rm rootfiles/'+haddname)
        commands.append('hadd rootfiles/'+haddname+' '+filesToHadd)
        commands.append('rm '+filesToHadd)

for c in commands:
    subprocess.call([c],shell=True)

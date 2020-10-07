import subprocess, sys, glob, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-r', '--regions', metavar='FILE', type='string', action='store',
                default   =   'default,sideband,ttbar',
                dest      =   'regions',
                help      =   'Regions to consider (comma separated list). Default is signal region ("default")')
parser.add_option('-y', '--years', metavar='FILE', type='string', action='store',
                default   =   '16,17,18',
                dest      =   'years',
                help      =   'Years to consider (comma separated list). Default is 16,17,18.')
parser.add_option('-t', '--taggers', metavar='FILE', type='string', action='store',
                default   =   'loose,medium',
                dest      =   'taggers',
                help      =   'Tau32 opperating points to consider (comma separated list). Default is loose,medium')
parser.add_option('-i', '--ignoreset', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'ignoreset',
                help      =   'Setnames from *_loc.txt files to IGNORE (comma separated list). Default is empty.')
parser.add_option('-n', '--name', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'name',
                help      =   'A custom name for this argument list (bstar_presel_<name>_args.txt)')
parser.add_option('-s', '--setnames', type='string', action='store',
                default   =   '',
                dest      =   'setnames')
(options, args) = parser.parse_args()

# Options to customize run
regions = options.regions.split(',')
years = options.years.split(',')
taggers = options.taggers.split(',')
ignore = options.ignoreset.split(',')
name_string = '_'+options.name if options.name != '' else ''

# Initialize output file
outfile = open('../args/bstar_presel'+name_string+'_args.txt','w')

base_string = '-s TEMPSET -r TEMPREG -j IJOB -n NJOB -y TEMPYEAR -t TEMPTAGGER'

for year in years:
    for reg in regions:
        for tagger in taggers:
            job_base_string = base_string.replace("TEMPYEAR",year).replace('TEMPREG',reg).replace('TEMPTAGGER',tagger)

            if options.setnames == '':setnames = glob.glob('../../bstarTrees/NanoAOD'+year+'_lists/*_loc.txt')
            else: setnames = ['../../bstarTrees/NanoAOD'+year+'_lists/%s_loc.txt'%s for s in options.setnames.split(',')]
            #print setnames 
            for loc_file in setnames:
                print loc_file
                
                setname = loc_file.split('/')[-1].split('_loc')[0] 

                if (setname not in ignore) and not ('-q' in base_string and 'data' in setname):
                        if not os.path.exists('/eos/uscms/store/user/lcorcodi/bstar_nano/rootfiles/'+setname+'_bstar'+year+'.root'): 
                            print 'Cant find '+setname+'_bstar'+year+'.root'
                            continue
                        # Get njobs by counting how many GB in each file (1 job if file size < 1 GB)
                        bitsize = os.path.getsize('/eos/uscms/store/user/lcorcodi/bstar_nano/rootfiles/'+setname+'_bstar'+year+'.root')
                        if bitsize/float(10**9) < 1:  set_njobs = 1
                        else: set_njobs = int(round(bitsize/float(10**9)))
                        if reg == 'ttbar' and 'ttbar' in setname and year == '18': 
                            print 'Special jobs for ttbar in ttMR'
                            set_njobs = set_njobs*10
                        
                        njob_string = job_base_string.replace('TEMPSET',setname).replace('NJOB',str(set_njobs))               
                        for i in range(1,set_njobs+1):
                            job_string = njob_string.replace('IJOB',str(i))
                            outfile.write(job_string+'\n')

                            if 'data' not in setname and 'QCD' not in setname and 'scale' not in setname:
                                for j in [' -J', ' -R', ' -a', ' -b']:
                                    for v in [' up',' down']:
                                        jec_job_string = job_string + j + v
                                        outfile.write(jec_job_string+'\n')

outfile.close()

import subprocess

commands = []

base_string = '-s TEMPSET -r TEMPREG -t TEMPTAU32 -n NJOB -j IJOB -y TEMPYEAR'# -j -r -a -b

for year in ['16','17','18']:
    for tau32 in ['medium']:
        for reg in ['default']:
            year_string = base_string.replace("TEMPYEAR",year).replace('TEMPREG',reg).replace('TEMPTAU32',tau32)
            # QCD
            if year == '16':
                qcd_dict = {'QCDHT700':1,'QCDHT1000':1,'QCDHT1500':1,'QCDHT2000':1,'QCDHT700ext':1,'QCDHT1000ext':1,'QCDHT1500ext':1,'QCDHT2000ext':1}
            elif year == '17' or year == '18':
                qcd_dict = {'QCDHT700':1,'QCDHT1000':1,'QCDHT1500':1,'QCDHT2000':1}
            for qcd in qcd_dict.keys():
                qcd_string = year_string.replace('TEMPSET',qcd).replace('NJOB',str(qcd_dict[qcd]))
                for i in range(1,qcd_dict[qcd]+1):
                    qcd_job_string = qcd_string.replace('IJOB',str(i))
                    commands.append(qcd_job_string)

            # TTbar
            ttbar_jobs = 1
            ttbar_string = year_string.replace('TEMPSET','ttbar').replace("NJOB",str(ttbar_jobs))
            for i in range(1,ttbar_jobs+1):
                commands.append(ttbar_string.replace('IJOB',str(i)))


            # TTbar semilep
            if year != '16':
                ttbar_jobs = 1
                ttbar_string = year_string.replace('TEMPSET','ttbar_semilep').replace("NJOB",str(ttbar_jobs))
                for i in range(1,ttbar_jobs+1):
                    commands.append(ttbar_string.replace('IJOB',str(i)))


            # W+jets
            # if year == '16':
            #     wjet_dict = {'WjetsHT600':1}
            # elif year == '17' or year == '18':
            #     wjet_dict = {'WjetsHT400':1,'WjetsHT600':1,'WjetsHT800':1}
            # for wjet in wjet_dict.keys():
            #     wjet_string = year_string.replace('TEMPSET',wjet).replace('NJOB',str(wjet_dict[wjet]))
            #     for i in range(1,wjet_dict[wjet]+1):
            #         wjet_job_string = wjet_string.replace('IJOB',str(i))
            #         commands.append(wjet_job_string)

            # ST
            st_dict = {'singletop_tW':1,'singletop_tWB':1}
            for st in st_dict.keys():
                if year == '17' and (st == 'singletop_s'):
                    continue
                st_string = year_string.replace('TEMPSET',st).replace('NJOB',str(st_dict[st]))
                for i in range(1,st_dict[st]+1):
                    commands.append(st_string.replace('IJOB',str(i)))
                

            # Signal
            if year == '16' or year == '17':
                for hand in ['LH','RH']:
                    for mass in range(1200,3200,200):
                        if year == '17' and hand == 'LH' and mass == 2800: continue
                        sig_name = 'signal'+hand+str(mass)
                        commands.append(year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1'))

            # Data
            # if year == '16':
            #     data_dict = {'dataB':1,'dataB2':100,'dataC':25,'dataD':50,'dataE':50,'dataF':50,'dataG':50,'dataH':50,'dataH2':1}
            # elif year == '17':
            #     data_dict = {'dataA':50,'dataB':50,'dataC':50,'dataD':50,'dataE':50,'dataF':50}

            # for data in data_dict.keys():

            # if year == '16': subsets = ['B2','C','D','E','F','G','H']
            # elif year == '17': subsets = ['B','C','D','E','F']
            # elif year == '18': subsets = ['A','B','C','D']
            # for sub in subsets:
            #    data_string = year_string.replace('TEMPSET','data'+sub).replace('NJOB','5')
            #    for i in range(1,6):
            #        data_job_string = data_string.replace('IJOB',str(i))
            #        commands.append(data_job_string)

outfile = open('../args/bstar_nminusone_args.txt','w')

for s in commands:
    outfile.write(s+'\n')

outfile.close()

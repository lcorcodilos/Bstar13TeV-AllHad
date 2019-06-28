import subprocess

commands = []

base_string = '-s TEMPSET -n IJOB -j NJOB -y TEMPYEAR'#'python CondorHelper.py -r run_bstar.sh -a "-s TEMPSET -j IJOB -n NJOB -y TEMPYEAR"'

for year in ['16','17','18']:
    year_string = base_string.replace("TEMPYEAR",year)

    # QCD
    if year == '16':
        qcd_dict = {'QCDHT700':14,'QCDHT1000':7,'QCDHT1500':4,'QCDHT2000':3,'QCDHT700ext':25,'QCDHT1000ext':12,'QCDHT1500ext':8,'QCDHT2000ext':8}
    elif year == '17':
        qcd_dict = {'QCDHT700':39,'QCDHT1000':15,'QCDHT1500':10,'QCDHT2000':7}
    elif year == '18':
        qcd_dict = {'QCDHT700':48,'QCDHT1000':15,'QCDHT1500':11,'QCDHT2000':11}
    for qcd in qcd_dict.keys():
        qcd_string = year_string.replace('TEMPSET',qcd).replace('NJOB',str(qcd_dict[qcd]))
        for i in range(1,qcd_dict[qcd]+1):
            qcd_job_string = qcd_string.replace('IJOB',str(i))
            commands.append(qcd_job_string)

    # TTbar
    if year == '16':
        ttbar_jobs = 72
    elif year == '17':
        ttbar_jobs = 30
    elif year == '18':
        ttbar_jobs = 133
    ttbar_string = year_string.replace('TEMPSET','ttbar').replace("NJOB",str(ttbar_jobs))
    for i in range(1,ttbar_jobs+1):
        ttbar_job_string = ttbar_string.replace('IJOB',str(i))
        commands.append(ttbar_job_string)

    # TTbar-semilep
    if year != '16':
        if year == '17':
            ttbar_jobs = 35
        elif year == '18':
            ttbar_jobs = 70
        ttbar_string = year_string.replace('TEMPSET','ttbar_semilep').replace("NJOB",str(ttbar_jobs))
        for i in range(1,ttbar_jobs+1):
            ttbar_job_string = ttbar_string.replace('IJOB',str(i))
            commands.append(ttbar_job_string)

    # ST
    if year == '16':
        st_dict = {'singletop_s':4,'singletop_t':44,'singletop_tB':27,'singletop_tW':3,'singletop_tWB':2}
    elif year == '17':
        st_dict = {'singletop_t':6,'singletop_tB':3,'singletop_tW':7,'singletop_tWB':6}
    elif year == '18':
        st_dict = {'singletop_s':11,'singletop_t':87,'singletop_tB':90,'singletop_tW':8,'singletop_tWB':7}
    for st in st_dict.keys():
        st_string = year_string.replace('TEMPSET',st).replace('NJOB',str(st_dict[st]))
        for i in range(1,st_dict[st]+1):
            st_job_string = st_string.replace('IJOB',str(i))
            commands.append(st_job_string)

    # W+jets
    if year == '16':
        wjets_dict = {'WjetsHT600':3}
    elif year == '17':
        wjets_dict = {'WjetsHT400':11,'WjetsHT600':34,'WjetsHT800':8}
    elif year == '18':
        wjets_dict = {'WjetsHT400':12,'WjetsHT600':16,'WjetsHT800':18}
    for wj in wjets_dict.keys():
        wj_string = year_string.replace('TEMPSET',wj).replace('NJOB',str(wjets_dict[wj]))
        for i in range(1,wjets_dict[wj]+1):
            wj_job_string = wj_string.replace('IJOB',str(i))
            commands.append(wj_job_string)

    # Signal
    if year == '16' or year == '17':
        for hand in ['LH','RH']:
            for mass in range(1200,3200,200):
                sig_name = 'signal'+hand+str(mass)
                if year == '17' and sig_name in ['signalLH2200','signalLH2800','signalRH3000']:
                    continue
                signal_string = year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1')
                commands.append(signal_string)

    # Data
    if year == '16':
        data_dict = {'dataB2':88,'dataC':31,'dataD':43,'dataE':50,'dataF':31,'dataG':89,'dataH':77}#,'dataH2':1}
    elif year == '17':
        data_dict = {'dataB':41,'dataC':57,'dataD':26,'dataE':52,'dataF':67}
    elif year == '18':
        data_dict = {'dataA':135,'dataB':93,'dataC':72, 'dataD':204}
    for data in data_dict.keys():
        data_job_string = year_string.replace('TEMPSET',data).replace('NJOB',str(data_dict[data]))
        for i in range(1,data_dict[data]+1):
            data_subjob_string = data_job_string.replace('IJOB',str(i))
            commands.append(data_subjob_string)


outfile = open('../args/bstar_nano_args.txt','w')

for s in commands:
    outfile.write(s+'\n')

outfile.close()

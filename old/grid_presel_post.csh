rm output_JID_*.log

hadd TWpreselection_ttbar_DAK8medium_$1.root TWpreselection_ttbar_job*of*_DAK8medium_$1.root
hadd TWpreselection_QCDHT500_DAK8medium_$1.root TWpreselection_QCDHT500_job*of*_DAK8medium_$1.root
hadd TWpreselection_QCDHT700_DAK8medium_$1.root TWpreselection_QCDHT700_job*of*_DAK8medium_$1.root
hadd TWpreselection_QCDHT1000_DAK8medium_$1.root TWpreselection_QCDHT1000_job*of*_DAK8medium_$1.root
hadd TWpreselection_QCDHT1500_DAK8medium_$1.root TWpreselection_QCDHT1500_job*of*_DAK8medium_$1.root
hadd TWpreselection_QCDHT2000_DAK8medium_$1.root TWpreselection_QCDHT2000_job*of*_DAK8medium_$1.root

rm TWpreselection_ttbar_job*of*_DAK8medium_$1.root
rm TWpreselection_QCDHT500_job*of*_DAK8medium_$1.root
rm TWpreselection_QCDHT700_job*of*_DAK8medium_$1.root
rm TWpreselection_QCDHT1000_job*of*_DAK8medium_$1.root
rm TWpreselection_QCDHT1500_job*of*_DAK8medium_$1.root
rm TWpreselection_QCDHT2000_job*of*_DAK8medium_$1.root

hadd TWpreselection_QCD_DAK8medium_$1.root TWpreselection_QCDHT*_DAK8medium_$1.root

mv TWpreselection_*_DAK8medium_$1.root rootfiles

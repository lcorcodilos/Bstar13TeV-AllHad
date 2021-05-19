##################################################################
# Helper class to deal with DeepAK8 output (in CSV format only!) #
# Author: Lucas Corcodilos                                       #
# Date: 9/26/18                                                  #
##################################################################

import csv
import pandas

class FatJetNNHelper:
    # csvFileName = string - name of csv file to load
    # decorr = bool - sets decorrelated NN on (True) or off (False)
    def __init__(self, csvFileName, decorr):

        # If this isn't a csv, raise an exception
        if '.csv' not in csvFileName:
            raise ValueError('File input to FatJetNNHelper class is not of format .csv')

        # Make a panda DataFrame from the csv
        self.df = pandas.read_csv(csvFileName) # df = dataframe

        # Want the subset of this where only the decorrelated or nominal values are available
        self.df = self.df.where(self.df['nn_version'] == "Decorrelated").dropna()

        # Convert events from floats to ints
        self.df = self.df.astype({'event':int})

        # These are all of the column names we care about
        self.label_Top_bcq = "Top_bcq"
        self.label_Top_bqq = "Top_bqq"
        self.label_Top_bc = "Top_bc"
        self.label_Top_bq = "Top_bq"
        self.label_W_cq = "W_cq"
        self.label_W_qq = "W_qq"
        self.label_Z_bb = "Z_bb"
        self.label_Z_cc = "Z_cc"
        self.label_Z_qq = "Z_qq"
        self.label_H_bb = "H_bb"
        self.label_H_cc = "H_cc"
        self.label_H_qqqq = "H_qqqq"
        self.label_QCD_bb = "QCD_bb"
        self.label_QCD_cc = "QCD_cc"
        self.label_QCD_b = "QCD_b"
        self.label_QCD_c = "QCD_c"
        self.label_QCD_others = "QCD_others"

        self.event = 0

    def set_event(self,eventNumber):
        self.event = eventNumber
        # Make subset DataFrame with only relevent event info
        self.df_event = self.df.where(self.df['event'] == self.event).dropna()
        # Re-index according to jet ordering
        self.df_event = self.df_event.astype({'jet_no':int})  # First convert to ints
        self.df_event = self.df_event.set_index('jet_no')

    ############################
    # Internal helper function #
    ############################

    def divide_filter_zero(self,numerator, denominator, fallback=-10.):
        if (denominator != 0 and numerator >= 0):
            return numerator/denominator
        else:
            return fallback

    ############################
    # Now the getter functions #
    ############################
    def has_second_jet(self):
        if 1 in self.df_event.index:
            return True
        else:
            return False

    def get_df(self):
        return self.df

    def get_pt(self,jetIndex):
        return self.df_event['pt'][jetIndex]
    def get_eta(self,jetIndex):
        return self.df_event['eta'][jetIndex]
    def get_phi(self,jetIndex):
        return self.df_event['phi'][jetIndex]

    def get_raw_score_qcd(self,jetIndex):
        scores_to_sum = [ 
            self.df_event[self.label_QCD_b][jetIndex],
            self.df_event[self.label_QCD_bb][jetIndex],
            self.df_event[self.label_QCD_c][jetIndex],
            self.df_event[self.label_QCD_cc][jetIndex],
            self.df_event[self.label_QCD_others][jetIndex]
            ]
        return sum(scores_to_sum)

    def get_raw_score_top(self,jetIndex):
        scores_to_sum = [ 
            self.df_event[self.label_Top_bcq][jetIndex],
            self.df_event[self.label_Top_bqq][jetIndex]
            ]
        return sum(scores_to_sum)

    def get_raw_score_w(self,jetIndex):
        scores_to_sum = [ 
            self.df_event[self.label_W_cq][jetIndex],
            self.df_event[self.label_W_qq][jetIndex]
            ]
        return sum(scores_to_sum)

    def get_raw_score_z(self,jetIndex):
        scores_to_sum = [ 
            self.df_event[self.label_Z_bb][jetIndex],
            self.df_event[self.label_Z_cc][jetIndex],
            self.df_event[self.label_Z_qq][jetIndex]
            ]
        return sum(scores_to_sum)

    def get_raw_score_zbb(self,jetIndex):
        return self.df_event[self.label_Z_bb][jetIndex]

    def get_raw_score_zcc(self,jetIndex):
        return self.df_event[self.label_Z_cc][jetIndex]

    def get_raw_score_hbb(self,jetIndex):
        return self.df_event[self.label_H_bb][jetIndex]

    def get_raw_score_hcc(self,jetIndex):
        return self.df_event[self.label_H_cc][jetIndex]

    def get_raw_score_h4q(self,jetIndex):
        return self.df_event[self.label_H_qqqq][jetIndex]


    def get_binarized_score_top(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_top(jetIndex), 
            self.get_raw_score_top(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_w(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_w(jetIndex),
            self.get_raw_score_w(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_z(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_z(jetIndex), 
            self.get_raw_score_z(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_zbb(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_zbb(jetIndex), 
            self.get_raw_score_zbb(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_zcc(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_zcc(jetIndex), 
            self.get_raw_score_zcc(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_hbb(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_hbb(jetIndex), 
            self.get_raw_score_hbb(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_hcc(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_hcc(jetIndex), 
            self.get_raw_score_hcc(jetIndex)+self.get_raw_score_qcd(jetIndex))

    def get_binarized_score_h4q(self,jetIndex):
        return self.divide_filter_zero(
            self.get_raw_score_h4q(jetIndex), 
            self.get_raw_score_h4q(jetIndex)+self.get_raw_score_qcd(jetIndex))


    def get_flavor_score_bb(self,jetIndex):
        return self.divide_filter_zero(
                self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex]+self.df_event[self.label_QCD_bb][jetIndex],
                self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex]++self.df_event[self.label_H_cc][jetIndex]++self.df_event[self.label_Z_cc][jetIndex] + self.get_raw_score_qcd(jetIndex)
            )

    def get_flavor_score_cc(self,jetIndex):
        return self.divide_filter_zero(
                self.df_event[self.label_H_cc][jetIndex]+self.df_event[self.label_Z_cc][jetIndex]+self.df_event[self.label_QCD_cc][jetIndex],
                self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex]+self.df_event[self.label_H_cc][jetIndex]+self.df_event[self.label_Z_cc][jetIndex] + self.get_raw_score_qcd(jetIndex)
            )

    def get_flavor_score_bb_no_gluon(self,jetIndex):
        return self.divide_filter_zero(
            self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex],
            self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex]+self.df_event[self.label_H_cc][jetIndex]+self.df_event[self.label_Z_cc][jetIndex] + self.get_raw_score_qcd(jetIndex)
        )

    def get_flavor_score_cc_no_gluon(self,jetIndex):
        return self.divide_filter_zero(
            self.df_event[self.label_H_cc][jetIndex]+self.df_event[self.label_Z_cc][jetIndex],
            self.df_event[self.label_H_bb][jetIndex]+self.df_event[self.label_Z_bb][jetIndex]+self.df_event[self.label_H_cc][jetIndex]+self.df_event[self.label_Z_cc][jetIndex] + self.get_raw_score_qcd(jetIndex)
        )



    
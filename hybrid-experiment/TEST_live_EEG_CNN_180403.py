# Jonas Braun jonas.braun@tum.de
# 03.04.2018
# this script is used to test the functions in live_EEG_CNN_180403 without having to call them from record_data or run_session


import sys, os, os.path
sys.path.append('C:\\Users\\mirja\\Anaconda3\\Lib\\site-packages\\gumpy-master\\gumpy')

import numpy as np
import gumpy


from live_EEG_CNN_180403 import liveEEG_CNN
from gumpy.data.nst_eeg_live import NST_EEG_LIVE



if __name__ == '__main__':

    base_dir = 'C:\\PYTHON_DATA\\02_realtime\\00_DATA\\10_EEG_Jonas_Braun'
    file_name = 'Run1.mat'
    file_name2 = 'EEG_session_10_47_19_04_2018_run3.mat'#'EEG_session_10_31_19_04_2018_run2.mat'#'EEG_session_10_10_19_04_2018_run1.mat'#'Run3.mat'

    myclass = liveEEG_CNN(base_dir,file_name)
    myclass.fit(load = True)
    myclass2 = liveEEG_CNN(base_dir, file_name2)
    
    true = 0
    false = 0

    for i in range(0,myclass2.data_notlive.trials.shape[0]):
        fs = myclass2.data_notlive.sampling_freq
        label = myclass2.data_notlive.labels[i]+1
        ### no need to subtract trial_offset*fs here, because it is already done when loading in the constructor of liveEEG_CNN
        trial = myclass2.data_notlive.trials[i]
        if i < (myclass2.data_notlive.trials.shape[0] - 1):
            next_trial = myclass2.data_notlive.trials[i+1]
            X = myclass2.data_notlive.raw_data[trial:next_trial]
        else:
            X = myclass2.data_notlive.raw_data[trial:]

        trial = 0
        nst_eeg_live = NST_EEG_LIVE(base_dir, file_name2)
        nst_eeg_live.load_from_mat(label,trial,X,fs)

        current_classifier, pred_true, pred_valid = myclass.classify_live(nst_eeg_live)
        
        if pred_valid:
            
            print('Classification result: ',current_classifier,'\n')
            if pred_true:
                print('This is true!\n')
                true += 1 
            else:
                print('This is false!\n')
                false += 1

    print('Count of true predictions:', true)
    print('Percentage of true predictions:', 100*true/(true+false))
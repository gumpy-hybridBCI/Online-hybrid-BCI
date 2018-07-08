# Jonas Braun, jonas.braun@tum.de
# MSNE Research Internship Hybrid BCI
# 01.03.2018
# this script is used to test the functions in live_EMG_180301.py and nst_emg_live_180301 without having to call them from record_data or run_session


#import matplotlib.pyplot as plt 

import sys, os, os.path

#sys.path.append('C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\gumpy-master')
#sys.path.append('C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\gumpy-0.5.0-py3.6.egg')
#sys.path.append('C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\mlxtend-0.10.0')
#sys.path.append('C:\\PYTHON_DATA\\01_EMG_classify')

import numpy as np
import gumpy

from live_EMG_180301 import liveEMG
from nst_emg_live_180301 import NST_EMG_LIVE
from robothand_arduino_180321 import RobotHand

#from emg_script_class_180302 import EMG_SCRIPT


#
def run_once(f):
        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                wrapper.has_run = True
                return f(*args, **kwargs)
        wrapper.has_run = False
        return wrapper

if __name__ == '__main__':

    #emg_script = EMG_SCRIPT()
    if 0:
        base_dir = 'C:\\PYTHON_DATA\\02_realtime\\00_DATA\\00_BIG_DATA_Jonas_Braun'#01_EMG_data\\S1'#'C:\\Users\\nst\\Desktop\\Jonas_HybridBCI\\02_realtime'   
        file_name = 'session_live_09_11_23_03_2018.mat' #session_live_16_03_20_03_2018.mat
        #very long session:'session_live_15_28_13_03_2018.mat' 
        file_name_live = 'session_09_11_23_03_2018.mat'
        #very long session: 'session_15_28_13_03_2018.mat'
    
    if 0:
        # Jonas with force
        base_dir = 'C:\\PYTHON_DATA\\02_realtime\\00_DATA\\00_BIG_DATA_Jonas_Braun'
        file_name = 'session_live_09_47_23_03_2018.mat' 
        file_name_live = 'session_09_47_23_03_2018.mat'
    if 0:
        #Mirjam trial one
        base_dir = 'C:\\PYTHON_DATA\\02_realtime\\00_DATA\\01_Mirjam_Hemberger'
        file_name = 'session_live_10_34_23_03_2018.mat'
        file_name_live = 'session_10_34_23_03_2018.mat'
    if 1:
        #Mirjam trial with force
        base_dir = 'C:\\PYTHON_DATA\\02_realtime\\00_DATA\\01_Mirjam_Hemberger'
        file_name = 'session_live_12_10_23_03_2018.mat'
        file_name_live = 'session_12_10_23_03_2018.mat'
        
    pos_choices = ["fist", "pinch_2", "pinch_3"]
    splits = [3,5,8,10,12]#,8,10,12]#[5,10,15,20]#,10,24
    result_live = np.zeros(len(splits))
    result_SFFS = result_live
    result_notlive = result_live
    for j in range(len(splits)):#,split in splits:
        split = splits[j]
        #sprint('Split:',split)
        myclass = liveEMG(base_dir,file_name)
        #for k in range(int(len(myclass.y_class_force)/2),len(myclass.y_class_force)):
        #myclass.y_class_force[int(len(myclass.y_class_force)/2):int(len(myclass.y_class_force))] += 10
        #old_stdout = sys.stdout
        #log_file = open("log_algeval2.log","w")
        #sys.stdout = log_file
        
        #for classifier in gumpy.classification.available_classifiers:
        #    if classifier == 'SVM' or classifier == 'KNN' or classifier == 'LDA' \
        #    or classifier == 'MLP' or classifier == 'LogisticRegression' \
        #    or classifier == 'RandomForest'  or classifier == 'ShrinkingLDA':
        #        continue
        #    print('**********',classifier,'**********')
        #    myclass.fit(classifier)
    
        myclass.fit('NaiveBayes', split=split)#QuadraticLDA
        result_SFFS[j] = myclass.sffs_score
        result_notlive[j] = myclass.acc_notlive
        #sys.stdout = old_stdout
        #log_file.close()
        
        """
        for i in range(0,myclass.data_notlive.trials.shape[0]):
            fs = myclass.data_notlive.sampling_freq
            label = myclass.data_notlive.labels[i]
            trial = myclass.data_notlive.trials[i]
            if i < (myclass.data_notlive.trials.shape[0] - 1):
                next_trial = myclass.data_notlive.trials[i+1]
                X = myclass.data_notlive.raw_data[trial:next_trial]
                force = myclass.data_notlive.forces[trial:next_trial]
            else:
                X = myclass.data_notlive.raw_data[trial:]
                force = myclass.data_notlive.forces[trial:]
    
            trial = 0
            nst_emg_live = NST_EMG_LIVE('','','')
            nst_emg_live.load_from_mat(label,trial, X, force, fs)
    
            current_classifier, pred_true = myclass.classify_live(nst_emg_live)
            print('---------- Classification result: posture ',current_classifier[0],'----------\n')
            if pred_true:
                print('---------- This is true! ----------\n')
            else:
                print('---------- This is false! ----------\n')
                """
                
        myclass_live = liveEMG(base_dir,file_name_live)
        #robothand = RobotHand()
        
        right = 0
        wrong = 0
        for i in range(72,myclass_live.data_notlive.trials.shape[0]):
            fs = myclass_live.data_notlive.sampling_freq
            label = myclass_live.data_notlive.labels[i]
            trial = myclass_live.data_notlive.trials[i]
            if i < (myclass_live.data_notlive.trials.shape[0] - 1):
                next_trial = myclass_live.data_notlive.trials[i+1]
                X = myclass_live.data_notlive.raw_data[trial:next_trial]
                force = myclass_live.data_notlive.forces[trial:next_trial]
            else:
                X = myclass_live.data_notlive.raw_data[trial:]
                force = myclass_live.data_notlive.forces[trial:]
    
            trial = 0
            nst_emg_live = NST_EMG_LIVE('','','')
            nst_emg_live.load_from_mat(label,trial, X, force, fs)
            print(label)
            current_classifier, pred_true, pred_valid = myclass.classify_live(nst_emg_live)
            print('---------- Classification result: posture ',current_classifier, 
                      pos_choices[int(np.remainder(current_classifier,10))], '----------')
            if pred_true:
                print('---------- This is true! ----------\n')
                right +=1
            else:
                print('---------- This is false! ----------\n')
                wrong +=1
            #robothand.do_posture(current_classifier,5)
        
        print('Correct:',right,'/',right+wrong)
        result_live[j] = right / (right+wrong)
        
    print('splits',splits,'SFFS score',result_SFFS,'notlive score',result_notlive, 'live score',result_live)

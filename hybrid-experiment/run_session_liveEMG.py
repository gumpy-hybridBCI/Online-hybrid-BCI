# Jonas Braun, jonas.braun@tum.de
# MSNE Research Internship Hybrid BCI
# 01.03.2018
# modification of run_session_2.py to allow live processing and classification of EMG
# state 1: collect data (certain amount of trials, defined by trials_notlive (-l)), when finished with all trials, go to 2
# state 2: analyse and classify collected data and build model, afterwards go to 3
# state 3: collect live data of one trial and then go to 4
# state 4: uses model and live data to classify every trial live, go back to 3




from math import pi, sin, cos
import os
import random
import sys
import argparse
#import time
import numpy as np

sys.path.append('C:\\Panda3D-1.9.4-x64\\direct')
from direct.showbase.ShowBase import ShowBase
#from direct.task import Task
from direct.actor.Actor import Actor

from record_data_liveEMG_180301 import RecordData_liveEMG
from live_EMG_180301 import liveEMG
from robothand_arduino_180321 import RobotHand

#from nst_emg_live_180301 import NST_EMG_LIVE

class MyApp_liveEMG(ShowBase):
    def __init__(self, force_classify, trial_count,trials_notlive, Fs, age, gender="male"):
        ### call init of base class ShowBase
        ShowBase.__init__(self)

        self.pos_choices = ["fist", "pinch_2", "pinch_3"]
        
        ### check inputs, whether the size is acceptable
        self.num_pos = len(self.pos_choices)
        if trials_notlive > trial_count:
                raise ValueError("'trials_notlive' cannot be larger than 'trials'")
        self.force_classify = force_classify
        
        if self.force_classify == True:
            # case when force shall be classified as well
            if trial_count % (2*self.num_pos):
                raise ValueError("'trials' must be devisable by ", 2*self.num_pos)

            if trials_notlive % (2*self.num_pos):
                raise ValueError("'trials_notlive' must be devisable by ", 2*self.num_pos)

            self.trial_count_for_each_cue_pos = trial_count // self.num_pos // 2
            self.trial_count_for_each_cue_pos_notlive = trials_notlive // self.num_pos // 2
            print("\nFirst, please apply strong force for ", trials_notlive // 2, " trials.\n", \
                  "Afterwards, please apply weak force for ", trials_notlive // 2, "trials.\n" )
        else:
            # noone cares about force, only posture
            if trial_count % self.num_pos:
                raise ValueError("'trials' must be devisable by ", self.num_pos)

            if trials_notlive % self.num_pos:
                raise ValueError("'trials_notlive' must be devisable by ", self.num_pos)

            self.trial_count_for_each_cue_pos = trial_count // self.num_pos
            self.trial_count_for_each_cue_pos_notlive = trials_notlive // self.num_pos

        ### Generate position lists for both live and notlive trials
            
        self.cue_pos_choices_notlive = [x for pair in zip(self.pos_choices*self.trial_count_for_each_cue_pos_notlive) for x in pair]
        self.cue_pos_choices_live = [x for pair in zip(self.pos_choices*(self.trial_count_for_each_cue_pos - 
                                            self.trial_count_for_each_cue_pos_notlive)) for x in pair]

        # Randomizing the positions
        random.shuffle(self.cue_pos_choices_notlive)
        random.shuffle(self.cue_pos_choices_live)
        
        if self.force_classify==True:
            # repeat the exact same testing procedure -->once strong and once weak
            self.cue_pos_choices_notlive = self.cue_pos_choices_notlive + self.cue_pos_choices_notlive #.append(self.cue_pos_choices_notlive)
            self.cue_pos_choices_live = self.cue_pos_choices_live + self.cue_pos_choices_live #.append(self.cue_pos_choices_live)
            self.trial_count_for_each_cue_pos = self.trial_count_for_each_cue_pos*2
            self.trial_count_for_each_cue_pos_notlive = self.trial_count_for_each_cue_pos_notlive*2
            
        print("\nNot live trials:")
        print(self.cue_pos_choices_notlive)
        print("\nLive trials:")
        print(self.cue_pos_choices_live, '\n')
        
        ### Initialise states
        if self.trial_count_for_each_cue_pos >0:
            self.state = 1
        else:
            self.state = 0

        #Add of a position to avoid data loss, because pop(0) is used
        self.cue_pos_choices_notlive.append('end')
        self.cue_pos_choices_live.append('end')

        ### initialise the RecordData thread and the RobotHand
        self.record_data = RecordData_liveEMG(Fs, age, gender, with_feedback=False)
        self.record_data.start_recording()
        try:
            self.robothand = RobotHand(port="COM6") #"COM4" on Windows measurement PC
            self.robotconnected = 1
        except:
            print('Robot not connected. Output only to console')
            self.robotconnected = 0
            
        ### initialise tasks, including Panda and the run_trial task

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # Add the run_trial procedure to the task manager
        self.taskMgr.add(self.run_trial, "run_trial_task")

        # Load and transform the panda actor.
        self.pandaActor = Actor("models/Hand")

        scale = 10
        self.pandaActor.setScale(scale, scale, scale)
        self.pandaActor.reparentTo(self.render)

        self.pandaActor.setPos(7.9, 1.5, -14.5)

        self.filename_notlive = ""
        self.cwd = os.getcwd()
        self.datapath = self.cwd
        self.current_classifier = []
        self.true = 0
        self.false = 0
        
        
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = 205#20 * task.time * 6.0
        theta = 20
        angleRadians = angleDegrees * (pi / 180.0)
        thetaRad = theta * (pi / 180.0)
        self.camera.setPos(3.5*sin(angleRadians), -3.5*cos(angleRadians), -3.5*sin(thetaRad))
        self.camera.setHpr(angleDegrees, theta, 0)

        return task.cont
    
    # this decorator is defined to protect the classification function to run only once
    # otherwise the sequential feature selector causes problems, because it uses
    # the parallel processing toolbox
    def run_once(f):
        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                wrapper.has_run = True
                return f(*args, **kwargs)
        wrapper.has_run = False
        return wrapper

    @run_once
    def classify_notlive(self):
    ### does the classification (called in state 2)
        if __name__ == '__main__':
            print('\nClassification is starting. This might take a while.\n')
            self.cue_pos_choices_notlive = ['end']
            ### pause recording while classification such that data file does get to large
            ### alternatively, recording can be continued, but in that case restart_recording() is not required       
            self.filename_notlive, self.datapath = self.record_data.pause_recording_and_dump()
            #self.filename_notlive = self.record_data.continue_recording_and_dump()
            print(self.datapath, '  ', self.filename_notlive, '\n')
            ### initialise liveEMG class with the not live data and perform the fit of the model
            self.liveEMG = liveEMG(self.datapath,self.filename_notlive)
            self.liveEMG.fit()
            print('Classification completed. Back in run_session.\n')
            ### resume recording
            self.record_data.restart_recording()
            
    def classify_life(self):
    ### called in state 4
        ### get_last_trial returns an instance of the Dataset class NST_EMG_LIVE, which is directly handed over to the liveEMG object
        self.current_classifier, pred_true, pred_valid = self.liveEMG.classify_live(self.record_data.get_last_trial())
        if pred_valid != False:
            # display result of classification
            print('---------- Classification result: posture ',self.current_classifier, 
            self.pos_choices[int(np.remainder(self.current_classifier,10))], '----------')
            if pred_true: 
                print('---------- This is true! ----------\n')
                self.true +=1
            else:
                print('---------- This is false! ----------\n')
                self.false +=1
            ### move the robothand if it is connected
            if self.robotconnected:
                self.robothand.do_posture(self.current_classifier,5)
 
        else:
            print('This trial is skipped because recording was too short.\n') 
            
    def run_notlive(self):
        ### state 1: record data nonlive
        ### state 1.5 is for applying low force 
        pos = self.cue_pos_choices_notlive.pop(0)
            
        if self.force_classify == True and  len(self.cue_pos_choices_notlive) == (self.trial_count_for_each_cue_pos_notlive*self.num_pos // 2):
            ### transintion from 1 to 1.5 after half of the notlive trials
            print("From now on, please apply low force!")
            self.state = 1.5
        ### do the hand movement
        self.pandaActor.play(pos)
        ### add_trial adds the timestamp and label to the recorded data for later identification of individual trials
        if self.state == 1:
            self.record_data.add_trial(self.pos_choices.index(pos))
        elif self.state == 1.5:
            ### for low force, 10 is added to all labels 
            self.record_data.add_trial(self.pos_choices.index(pos)+10)

        print('Now:',pos,'\t--- Next:',self.cue_pos_choices_notlive[0],'\t---',len(self.cue_pos_choices_notlive)-1,'left.')
    
    
    def run_live(self):
        # state 3: record data live
        # state 3.5 is for applying low force        
        pos = self.cue_pos_choices_live.pop(0)
        
        if self.force_classify == True and  len(self.cue_pos_choices_live) == \
            ((self.trial_count_for_each_cue_pos-self.trial_count_for_each_cue_pos_notlive)*self.num_pos // 2):
            ### transintion from 3 to 3.5 after half of the live trials
            print("From now on, please apply low force!")
            self.state = 3.5
        
        ### do the hand movement
        self.pandaActor.play(pos)
        ### add_trial adds the timestamp and label to the recorded data for later identification of individual trials
        if self.state == 3:
            self.record_data.add_trial(self.pos_choices.index(pos))
        elif self.state == 3.5:
            ### for low force, 10 is added to all labels 
            self.record_data.add_trial(self.pos_choices.index(pos)+10)

        print('Now:',pos,'\t--- Next:',self.cue_pos_choices_live[0],'\t---',len(self.cue_pos_choices_live)-1,'left.')
            
                    
        
    def run_trial(self, task): 
        ### this is the state-machine calling the different functions for each state
        if task.time < 10.0: #both playing the gesture in panda and performing the gesture with the robot arm take 10s
            return task.cont
        
        if self.state == 1 or self.state == 1.5: 
            ### state 1 and 1.5: do notlive recording (1 for high force, 1.5 for low force)
            self.run_notlive()
            ### change state from 1 to 2 (classify) or to 0 (end)
            if len(self.cue_pos_choices_notlive) == 1 and len(self.cue_pos_choices_live) >1:
                self.state = 2
            elif len(self.cue_pos_choices_live) <=1:
                self.state = 0                
            return task.again
            
        elif self.state == 2:   
            ### state 2: do classification of notlive data and change to state 3
            self.classify_notlive()
            self.state = 3
            return task.again
          
        elif self.state == 3 or self.state == 3.5:              
            ### state 3: do live recording 
            ###  start next trial (only if there is one trial left. otherwise change state to 0 (end))
            if  len(self.cue_pos_choices_live) <=1:
                self.state = 0
            else:
                self.run_live()
                ### change to 4 or 4.5, important to keep information of high or low
                self.state += 1
            return task.again
        
        elif self.state == 4 or self.state == 4.5:
            ### state 4 do live classification and robot arm movement ->afterwards go back to state 3/3.5
            self.classify_life()
            ### change to 3 or 3.5, important to keep information of high or low
            self.state -=1
            return task.again
    
        else:
            ### other, e.g. 0:   stop system
            if (self.true+self.false) != 0:
                print('Correct:',self.true,'/',self.true+self.false)
            self.record_data.stop_recording_and_dump()
            ShowBase.destroy(self)#base.destroy()
            if self.robotconnected:
                self.robothand.shutdown()
            sys.exit()
            return task.done


    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="emg experiment with panda visualisation")
    parser.add_argument("-t", "--trials"       , help="number of trials"        , default=72   , type=int)
    parser.add_argument("-f", "--Fs"           , help="sampling frequency"      , required=True, type=int)
    parser.add_argument("-a", "--age"          , help="age of the subject"      , required=True, type=int)
    parser.add_argument("-g", "--gender"       , help="gender of the subject"   , required=True)
    parser.add_argument("-w", "--with_feedback", help="with additional feedback", type=bool)
    parser.add_argument("-l", "--trials_notlive",help="number of trials before live", default=66,type=int)
    parser.add_argument("-p", "--force_classify",help="enable force classification", default=0, type=int)


    args = vars(parser.parse_args())

    app = MyApp_liveEMG(args["force_classify"], args['trials'], args["trials_notlive"], args["Fs"], args["age"],
            gender=args["gender"])
    app.run() 

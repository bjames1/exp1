
"""
                      File    :   "sizeGloss.py"
                      Author  :   James Michael Brown
                      Updated :   January 26, 2020
"""

from psychopy import visual, event, core, gui, logging
import os, sys, shutil
import pandas as pd

logFileDir = './data/'

# demographics
cols = [
    'First Name',
    'Last Name',
    'Middle Initial',
    'age',
    'gender'
];

# setup data entry fields
info = {
    cols[0]:'',
    cols[1]:'',
    cols[2]:'',
    cols[3]:'',
    cols[4]:['male', 'female'],
};

# create Dlg from Dict
fileDlg = gui.DlgFromDict(
    dictionary=info,
    title='Size-Gloss Study',
    order=[
    cols[0],
    cols[1],
    cols[2],
    cols[3],
    cols[4]
]);

#---Build Logging File
if gui.OK:
    Dlg_Responses=fileDlg.data;

    studyIDPrefix = 'sizeGloss_exp1_';
    subjectIDPrefix = '999';
    logFilePrefix = '_DATA_subjectInfo.csv';

    logFileName = logFileDir + studyIDPrefix + subjectIDPrefix + logFilePrefix;

    for i in range(len(Dlg_Responses)):
        resp = Dlg_Responses[i];
        if resp == '':
            print('...Missing Participant Data')
            print('...Session Cancelled')
            core.quit()

    df = pd.DataFrame([info], columns = cols)
    df.to_csv(logFileName, index = False, header=True)
    print('...All Participant Data Logged!')
    print('...Beginning Session')

core.quit();

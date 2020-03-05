################################################################################
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
"""
                      File    :   "exp1.py"
                      Author  :   James Michael Brown
                      Updated :   March 2, 2020
"""
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
# Load Modules
from psychopy import visual, event, core, gui, logging, monitors
from psychopy.hardware import keyboard
from pathlib import Path
from PIL import Image
import os, sys, shutil, cv2, pickle, math, zipfile, random, glob
import pandas as pd
import numpy as np
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
# Task Parameters
N_TRIALS = 5;
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
def getTaskObjects(*args):
    from PIL import Image
    import glob
    try:
        arr = args[0];
        for arr in args:
            globTaskList = [];
            path = './stimuli/' + arr;
            for filename in glob.glob(path + '/*.png'):
                globTaskList.append(filename)

        globTaskList.sort()
        return globTaskList
    except:
        taskObjectList = ['size', 'layer', 'gloss', 'grid','background']
        print('TASK OBJECTS:')
        for i in taskObjectList:
            print(i)
#------------------------------------------------------------------------------#
#---------------------------------------------------------------------------
def whiteSpace():
    for i in range(5):
        print('')
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
def setupTask():
    VM_SHOW_LIMIT_BOX = False;
    VM_CLICK_ON_UP = False;
    VM_WIDTH = 1920;
    VM_HEIGHT = 1080;
    win = visual.Window(
                size=(1920, 1080),
                color='grey',
                fullscr=True,
                units='pix',
                mon='testMonitor');
    vm = visual.CustomMouse(
            win,
            leftLimit=-(VM_WIDTH/2.0),
            topLimit=(VM_HEIGHT/2.0),
            rightLimit=(VM_WIDTH/2.0),
            bottomLimit=-(VM_HEIGHT/2.0),
            showLimitBox=VM_SHOW_LIMIT_BOX,
            clickOnUp=VM_CLICK_ON_UP);
    vm.setVisible=False;
    mouse = event.Mouse();
    return win, mouse, vm
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

#########################
## TASK: subjectInfo   ##
#########################

# demographics
cols = [
    'ID',
    'First Name',
    'Last Name',
    'Middle Initial',
    'Age',
    'Gender'
];

# setup data entry fields
info = {
    cols[0]:'',
    cols[1]:'',
    cols[2]:'',
    cols[3]:'',
    cols[4]:'',
    cols[5]:['male', 'female', 'transgender', 'non-binary', 'prefer not to say'],
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
    cols[4],
    cols[5],
]);

#---Build Logging File
if gui.OK:
    Dlg_Responses=fileDlg.data;

    for i in range(len(Dlg_Responses)):
        resp = Dlg_Responses[i];
        if resp == '':
            print('...Missing Participant Data')
            print('...Session Cancelled')
            core.quit()
        else:

            ID_resp = int(Dlg_Responses[0]);

            studyIDPrefix = 'sizeGloss_exp1_';
            df_sampleFrame = pd.read_excel('sizeGloss_exp1_SampleFrame.xlsx', index_col=0);

            subject_numbers = df_sampleFrame['subject #'];
            subject_IDs = df_sampleFrame['ID'];

            ID_index = list(subject_numbers).index(ID_resp);
            subjectID = str(list(subject_IDs)[ID_index]);

            subjectTask = list(df_sampleFrame['task'])[list(subject_numbers).index(ID_resp)];

            taskList = ['subjectInfo', 'objectNaming', subjectTask];
            logFileDir = './data/{}/'.format(subjectID);

            dirExists = os.path.isdir(logFileDir)

            if dirExists == True:
                whiteSpace()
                print('...directory already exists!')
                print('...quitting experiment!')
                whiteSpace()
                core.quit()
            else:
                pass

    if dirExists == False:
        print('...directory does not already exist.')
        print('...creating directory.')
        os.makedirs(logFileDir)

    logFilePrefix = '_DATA_subjectInfo.csv';
    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

    df = pd.DataFrame([info], columns = cols);
    df.to_csv(logFileName, index = False, header=True);

    studyIDPrefix = 'sizeGloss_exp1_';
    logFileDir = './data/{}/'.format(subjectID)

    taskInfo = {};
    for task in taskList:
        taskInfo.update({task:{'taskCompleted':False}});


    taskInfo['subjectInfo']['taskCompleted']=True;
    logFilePrefix = '_DATA_taskInfo.csv';
    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

    df_taskInfo = pd.DataFrame(taskInfo).T
    df.to_csv(logFileName, index = True, header=True)

    print('...All Participant Data Logged!')
    print('...Beginning Session')
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
win, mouse, vm = setupTask();
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
for task in taskList:
    try:

        #########################
        ## TASK: objectNaming  ##
        #########################
        if task == 'objectNaming':
            txt = '';
            i = 0;
            next_inc = 0;
            continuing = True;
            counter_var = 0;
            refresh = False;
            TASK_DONE = False;
            userLabel = 'object name';
            sizeKey = getTaskObjects('size')
            dataDict = {};
            for index in range(len(sizeKey)):
                image = sizeKey[index];
                element = {index: {
                            'image': image,
                            'userLabel':None}
                            };
                dataDict.update(element);
            random.shuffle(sizeKey);
            objectName = visual.TextStim( win,
                                    userLabel,
                                    height = 30,
                                    alignVert='center',
                                    alignHoriz='center',
                                    units='pix');
            objectName.pos = (0, 0);
            msg = visual.TextStim(win, 'input text', height = 30);
            msg.pos = (0, -325);
            msg2 = visual.TextStim( win,
                                    'Name this object',
                                    height = 30);
            msg2.pos = (0, 375);
            endBlock = visual.Rect(win=win,
                width=2000,
                height=2000,
                lineColor='grey',
                lineWidth=3.0,
                fillColor='grey',
                units='pix');
            endBlock.setOpacity(0);
            #
            endText = visual.TextStim(win,
                                    text='',
                                    height = 30,
                                    alignVert='center',
                                    alignHoriz='center',
                                    units='pix');
            endText.pos = (0, 0);
            endText.setOpacity(0);
            def refresh_trial(msg, refresh):
                del msg
                msg = visual.TextStim(win, 'input text', height = 30, wrapWidth=20)
                msg.pos = (0, -300); msg.setAutoDraw(True);
                refresh = False;
                return msg, refresh

            def sizeImage(win, key):
                im = visual.ImageStim(
                            win,
                            image=key,
                            pos=(0, 0),
                            size=(440, 440),
                            units='pix');
                return im

            def saveData(dataDict):
                logFilePrefix = '_DATA_objectNaming.csv';
                logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                df = pd.DataFrame.from_dict(dataDict)
                df.to_csv(logFileName, index = True, header=True)

            def findImageIndex(imageName):
                try:
                    for index in range(len(dataDict)):
                        image = dataDict[index]['image']
                        if imageName == image:
                            return(index)
                except:
                    index = 'NULL'
                    return
            def edit(word, theString):
                 word = word.replace(theString, '')
                 return ''.join(word.split())
            def task_keys(txt, pygKey):

                txt += ('{}'.format(pygKey));

                if pygKey == '0':
                    txt=edit(txt, '0');

                if pygKey == '1':
                    txt=edit(txt, '1');

                if pygKey == '2':
                    txt=edit(txt, '2');

                if pygKey == '3':
                    txt=edit(txt, '3');

                if pygKey == '4':
                    txt=edit(txt, '4');

                if pygKey == '5':
                    txt=edit(txt, '5');

                if pygKey == '6':
                    txt=edit(txt, '6');

                if pygKey == '7':
                    txt=edit(txt, '7');

                if pygKey == '8':
                    txt=edit(txt, '8');

                if pygKey == '9':
                    txt=edit(txt, '9');

                if pygKey == '=':
                    txt=edit(txt, '=');

                if pygKey == 'delete':
                    txt=edit(txt, 'delete');

                if pygKey == ';':
                    txt=edit(txt, ';');

                if pygKey == ',':
                    txt=edit(txt, ',');

                if pygKey == '.':
                    txt=edit(txt, '.');

                if pygKey == 'control':
                    txt=edit(txt, 'control');

                if pygKey == '/':
                    txt=edit(txt, '/');

                if pygKey == '|':
                    txt=edit(txt, '|');

                if pygKey == '{':
                    txt=edit(txt, '{');

                if pygKey == '}':
                    txt=edit(txt, '}');

                if pygKey == '[':
                    txt=edit(txt, '[');

                if pygKey == ']':
                    txt=edit(txt, ']');

                if pygKey == '?':
                    txt=edit(txt, '?');

                if pygKey == '-':
                    txt=edit(txt, '-');

                if pygKey == '_':
                    txt=edit(txt, '_');

                if pygKey == 'apostrophe':
                    txt=edit(txt, 'apostrophe')

                if pygKey == 'minus':
                    txt=edit(txt, 'minus')

                if pygKey == 'quoteleft':
                    txt=edit(txt, 'quoteleft')

                if pygKey == 'bracketleft':
                    txt=edit(txt, 'bracketleft');

                if pygKey == 'bracketright':
                    txt=edit(txt, 'bracketright');

                if pygKey == 'lctrl':
                    txt=edit(txt, 'lctrl');

                if pygKey == 'capslock':
                    txt=edit(txt, 'capslock');


                if pygKey == 'up':
                    txt=edit(txt, 'up');

                if pygKey == 'down':
                    txt=edit(txt, 'down');

                if pygKey == 'right':
                    txt=edit(txt, 'right');

                if pygKey == 'left':
                    txt=edit(txt, 'left');

                if pygKey == 'comma':
                    txt=edit(txt, 'comma');

                if pygKey == 'slash':
                    txt=edit(txt, 'slash');

                if pygKey == '[':
                    txt=edit(txt, '[');

                if pygKey == ']':
                    txt=edit(txt, ']');

                if pygKey == 'equal':
                    txt=edit(txt, 'equal');

                if pygKey == 'equals':
                    txt=edit(txt, 'equals');

                if pygKey == 'period':
                    txt=edit(txt, 'period');

                if pygKey == 'backslash':
                    txt=edit(txt, 'backslash');

                if pygKey == '.':
                    txt=edit(txt, '.');

                if pygKey == ';':
                    txt=edit(txt, ';');

                if pygKey == ':':
                    txt=edit(txt, ':');

                if pygKey == 'semicolon':
                    txt=edit(txt, 'semicolon');

                if pygKey == 'tab':
                    txt=edit(txt, 'tab');

                if pygKey == 'command':
                    txt=edit(txt, 'command');

                if pygKey == 'lcommand':
                    txt=edit(txt, 'lcommand');

                if pygKey == 'rcommand':
                    txt=edit(txt, 'rcommand')

                if pygKey == 'loption':
                    txt=edit(txt, 'loption');

                if pygKey == 'roption':
                    txt=edit(txt, 'roption')

                if pygKey == '`':
                    txt=edit(txt, '`')

                if pygKey == 'rshift' or 'lshift' or 'shift':
                    txt=edit(txt, 'rshift');
                    txt=edit(txt, 'lshift');
                    txt=edit(txt, 'shift');

                if pygKey == 'space':
                    txt=edit(txt, 'space');
                    txt = txt + '-';

                if pygKey == 'backspace':
                    txt=edit(txt, 'backspace');
                    txt = txt[:-1];

                if pygKey == 'return':
                    txt=edit(txt, 'return')

                if pygKey == 'escape':
                    txt=edit(txt, 'escape')

                return txt

            try:

                kb = keyboard.Keyboard();
                timer = core.Clock();
                while continuing:

                    if i < N_TRIALS:
                        timer.reset();
                        kb.clock.reset();
                        key = sizeKey[i];
                        im = sizeImage(win, key);

                    if i >= N_TRIALS:
                        im.opacity=0;
                        msg.opacity=0;
                        msg2.opacity=0;
                        endBlock.opacity=1;
                        endText.opacity=1;
                        endText.text = 'Done!';
                        TASK_DONE = True;

                    im.draw();
                    msg.draw();
                    msg2.draw();
                    endBlock.draw();
                    endText.draw();
                    win.flip();

                    pygKey = event.waitKeys()[0]; core.wait(0.001);
                    ptbKey = kb.getKeys(waitRelease=False)[0];

                    if pygKey == 'escape':
                        continuing = False;
                        core.quit(); win.close();

                    if pygKey == 'return':
                        next_inc += 1;

                    txt = task_keys(txt, pygKey); msg.text = txt;

                    if next_inc == 0:
                        msg2.pos = (2000, 2000);
                        message = 'Name this object';
                        msg2.text = message;

                    if next_inc == 1:
                        msg2.pos = (0, 375);
                        message = 'Are you sure?';
                        msg2.text = message;

                    if pygKey == 'space' and next_inc == 1:

                        next_inc = 0;

                        msg = visual.TextStim(win, 'input text', height = 30)
                        msg.pos = (0, -325);
                        msg2.pos = (0, 375);

                        message = 'Name this object';
                        msg2.text = message;
                        txt = '';
                        win.flip();

                    if next_inc == 2:
                        userLabel = msg.text;
                        imageName = im.image;
                        index = findImageIndex(imageName);
                        dataDict[index]['userLabel'] = userLabel;
                        print("dataDict[index]['userLabel']: ", dataDict[index]['userLabel'])
                        saveData(dataDict);
                        imageName = imageName.replace('./stimuli/size/', '');
                        imageName = imageName.replace('.jpg.png-gaussian.png', '');
                        fileName = logFileDir + studyIDPrefix + subjectID + '_IMAGE_{}_objectNaming'.format(imageName);
                        savedFrame =  fileName + '.png';
                        win.getMovieFrame(buffer='front');
                        win.saveMovieFrames(savedFrame);
                        msg = visual.TextStim(win, 'input text', height = 30)
                        msg.pos = (0, -325);
                        msg2.pos = (0, 375);
                        message = 'Name this object';
                        msg2.text = message;
                        i += 1;
                        next_inc = 0;
                        txt = '';
                        win.flip();

                    if TASK_DONE == True:
                        userLabel = msg.text;
                        imageName = im.image;
                        index = findImageIndex(imageName);
                        dataDict[index]['userLabel'] = userLabel;
                        saveData(dataDict);
                        print('...OBJECT NAMING TASK COMPLETE')
                        event.waitKeys();
                        kb.stop()

                        del \
                        objectName,
                        dataDict,
                        endText,
                        endBlock,
                        pygKey,
                        ptbKey,
                        im,
                        msg,
                        msg2,
                        pygKey,
                        message,
                        txt,
                        next_inc,
                        taskInfo['objectNaming']['taskCompleted']=True;

                        # WRITE
                        logFilePrefix = '_DATA_taskInfo.csv';
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        df = pd.DataFrame(taskInfo).T
                        df.to_csv(logFileName, index = True, header=True)

                        break

            except:
                win.close()
                core.quit()

        #########################
        ## TASK: sizeRanking   ##
        #########################

        if task == 'sizeRanking':

            # Setup Background Image
            BG_PATH = './stimuli/background';
            BG_FILE = './stimuli/background/background.png.zip';
            unzipper = zipfile.ZipFile(BG_FILE, 'r');
            unzipper.extractall(BG_PATH); unzipper.close();

            try:
                print('...STARTING SIZE RANKING TASK')
                IMAGE_RESIZE_VAR = .45
                IMAGE_DIR='./stimuli/size/';
                GRID_DATA='./stimuli/grid/task_grid.xlsx';
                TXT_PROMPT_HEIGHT = 25;
                TXT_USERLABEL_HEIGHT = 22;
                TXT_PROMPT_COLOR = 'white';
                TXT_PROMPT_UNITS = 'pix';
                TXT_PROMPT_FONTS = 'Arial';
                TXT_PROMPT_SMALL = 'SMALL';
                TXT_PROMPT_LARGE = 'LARGE';
                TXT_PROMPT_SMALL_POSITION = (-560, 0);
                TXT_PROMPT_LARGE_POSITION = (560, 0);
                SMALL_GREY_BLOCK_POS = (560, 0);
                LARGE_GREY_BLOCK_POS = (-560, 0);
                TXT_PROMPT_MESSAGE = 'input text';
                WIN_WIDTH= 1280;
                WIN_HEIGHT= 1024;
                WIN_FULL_SCREEN= True;
                WIN_MONITOR= 'testMonitor';
                WIN_UNITS = 'pix';
                WIN_COLOR = 'gray';
                MESSAGE_POSITION = (0, 385);
                DEALER_POSITION = (0, 450);
                IMAGE_RESIZE_VAR= 1;

                IMAGE_SIZE= 60;
                IMAGE_WIDTH= IMAGE_SIZE;
                IMAGE_HEIGHT= IMAGE_SIZE;

                IMAGE_UNITS= 'pix';
                VM_SHOW_LIMIT_BOX = False;
                VM_CLICK_ON_UP = True;

                VM_WIDTH = 1920;
                VM_HEIGHT = 1080;

                GRID_WIDTH = 1280;
                GRID_HEIGHT = 1024;
                GRID_ROWS = 8;
                GRID_COLUMNS  = 8;
                GRID_RESIZE_WPX_VAR = .65;
                GRID_RESIZE_HPX_VAR = .63;
                GRID_VERT_SHIFT_VAR = (-15);
                CHOICE_BOUNDARY_WIDTH = 480*2;
                CHOICE_BOUNDARY_HEIGHT = 365*2;
                CHOICE_BOUNDARY_POSITION_SHIFT = (0, -15);
                DBLOCK01_WIDTH = 50;
                DBLOCK01_HEIGHT = 50;
                DBLOCK01_FILL_COLOR = 'black';
                DBLOCK01_LINE_COLOR = 'black';
                DBLOCK01_UNITS = 'pix';
                DBLOCK02_FILL_COLOR = 'white';
                DBLOCK02_LINE_COLOR = 'white';
                DBLOCK02_UNITS = 'pix';
                TBLOCK_WIDTH = 1200;
                TBLOCK_HEIGHT = 50;
                TBLOCK_FILL_COLOR = 'gray';
                TBLOCK_LINE_COLOR = 'gray';
                TBLOCK_UNITS = 'pix';
                TBLOCK_POSITION = (0, 385);
                RESIZED_IMAGE_POSITION = (0, 0);
                RESIZED_IMAGE_SIZE = (300, 300);

                def makeCoords(n_rows, n_cols, win_wpx, win_hpx, grid_vert_shift):
                    GridRows = np.linspace(-win_hpx/2, +win_hpx/2, n_rows)
                    GridCols = np.linspace(-win_wpx/2, +win_wpx/2, n_cols)
                    xGridCoords, yGridCoords = np.meshgrid(GridCols, GridRows)
                    yGridCoords += grid_vert_shift
                    return(xGridCoords, yGridCoords)

                def stackCoords(x, y):
                    x_list = [];
                    for i in x:
                        row = i;
                        for j in row:
                            # print(j)
                            x_list.append(j)
                    y_list = [];
                    for i in y:
                        col = i;
                        for j in col:
                            # print(j)
                            y_list.append(j)
                    task_grid = np.column_stack((x_list, y_list))
                    return task_grid

                def saveGrid():
                    n_rows = GRID_ROWS;
                    n_cols = GRID_COLUMNS;
                    win_wpx = (GRID_WIDTH*GRID_RESIZE_WPX_VAR);
                    win_hpx = (GRID_HEIGHT*GRID_RESIZE_HPX_VAR);
                    filepath ='./stimuli/grid/task_grid.xlsx';
                    x, y = makeCoords(n_rows, n_cols, win_wpx, win_hpx, GRID_VERT_SHIFT_VAR);
                    task_grid = stackCoords(x, y);
                    ## convert your array into a dataframe
                    df = pd.DataFrame(task_grid)
                    ## save to xlsx file
                    df.to_excel(filepath, index=False)

                saveGrid()

                dealer_VAR = True; undealer_VAR = False; redealer_VAR = False;
                TASK_DONE = False;
                switcher_VAR = False;
                sCOUNTS = 0;
                switch_done = False;
                index = 0;
                grey_im = []; grey_xy = []; grey_point = [];
                zCOUNTS = 0; INC = 0;
                BG_PNG_ZIP = './stimuli/background/background.png.zip';
                BG_PNG = './stimuli/background/background.png';
                BG_DIR = '/stimuli/background/background.png.zip';
                GRID_DATA ='./stimuli/grid/task_grid.xlsx';

                def grid_data():
                    import numpy as np
                    import pandas as pd
                    grid_points = pd.read_excel(GRID_DATA)
                    grid_points = np.array(grid_points)
                    point_keys = []; point_values = [];
                    for i in range(len(grid_points)):
                        point_key = "p" + str(i)
                        point_x, point_y = grid_points[i][0], grid_points[i][1]
                        point_value = (point_x, point_y)
                        point_keys.append(point_key)
                        point_values.append(point_value)
                        point_dictionary = dict(zip(point_keys, point_values))
                    return point_dictionary

                point_dictionary = grid_data();

                dealer = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/dealer.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = DEALER_POSITION);

                bg = visual.ImageStim(win,
                            image=BG_PNG)

                pointer = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image2 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        pos = (2000, 2000),
                        units = 'pix');

                image3 = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image4 = visual.ImageStim(
                        win,
                        image=  './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                choice_boundary = visual.Rect(
                        win,
                        width=CHOICE_BOUNDARY_WIDTH,
                        height=CHOICE_BOUNDARY_HEIGHT,
                        units = 'pix');
                choice_boundary.pos += CHOICE_BOUNDARY_POSITION_SHIFT;

                def unzip(BG_PNG_ZIP):
                    CURRENT_DIR = os.getcwd()
                    zip_ref = zipfile.ZipFile(BG_PNG_ZIP, 'r')
                    zip_ref.extractall(CURRENT_DIR)
                    zip_ref.close()

                small = visual.TextStim(win,
                    height = TXT_PROMPT_HEIGHT,
                    pos=TXT_PROMPT_SMALL_POSITION,
                    text=TXT_PROMPT_SMALL,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    units=TXT_PROMPT_UNITS)

                large = visual.TextStim(win,
                    height = TXT_PROMPT_HEIGHT,
                    pos=TXT_PROMPT_LARGE_POSITION,
                    text=TXT_PROMPT_LARGE,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    units=TXT_PROMPT_UNITS)

                message = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    text=TXT_PROMPT_MESSAGE,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                dealerBlock1 = visual.Rect(win,
                        width=DBLOCK01_WIDTH,
                        height=DBLOCK01_HEIGHT,
                        fillColor = DBLOCK01_FILL_COLOR,
                        lineColor = DBLOCK01_LINE_COLOR,
                        units=DBLOCK01_UNITS);

                dealerBlock2 = visual.Rect(win,
                        width =IMAGE_WIDTH,
                        height =IMAGE_HEIGHT,
                        fillColor = DBLOCK02_FILL_COLOR,
                        lineColor = DBLOCK02_LINE_COLOR,
                        units = DBLOCK02_UNITS);

                textBlock = visual.Rect(win,
                        width=TBLOCK_WIDTH,
                        height=TBLOCK_HEIGHT,
                        fillColor = TBLOCK_FILL_COLOR,
                        lineColor = TBLOCK_LINE_COLOR,
                        units=TBLOCK_UNITS);

                dealerBlock2.autoDraw = True;

                dealerBlock1.pos = DEALER_POSITION;
                dealerBlock2.pos = DEALER_POSITION;
                textBlock.pos = TBLOCK_POSITION;

                dealerBlock1.setOpacity(1);
                dealerBlock2.setOpacity(0);

                def resizedImage(image):
                    resized_image = visual.ImageStim(
                            win,
                            image=image,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = RESIZED_IMAGE_POSITION);
                    resized_image.size = RESIZED_IMAGE_SIZE;
                    return resized_image

                zoomBackground = visual.Rect(
                        win,
                        fillColor = 'grey',
                        lineColor = None,
                        width=2000,
                        height=2000,
                        units = 'pix');

                zoomImage = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/undealer.png',
                        size=(600, 600),
                        units = IMAGE_UNITS,
                        pos = (15, 50));

                zoomText = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    text='',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                zoomBackground.setOpacity(0);
                zoomImage.setOpacity(0);
                zoomText.setOpacity(0);

                selection = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 1.0,
                        units = 'pix');

                selection.setOpacity(0);

                selection2 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'gray',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 3,
                        units = 'pix');

                selection2.setOpacity(0);
                selection.autoDraw = True;
                selection2.autoDraw = True;

                selection3 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 1.0,
                        units = 'pix');

                selection3.setOpacity(0);
                selection3.autoDraw = True;

                # import numpy as np
                # vert_lines = np.linspace(-480, 480, num=9);
                # for i in vert_lines:
                #     print(i)
                # -480.0
                # -360.0
                # -240.0
                # -120.0
                # 0.0
                # 120.0
                # 240.0
                # 360.0
                # 480.0

                sort01_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02a_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02b_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03a_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03b_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03c_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03d_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')

                sort01_vert.start = [0, -380];
                sort01_vert.end = [0, +350];
                sort02a_vert.start = [-240, -380];
                sort02a_vert.end = [-240, +350];
                sort02b_vert.start = [240, -380];
                sort02b_vert.end = [240, +350];
                sort03a_vert.start = [-120, -380];
                sort03a_vert.end = [-120, +350];
                sort03b_vert.start = [120, -380];
                sort03b_vert.end = [120, +350];
                sort03c_vert.start = [-365, -380];
                sort03c_vert.end = [-365, +350];
                sort03d_vert.start = [365, -380];
                sort03d_vert.end = [365, +350];

                SORT_VERT_LINE_WIDTH = .9;

                sort01_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort02a_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort02b_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03a_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03b_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03c_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03d_vert.lineWidth = (SORT_VERT_LINE_WIDTH);

                sort01_vert.setOpacity(1);
                sort02a_vert.setOpacity(0);
                sort02b_vert.setOpacity(0);
                sort03a_vert.setOpacity(0);
                sort03b_vert.setOpacity(0);
                sort03c_vert.setOpacity(0);
                sort03d_vert.setOpacity(0);

                sort01_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02a_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02b_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03a_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03b_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03c_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03d_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')

                sort01_vert_grey.start = [0, -380];
                sort01_vert_grey.end = [0, +350];
                sort02a_vert_grey.start = [-240, -380];
                sort02a_vert_grey.end = [-240, +350];
                sort02b_vert_grey.start = [240, -380];
                sort02b_vert_grey.end = [240, +350];
                sort03a_vert_grey.start = [-120, -380];
                sort03a_vert_grey.end = [-120, +350];
                sort03b_vert_grey.start = [120, -380];
                sort03b_vert_grey.end = [120, +350];
                sort03c_vert_grey.start = [-365, -380];
                sort03c_vert_grey.end = [-365, +350];
                sort03d_vert_grey.start = [365, -380];
                sort03d_vert_grey.end = [365, +350];

                SORT_VERT_GREY_LINE_WIDTH = 1.1;

                sort01_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort02a_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort02b_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03a_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03b_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03c_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03d_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);

                sort01_vert_grey.setOpacity(0);
                sort02a_vert_grey.setOpacity(0);
                sort02b_vert_grey.setOpacity(0);
                sort03a_vert_grey.setOpacity(0);
                sort03b_vert_grey.setOpacity(0);
                sort03c_vert_grey.setOpacity(0);
                sort03d_vert_grey.setOpacity(0);

                # import numpy as np
                # horiz_lines = np.linspace(350, -380, num=9);
                # for i in horiz_lines:
                #     print(i)

                # 350.0
                # 258.75
                # 167.5
                # 76.25
                # -15.0
                # -106.25
                # -197.5
                # -288.75
                # -380.0

                sort01_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02a_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02b_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03a_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03b_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03c_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03d_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')

                sort01_horiz.start = [-480, 258.75];
                sort01_horiz.end = [480, 258.75];
                sort02a_horiz.start = [-480, 167.5];
                sort02a_horiz.end = [480, 167.5];
                sort02b_horiz.start = [-480, 76.25];
                sort02b_horiz.end = [480, 76.25];
                sort03a_horiz.start = [-480, -15.0];
                sort03a_horiz.end = [480, -15.0];
                sort03b_horiz.start = [-480, -106.25];
                sort03b_horiz.end = [480, -106.25];
                sort03c_horiz.start = [-480, -197.5];
                sort03c_horiz.end = [480, -197.5];
                sort03d_horiz.start = [-480, -288.75];
                sort03d_horiz.end = [480, -288.75];

                SORT_HORIZ_LINE_WIDTH = .9;

                sort01_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort02a_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort02b_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03a_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03b_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03c_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03d_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);

                # sort01_horiz.setOpacity(1);
                # sort02a_horiz.setOpacity(1);
                # sort02b_horiz.setOpacity(1);
                # sort03a_horiz.setOpacity(1);
                # sort03b_horiz.setOpacity(1);
                # sort03c_horiz.setOpacity(1);
                # sort03d_horiz.setOpacity(1);

                sort01_horiz.setOpacity(0);
                sort02a_horiz.setOpacity(0);
                sort02b_horiz.setOpacity(0);
                sort03a_horiz.setOpacity(0);
                sort03b_horiz.setOpacity(0);
                sort03c_horiz.setOpacity(0);
                sort03d_horiz.setOpacity(0);

                sort01_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02a_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02b_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03a_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03b_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03c_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03d_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')

                sort01_horiz_grey.start = [-480, 258.75];
                sort01_horiz_grey.end = [480, 258.75];
                sort02a_horiz_grey.start = [-480, 167.5];
                sort02a_horiz_grey.end = [480, 167.5];
                sort02b_horiz_grey.start = [-480, 76.25];
                sort02b_horiz_grey.end = [480, 76.25];
                sort03a_horiz_grey.start = [-480, -15.0];
                sort03a_horiz_grey.end = [480, -15.0];
                sort03b_horiz_grey.start = [-480, -106.25];
                sort03b_horiz_grey.end = [480, -106.25];
                sort03c_horiz_grey.start = [-480, -197.5];
                sort03c_horiz_grey.end = [480, -197.5];
                sort03d_horiz_grey.start = [-480, -288.75];
                sort03d_horiz_grey.end = [480, -288.75];

                sort01_horiz_grey.setOpacity(0);
                sort02a_horiz_grey.setOpacity(0);
                sort02b_horiz_grey.setOpacity(0);
                sort03a_horiz_grey.setOpacity(0);
                sort03b_horiz_grey.setOpacity(0);
                sort03c_horiz_grey.setOpacity(0);
                sort03d_horiz_grey.setOpacity(0);

                SORT_HORIZ_GREY_LINE_WIDTH = 1.1;

                sort01_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort02a_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort02b_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03a_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03b_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03c_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03d_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);

                test_rect = visual.Rect(win,
                        width=800,
                        height=150,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect.pos = [4000, 4000];

                test_rect2 = visual.Rect(win,
                        width=1240,
                        height=155,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect2.pos = [4000, 4000];

                test_rect_bottom1 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom1.pos = [0, -450]

                test_rect_bottom2 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom2.pos = [4000, 4000];

                test_rect_bottom3 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom3.pos = [4000, 4000];

                end_round_block = visual.Rect(
                        win,
                        fillColor = 'white',
                        lineColor = 'white',
                        width=2000,
                        height=2000,
                        lineWidth = 1,
                        pos = (0, 0),
                        units = 'pix');
                end_round_block.setOpacity(0);

                begin_round_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'white',
                        width=500,
                        height=500,
                        lineWidth = 1,
                        pos = (0, 0),
                        units = 'pix');
                begin_round_block.setOpacity(0);

                begin_round_text_part1 = visual.TextStim(win,
                    height = 30,
                    pos=(0,100),
                    text="You have completed round 1",
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                begin_round_text_part2 = visual.TextStim(win,
                    height = 30,
                    pos=(0,-100),
                    text='...press "return" to begin round 2...',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                begin_round_text_part1.pos = (4000,4000);
                begin_round_text_part2.pos = (4000,4000);

                small_gray_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'gray',
                        width=100,
                        height=100,
                        lineWidth = 1,
                        units = 'pix');

                large_gray_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'gray',
                        width=100,
                        height=100,
                        lineWidth = 1,
                        units = 'pix');

                small_gray_block.pos = SMALL_GREY_BLOCK_POS;
                large_gray_block.pos = LARGE_GREY_BLOCK_POS;

                small_size_ranking_line_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='yellow')
                small_size_ranking_line_horiz.start = [-480, -465];
                small_size_ranking_line_horiz.end = [-250, -465];

                large_size_ranking_line_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='yellow')
                large_size_ranking_line_horiz.start = [480, -465];
                large_size_ranking_line_horiz.end = [250, -465];

                ROUND_TWO_TEXT = u"Sort the objects into 4 groups of roughly same-sized objects. From left to right, object groups should reflect increases in size. After you're finished, press 'return'. "

                ROUND_THREE_TEXT = u"Sort the objects into 8 groups of roughly same-sized objects. From left to right, object groups should reflect increases in size. After you're finished, press 'return'. "

                message2 = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                message2.text = ROUND_THREE_TEXT;
                message2.pos = (4000, 4000);

                end_round_text_prompt = visual.TextStim(win,
                    height = 30,
                    text='',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                end_round_text_prompt.pos = (4000, 4000);

                end_task_text_prompt = visual.TextStim(win,
                    height = 30,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                end_task_text_prompt.pos = (4000, 4000);
                END_TASK_PROMPT_TEXT = '...press "return" to quit...';
                end_task_text_prompt.text = END_TASK_PROMPT_TEXT;

                r1_y = -430;
                rtext_size = (50, 50);
                rtext_color = 'white';
                rtext_units = 'pix';

                r1_text = visual.TextStim(win, '1', color=rtext_color, units=rtext_units);
                r2_text = visual.TextStim(win, '2', color=rtext_color, units=rtext_units);
                r3_text = visual.TextStim(win, '3', color=rtext_color, units=rtext_units);
                r4_text = visual.TextStim(win, '4', color=rtext_color, units=rtext_units);
                r5_text = visual.TextStim(win, '5', color=rtext_color, units=rtext_units);
                r6_text = visual.TextStim(win, '6', color=rtext_color, units=rtext_units);
                r7_text = visual.TextStim(win, '7', color=rtext_color, units=rtext_units);
                r8_text = visual.TextStim(win, '8', color=rtext_color, units=rtext_units);

                class dictObj(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value1, value2):
                        self[key] = value1, value2
                switch_dict = dictObj();
                resize_COUNT = 0;
                def quit(win):
                    QUIT_KEYS = event.getKeys('0')
                    if len(QUIT_KEYS) > 0:

                        # imageName = image_value.replace('./stimuli/size/', '');
                        # imageName = imageName.replace('.jpg.png-gaussian.png', '');
                        # fileName = logFileDir + studyIDPrefix + subjectID + '_IMAGE_{}_sizeRanking'.format(imageName);
                        # savedFrame =  fileName + '.png';
                        # win.getMovieFrame(buffer='front');
                        # win.saveMovieFrames(savedFrame);

                        core.quit();
                        win.close()

                resize_VAR = False;
                point_dictionary_backup = grid_data();
                ROUND_TWO_VAR = False;
                ROUND_THREE_VAR = False;
                ZOOM_TEXT = '???';

                def getUserLabels():
                    logFilePrefix = '_DATA_objectNaming.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                    nameLib = pd.read_csv(logFileName);
                    nameLib = nameLib.T

                    nameLib = nameLib.drop(nameLib.index[0])
                    # nameLib.drop(nameLib.index[1])
                    cols = ['image', 'userLabel']
                    nameLib.columns = cols;
                    # nameLib.columns
                    fileNames = (nameLib['image'].values).tolist();
                    userLabels = (nameLib['userLabel'].values).tolist();
                    return fileNames, userLabels

                fileNames, userLabels = getUserLabels()

                def point_tools(vm):

                    sort01_KEYS = event.getKeys('t')
                    if len(sort01_KEYS) > 0:
                        # sort01_vert.setOpacity(1);
                        print('image3.pos: ', image3.pos)
                        print('image3.image: ', image3.image)
                        print('image4.pos: ', image4.pos)
                        print('image4.image: ', image4.image)
                        print('image.pos: ', image.pos)
                        print('image.image: ', image.image)

                    sort02_KEYS = event.getKeys('y')
                    if len(sort02_KEYS) > 0:
                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);

                    sort03_KEYS = event.getKeys('u')
                    if len(sort03_KEYS) > 0:

                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);
                        sort03a_vert.setOpacity(1);
                        sort03b_vert.setOpacity(1);
                        sort03c_vert.setOpacity(1);
                        sort03d_vert.setOpacity(1);


                    sort01_horiz_KEYS = event.getKeys('t')
                    if len(sort01_horiz_KEYS) > 0:
                        sort01_vert.setOpacity(1);

                    sort02_horiz_KEYS = event.getKeys('y')
                    if len(sort02_KEYS) > 0:
                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);

                    sort03_horiz_KEYS = event.getKeys('u')
                    if len(sort03_horiz_KEYS) > 0:

                        sort01_horiz_vert.setOpacity(1);
                        sort02a_horiz_vert.setOpacity(1);
                        sort02b_horiz_vert.setOpacity(1);
                        sort03a_horiz_vert.setOpacity(1);
                        sort03b_horiz_vert.setOpacity(1);
                        sort03c_horiz_vert.setOpacity(1);
                        sort03d_horiz_vert.setOpacity(1);


                    N_POPPED_IMAGES = event.getKeys('1')
                    if len(N_POPPED_IMAGES) > 0:
                        print('N_POPPED_IMAGES: ', len(popped_images));

                    LIST_POPPED_IMAGES = event.getKeys('9')
                    if len(LIST_POPPED_IMAGES) > 0:
                        itemlist1=[];
                        itemlist2=[];
                        for i in popped_images:
                            print('LIST_POPPED_IMAGES: ', popped_images[i]);
                            itemlist.append(i, popped_images[i])

                        with open('LIST_POPPED_IMAGES', 'wb') as fp:
                            pickle.dump(itemlist, fp)


                    LIST_POPPED_IMAGES = event.getKeys('2')
                    if len(LIST_POPPED_IMAGES) > 0:

                        itemlist1=[];
                        itemlist2=[];
                        itemlist3=[];
                        itemlist4=[];

                        for i in popped_images:
                            print('LIST_POPPED_IMAGES: ', popped_images[i]);
                            itemlist1.append(i)
                            itemlist2.append(popped_images[i])

                        with open('LIST_POPPED_imKEYS', 'wb') as fp:
                            pickle.dump(itemlist1, fp)

                        with open('LIST_POPPED_IMAGES', 'wb') as fp:
                            pickle.dump(itemlist2, fp)

                        for i in popped_dictionary:
                            print('LIST_POPPED_POINTS: ', i);
                            print('LIST_POPPED_XYs: ', popped_dictionary[i]);
                            itemlist3.append(i)
                            itemlist4.append(popped_dictionary[i])

                        with open('LIST_POPPED_pKEYS', 'wb') as fp:
                            pickle.dump(itemlist3, fp)

                        with open('LIST_POPPED_XYs', 'wb') as fp:
                            pickle.dump(itemlist4, fp)

                    N_AVAILABLE_POINTS = event.getKeys('3')
                    if len(N_AVAILABLE_POINTS) > 0:
                        print('N_AVAILABLE_POINTS: ', len(point_dictionary));

                    CLOSEST_POINT = event.getKeys('4')
                    if len(CLOSEST_POINT) > 0:
                        closest_point = new_position(vm, point_dictionary_backup)
                        print('CLOSEST POINT: ', closest_point);

                    N_POPPED_POINTS = event.getKeys('5')
                    if len(N_POPPED_POINTS) > 0:
                        print('N_POPPED_POINTS: ', len(popped_dictionary));

                    LIST_POPPED_POINTS = event.getKeys('6')
                    if len(LIST_POPPED_POINTS) > 0:
                        itemlist=[];
                        for i in popped_dictionary:
                            print('LIST_POPPED_POINTS: ', i);
                            print('LIST_POPPED_(XY): ', popped_dictionary[i]);
                            itemlist.append(i, popped_dictionary[i])

                    N_POPPED_IMAGES = event.getKeys('7')
                    if len(N_POPPED_IMAGES) > 0:
                        print('N_POPPED_IMAGES: ', len(popped_images));

                def zoom(win, vm, zoomImage, selection2, selection):
                    zoomText.pos = (0, -365)
                    zoomText.height = 35;
                    message.setOpacity(0);

                    selection.setOpacity(0)
                    selection2.setOpacity(0)

                    point_key = new_position(vm, point_dictionary_backup)
                    imDict = set_images[point_key];

                    if imDict['image'] != None:
                        imageName = imDict['image'];
                        ZOOM_IMAGE = imageName;
                        zoomImage.image = ZOOM_IMAGE;
                        if imageName in fileNames:
                            index = fileNames.index(imageName)
                            userLabel = userLabels[index];
                            ZOOM_TEXT = userLabel;
                            message.setOpacity(0)
                            zoomBackground.setOpacity(1);
                            zoomImage.setOpacity(1);
                            zoomText.setOpacity(1);
                            win.mouseVisible = False;

                            return ZOOM_TEXT

                        elif imageName not in fileNames:

                            message.setOpacity(0)
                            zoomBackground.setOpacity(1);
                            zoomImage.setOpacity(1);
                            zoomText.setOpacity(1);

                            ZOOM_IMAGE = imageName;

                            print("elif imageName not in fileNames: ", ZOOM_IMAGE)
                            zoomImage.image = ZOOM_IMAGE;

                            userLabel = '???';
                            ZOOM_TEXT = userLabel;
                            win.mouseVisible = False;
                            return ZOOM_TEXT

                def shrink(win, vm, zoomImage, selection2, selection):

                    selection.setOpacity(0)
                    selection2.setOpacity(0);
                    zoomBackground.setOpacity(0);
                    zoomImage.setOpacity(0);
                    zoomImage.opacity = 0;
                    message.setOpacity(1)
                    win.mouseVisible = True;

                    message.opacity = 1;
                    zoomText.setOpacity(1);
                    zoomText.pos = (2000, 2000);

                    point_key = new_position(vm, point_dictionary_backup)
                    print(point_key)
                    imDict = set_images[point_key];

                    if imDict['image'] != None:
                        imageName = imDict['image'];
                        if imageName in fileNames:
                            ZOOM_IMAGE = imageName;
                            zoomImage.image = ZOOM_IMAGE;
                            index = fileNames.index(imageName)
                            userLabel = userLabels[index];
                            ZOOM_TEXT = userLabel;

                def imageZoomer(win, vm, resize_VAR, zoomImage, selection2, selection):

                    ZOOM_KEYS = event.getKeys('s');

                    if len(ZOOM_KEYS) > 0:

                        if resize_VAR == False:
                            ZOOM_TEXT = zoom(win, vm, zoomImage, selection2, selection);
                            resize_VAR = True;
                            return resize_VAR, ZOOM_TEXT

                        if resize_VAR == True:
                            ZOOM_TEXT = shrink(win, vm, zoomImage, selection2, selection);
                            resize_VAR = False;
                            return resize_VAR, ZOOM_TEXT

                            logFilePrefix = '_DATA_sizeRanking.csv';
                            logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                            point_dictionary_backup = grid_data();
                            nuu = None;
                            text = None;

                            SELF_DIR = os.path.dirname(__file__);
                            TASK_DIR = os.path.abspath(SELF_DIR);
                            TASK_DIR = SELF_DIR + TASK_DIR;

                fileNames, userLabels = getUserLabels()

                blank1 = [];
                blank2 = [];
                blank3 = [];

                sCOUNTS = 0;
                index = 0;
                switch_dict = dictObj();
                switch_dict2 = dictObj();

                class dictObj2(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value):
                        self[key] = value

                class dictObj3(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value1, value2, value3):
                        self[key] = value1, value2, value3

                def dealer_image(INC, obj):
                    if INC < N_TRIALS:
                        image_key = 'im'+ str(INC);
                        image_value = image_dict[image_key];
                        try:
                            imageName = image_value;
                            index = fileNames.index(imageName);
                            userLabel = userLabels[index];
                            obj.text = userLabel;
                        except (IndexError, ValueError):
                            userLabel = '???';
                            obj.text = userLabel;

                    if INC >= N_TRIALS:
                        image_value = './stimuli/dealers/image.png';
                    image = visual.ImageStim(win,
                                    image=image_value,
                                    pos  = DEALER_POSITION,
                                    size = (IMAGE_WIDTH,
                                            IMAGE_HEIGHT));

                    return image

                def update_image(INC):
                    image_key = 'im'+ str(INC);
                    image_value = image_dict[image_key];
                    popped_images.update({image_key: image_value})
                    image = visual.ImageStim(win,
                                    image=image_value,
                                    size = (IMAGE_WIDTH,
                                            IMAGE_HEIGHT));

                    return image

                def CHOICE_UPDATE(INC, dealerBlock2):
                    image = update_image(INC); dealerBlock2.opacity = 0.0;
                    point_key = new_position(vm, point_dictionary);
                    point_value = point_dictionary.pop(point_key);
                    popped_dictionary.update({point_key:point_value});
                    image.pos = point_value;
                    element = set_images[point_key];
                    element['(x, y)'] = point_value;
                    element['image'] = images_key[INC]
                    set_image_key = point_key.replace('p', 'im');
                    element['set_image_key'] = set_image_key;
                    switch_dict.add(point_key, point_value, image.image)
                    set_images.update(element); INC += 1;
                    save_background(); bg = update_background(BG_PNG);
                    pointer.setOpacity(0); dealer_VAR = True;
                    vm.pointer = pointer; vm.visible = True;
                    return image, bg, INC, vm, dealer_VAR

                def pointer_update(INC, pointer, vm, dealer):
                    del pointer, vm
                    pointer = update_image(INC)
                    return pointer

                def reset_vm(vm):
                    vm.visible = True;
                    return vm

                def dealer_tools(dealerBlock2, vm):
                    dealerBlock2.opacity = .60;
                    vm.visible = True;

                def get_setImages():
                    return set_images

                def unsetter_image(point_key, point_value):
                    image_key = set_images[point_key]['image'];
                    image = image_key;
                    grey_im.append(image);
                    return image

                def unsetter_pointer(image_key):
                    pointer = visual.ImageStim(win,
                                    image=image_key,
                                    size = (IMAGE_WIDTH, IMAGE_HEIGHT));
                    return pointer

                def unsetter_keys(undealer_VAR, zCOUNTS, sCOUNTS, image, INC):
                    popped_size = len(popped_dictionary);
                    UNSETTER_KEYS = event.getKeys('d')

                    if len(UNSETTER_KEYS) > 0 and popped_size > 0 and zCOUNTS == 0 and sCOUNTS == 0:
                        point_key = new_position(vm, popped_dictionary);
                        point_value = popped_dictionary.pop(point_key);
                        del switch_dict[point_key]
                        image_key = unsetter_image(point_key, point_value);
                        vm.pointer = unsetter_pointer(image_key);
                        vm.visible = True; undealer_VAR = True;
                        grey_point.append(point_key); grey_xy.append(point_value);
                        return undealer_VAR
                    else:
                        pass

                def resetter_keys(switcher_VAR, vm, sCOUNTS, zCOUNTS):
                    popped_size = len(popped_dictionary);
                    SWITCHER_KEYS = event.getKeys('f')

                    if len(SWITCHER_KEYS) > 0 and popped_size > 0 and sCOUNTS == 0 and zCOUNTS == 0 and switcher_VAR != True:
                        tmp_dict = dictObj2();
                        for i in switch_dict:
                            tmp_dict.add(i, switch_dict[i][0])
                        switcher_VAR = True;
                        point_key = new_position(vm, tmp_dict);
                        point_value = switch_dict[point_key][0];

                        imDict = set_images[point_key];

                        selection.setOpacity(1);
                        selection2.setOpacity(0);
                        selection.pos = point_value;
                        selection2.pos = point_value;
                        image_name = switch_dict[point_key][1];

                        blank1.append(point_key)
                        blank2.append(point_value)
                        blank3.append(image_name)
                        globals()['sCOUNTS']=1;

                        return switcher_VAR
                    else:
                        pass

                def buffer_stimuli(stimlist):
                    rect = (-1, 1, 1, -1);
                    stimulus_display = visual.BufferImageStim(win,
                                            stim=stimlist,
                                            rect=rect);
                    return stimulus_display

                def DEALER_UPDATE(pointer):
                    vm.pointer = pointer; dealer_VAR = False;
                    return dealer_VAR, vm

                def pop_task_variables():
                    point_key = grey_point.pop();
                    point_value = grey_xy.pop();
                    image_key = grey_im.pop();
                    return point_key, point_value, image_key

                def zUNDEALER_UPDATE(image3, image4):
                    image3.opacity = 0; image4.opacity = 0; redealer_VAR = True;
                    image = visual.ImageStim(win,
                        image='./stimuli/dealers/image.png',
                        size = (IMAGE_WIDTH,IMAGE_WIDTH),
                        pos = grey_xy);
                    save_background();bg = update_background(BG_PNG)
                    return image, bg, redealer_VAR

                def zUNDEAL_DATA(data_dict):
                    point_key, point_value, image_key = pop_task_variables();
                    point_dictionary[point_key] = point_value;
                    data_dict[image_key] = point_key;
                    return point_key, point_value, image_key

                def zRESETTER_UPDATE(image_key, data_dict):
                    point_key = new_position(vm, point_dictionary);
                    point_value = point_dictionary.pop(point_key);
                    popped_dictionary.update({point_key:point_value});
                    image = visual.ImageStim(win,
                        image=image_key,
                        size = (IMAGE_WIDTH,IMAGE_WIDTH),
                        pos = point_value);
                    element = set_images[point_key];
                    element['(x, y)'] = point_value;
                    element['image'] = image_key;
                    set_image_key = point_key.replace('p', 'im');
                    element['set_image_key'] = set_image_key;
                    set_images.update(element); undealer_VAR = False;
                    switch_dict.add(point_key, point_value, image_key);
                    save_background(); bg = update_background(BG_PNG);
                    return undealer_VAR, image, bg

                def sREDEAL_DATA(sCOUNTS, index):
                    index += 1;
                    # FIXED
                    # image3.opacity = 0; image4.opacity = 0;
                    switch_dict2 = dictObj3();
                    switch_dict2.add(index, blank1[0], blank2[0], blank3[0]);
                    blank1.pop(); blank2.pop(); blank3.pop();
                    switcher_VAR = False;
                    return sCOUNTS, index, switcher_VAR, switch_dict2

                def sRESETTER_UPDATE(index, switch_dict2):
                    tmp_dict = dictObj2();
                    for i in switch_dict:
                        tmp_dict.add(i, switch_dict[i][0])
                    switcher_VAR = True;
                    point_key = new_position(vm, tmp_dict);
                    point_value = switch_dict[point_key][0];
                    image_name = switch_dict[point_key][1];
                    index += 1;

                    switch_dict2.add(index, point_key, point_value, image_name);
                    set_images[switch_dict2[1][0]]['(x, y)']= switch_dict2[2][1];
                    set_images[switch_dict2[1][0]]['image']= switch_dict2[2][2];
                    set_images[switch_dict2[2][0]]['(x, y)']= switch_dict2[1][1];
                    set_images[switch_dict2[2][0]]['image']= switch_dict2[1][2];
                    tmp3 = switch_dict2[2][2];
                    tmp4 = switch_dict2[1][2];


                    globals()['image3'] = visual.ImageStim(
                            win,
                            image=tmp4,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = switch_dict2[2][1]);

                    globals()['image4'] = visual.ImageStim(
                            win,
                            image=tmp3,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = switch_dict2[1][1]);

                    point_key1 = switch_dict2[1][0]
                    point_key2 = switch_dict2[2][0]
                    if point_key1 != point_key2:
                        tmp_point_key1 = switch_dict.pop(point_key1)
                        tmp_point_key2 = switch_dict.pop(point_key2)
                        switch_dict.add(point_key1, tmp_point_key1[0], tmp_point_key2[1])
                        switch_dict.add(point_key2, tmp_point_key2[0], tmp_point_key1[1])

                    globals()['sCOUNTS']=0;
                    del switch_dict2

                popped_dictionary = {};
                set_images = {};
                for i in range(100):
                    popped_point_key = 'p' + str(i);
                    set_image_key = 'im' + str(i);
                    popped_point_value = None
                    set_image_value = None
                    element = {popped_point_key: {
                                        '(x, y)': popped_point_value,
                                        'image': set_image_value,
                                        'set_image_key': set_image_key}}
                    set_images.update(element)
                images_key = getTaskObjects('size')
                random.shuffle(images_key);
                image_dict={};
                for i in range(60):
                    try:
                        image_dict.update({'im'+str(i):images_key[i]})
                    except IndexError:
                        image_dict.update({'im'+str(i):None})

                popped_images = {};

                def mouse_pos(vm):
                    mouse_x, mouse_y = vm.getPos()[0], vm.getPos()[1]
                    return mouse_x, mouse_y

                def calc_distances(vm, dictionary):
                    mouse_x, mouse_y = mouse_pos(vm)
                    for i in dictionary:
                        point_key = i;
                        point_x, point_y = dictionary[i];
                        mouse_dist = math.sqrt(np.linalg.norm(mouse_x-point_x) + np.linalg.norm(mouse_y-point_y));
                        yield point_key, mouse_dist

                def find_closest(calculated_distances):
                    distance_keys = []; distance_values = [];
                    for i, j in calculated_distances:
                        distance_keys.append(i)
                        distance_values.append(j)
                    closest_point = distance_keys[distance_values.index(min(distance_values))];
                    del calculated_distances, distance_values, distance_keys
                    return closest_point

                def new_position(vm, dictionary):
                    vm.visible = False; vm.resetClicks();
                    calculated_distances = calc_distances(vm, dictionary);
                    closest_point = find_closest(calculated_distances);
                    return closest_point

                def update_background(BG_PNG):
                    background = visual.ImageStim(win, image=BG_PNG);
                    return background

                def save_background():
                    win.getMovieFrame(buffer='back'); win.saveMovieFrames(BG_PNG);

                BG_PATH = './stimuli/background';
                BG_FILE = './stimuli/background/background.png.zip';

                unzipper = zipfile.ZipFile(BG_FILE, 'r');
                unzipper.extractall(BG_PATH); unzipper.close();

                DONE = False;
                resize_COUNT=0;
                NEW2 = '';
                imageZoomer_VAR = None;
                ROUND_TWO_COUNT = 0;
                ROUND_THREE_COUNT = 0;
                ROUND_FOUR_VAR = False;
                ROUND_FOUR_COUNT = 0;
                ROUND_FIVE_VAR = False;
                ROUND_FIVE_COUNT = 0;
                ROUND_SIX_COUNT = 0;

                def saveData(dataDict):

                    logFilePrefix = '_DATA_sizeRanking.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                    cols = [
                        'sizeKey',
                        'image',
                        'pointKey',
                        'xy'
                    ];

                    df = pd.DataFrame.from_dict(dataDict, orient='index')
                    df.columns = cols;
                    df.to_csv(logFileName, index = False, header=True)

                def keyCounter(x):
                    if event.getKeys(["return"]):
                        x+=1
                    return x

                data_dict={};

                TASK_COMPLETE = False;
                vm.visible = False;
                undealer_VAR = False;
                redealer_VAR = False;
                blank1 = [];
                blank2 = [];
                blank3 = [];
                sCOUNTS = 0;
                index = 0;
                switch_dict = dictObj();
                switch_dict2 = dictObj();
                data_dict = {};

                while True:
                # try:
                    if INC < N_TRIALS:

                        r1_text.opacity = 1;
                        r2_text.opacity = 1;
                        r3_text.opacity = 0;
                        r4_text.opacity = 0;
                        r5_text.opacity = 0;
                        r6_text.opacity = 0;
                        r7_text.opacity = 0;
                        r8_text.opacity = 0;

                        r1_text_position = (-275, r1_y);
                        r2_text_position = (275, r1_y);
                        r3_text_position = (4000, 4000);
                        r4_text_position = (4000, 4000);
                        r5_text_position = (4000, 4000);
                        r6_text_position = (4000, 4000);
                        r7_text_position = (4000, 4000);
                        r8_text_position = (4000, 4000);

                        r1_text.pos = r1_text_position;
                        r2_text.pos = r2_text_position;
                        r3_text.pos = r3_text_position;
                        r4_text.pos = r4_text_position;
                        r5_text.pos = r5_text_position;
                        r6_text.pos = r6_text_position;
                        r7_text.pos = r7_text_position;
                        r8_text.pos = r8_text_position;

                    if INC >= N_TRIALS:
                        test_rect2.pos = [0, 432]
                        ROUND_TWO_VAR = True;
                        message.text = ROUND_TWO_TEXT;
                        message.wrapWidth=600;
                        message.alignHoriz='center';
                        message.alignVert='bottom';

                    dealer = dealer_image(INC, message);

                    image_name = 'im'+ str(INC);
                    message.pos = MESSAGE_POSITION;
                    stimlist = [bg, dealerBlock1, dealer, choice_boundary, image];

                    display = buffer_stimuli(stimlist);
                    display.draw();

                    textBlock.draw();

                    small_gray_block.draw();
                    large_gray_block.draw();

                    small.draw();
                    large.draw();

                    image3.draw();
                    image4.draw();

                    test_rect2.draw();

                    message.draw();

                    sort01_vert_grey.draw();
                    sort02a_vert_grey.draw();
                    sort02b_vert_grey.draw();
                    sort03a_vert_grey.draw();
                    sort03b_vert_grey.draw();
                    sort03c_vert_grey.draw();
                    sort03d_vert_grey.draw();

                    sort01_vert.draw();
                    sort02a_vert.draw();
                    sort02b_vert.draw();
                    sort03a_vert.draw();
                    sort03b_vert.draw();
                    sort03c_vert.draw();
                    sort03d_vert.draw();

                    sort01_horiz_grey.draw();
                    sort02a_horiz_grey.draw();
                    sort02b_horiz_grey.draw();
                    sort03a_horiz_grey.draw();
                    sort03b_horiz_grey.draw();
                    sort03c_horiz_grey.draw();
                    sort03d_horiz_grey.draw();

                    sort01_horiz.draw();
                    sort02a_horiz.draw();
                    sort02b_horiz.draw();
                    sort03a_horiz.draw();
                    sort03b_horiz.draw();
                    sort03c_horiz.draw();
                    sort03d_horiz.draw();

                    test_rect_bottom1.draw();
                    test_rect_bottom2.draw();
                    test_rect_bottom3.draw();

                    end_round_block.draw();
                    begin_round_block.draw();
                    begin_round_text_part1.draw();
                    begin_round_text_part2.draw();

                    test_rect.draw();

                    message2.draw();

                    r1_text.draw();
                    r2_text.draw();
                    r3_text.draw();
                    r4_text.draw();
                    r5_text.draw();
                    r6_text.draw();
                    r7_text.draw();
                    r8_text.draw();

                    zoomBackground.draw();
                    zoomImage.draw();
                    zoomText.draw();

                    end_task_text_prompt.draw();

                    switcher_VAR = resetter_keys(switcher_VAR, vm, sCOUNTS, zCOUNTS);
                    if switcher_VAR == True :
                        sCOUNTS, index, switcher_VAR, switch_dict2 = sREDEAL_DATA(sCOUNTS, index)

                    if vm.getClicks() and dealer.contains(mouse) and INC != N_TRIALS:
                        print('vmCLICKED: , dealer')
                        dealer_tools(dealerBlock2, vm); vm.resetClicks();
                        if dealer_VAR == True:
                            pointer = pointer_update(INC, pointer, vm, dealer);
                            dealer_VAR, vm = DEALER_UPDATE(pointer);

                    if vm.getClicks() and choice_boundary.contains(mouse):
                        print('vmCLICKED: , choice_boardary')

                        selection2.pos = selection.pos;
                        vm.resetClicks();
                        if dealer_VAR == False:
                            image, bg, INC, vm, dealer_VAR = CHOICE_UPDATE(INC, dealerBlock2);

                        if redealer_VAR == True and zCOUNTS == 1:
                            redealer_VAR = False;
                            zCOUNTS = 0;
                            index = 0;
                            undealer_VAR, image, bg = zRESETTER_UPDATE(image_key, data_dict);

                        # if sCOUNTS == 0:
                        #     # del image3, image4
                        #     image3.opacity = 0;
                        #     image4.opacity = 0;
                        #     selection.setOpacity(0);
                        #     selection2.setOpacity(0);

                        if sCOUNTS == 1:
                            selection.setOpacity(1);
                            selection2.setOpacity(0);
                            sRESETTER_UPDATE(index, switch_dict2);
                            index = 0;
                            image.opacity = 0;
                            save_background();
                            bg = update_background(BG_PNG);
                            selection2.setOpacity(1);

                    if undealer_VAR == True and zCOUNTS == 1:
                        image, bg, redealer_VAR = zUNDEALER_UPDATE(image3, image4);
                        point_key, point_value, image_key = zUNDEAL_DATA(data_dict);

                    undealer_VAR = unsetter_keys(undealer_VAR, zCOUNTS, sCOUNTS, image, INC);
                    if zCOUNTS == 0 and undealer_VAR == True:
                        zCOUNTS += 1;

                    vm.draw();
                    win.flip();
                    quit(win);
                    text = point_tools(vm);
                    pointer = vm.pointer;
                    imageZoomer_VAR = imageZoomer(win, vm, resize_VAR, zoomImage, selection2, selection);

                    if type(imageZoomer_VAR) == tuple:
                        resize_VAR = imageZoomer_VAR[0];
                        zoomText.text = imageZoomer_VAR[1];

                    if ROUND_TWO_VAR == True and ROUND_TWO_COUNT < 1:

                        end_round_block.opacity = .35;
                        begin_round_block.opacity = 1;
                        begin_round_text_part1.pos = (0,75);
                        begin_round_text_part2.pos = (0,-75);

                        ROUND_TWO_COUNT = keyCounter(ROUND_TWO_COUNT)

                        if ROUND_TWO_COUNT == 1:

                            ROUND_THREE_VAR = True;

                            test_rect_bottom2.pos = [0, -450]

                            end_round_block.opacity = 0;
                            begin_round_block.opacity = 0;
                            begin_round_text_part1.pos = (4000,4000);
                            begin_round_text_part2.pos = (4000,4000);

                            sort01_vert.setOpacity(1);
                            sort02a_vert.setOpacity(1);
                            sort02b_vert.setOpacity(1);

                            r1_text.opacity = 1;
                            r2_text.opacity = 1;
                            r3_text.opacity = 1;
                            r4_text.opacity = 1;
                            r5_text.opacity = 0;
                            r6_text.opacity = 0;
                            r7_text.opacity = 0;
                            r8_text.opacity = 0;

                            r1_text_position = (-365, r1_y);
                            r2_text_position = (-120, r1_y);
                            r3_text_position = (120, r1_y);
                            r4_text_position = (365, r1_y);
                            r5_text_position = (4000, 4000);
                            r6_text_position = (4000, 4000);
                            r7_text_position = (4000, 4000);
                            r8_text_position = (4000, 4000);

                            r1_text.pos = r1_text_position;
                            r2_text.pos = r2_text_position;
                            r3_text.pos = r3_text_position;
                            r4_text.pos = r4_text_position;
                            r5_text.pos = r5_text_position;
                            r6_text.pos = r6_text_position;
                            r7_text.pos = r7_text_position;

                            end_round_text_prompt.text = 'Press "return" when you have completed round 2.';

                            end_round_text_prompt.wrapWidth=800;
                            end_round_text_prompt.alignHoriz='center';
                            end_round_text_prompt.pos = (0,-440);
                            print(ROUND_TWO_VAR)
                            print(ROUND_TWO_COUNT)

                    if ROUND_THREE_VAR == True and ROUND_THREE_COUNT < 1:
                        ROUND_THREE_COUNT = keyCounter(ROUND_THREE_COUNT);
                        if ROUND_THREE_COUNT == 1:

                            ROUND_THREE_VAR = False;
                            ROUND_FOUR_VAR = True;

                            end_round_block.opacity = .35;
                            begin_round_block.opacity = 1;
                            begin_round_text_part1.pos = (0,75);
                            begin_round_text_part1.text ="You have completed round 2";
                            begin_round_text_part2.pos = (0,-75);
                            begin_round_text_part2.text ='...press "return" to begin round 3...';
                            end_round_text_prompt.text = '';


                    if ROUND_FOUR_VAR == True and ROUND_FOUR_COUNT < 1:
                        ROUND_FOUR_COUNT = keyCounter(ROUND_FOUR_COUNT);
                        if ROUND_FOUR_COUNT == 1:


                            ROUND_FOUR_VAR = False;
                            ROUND_FIVE_VAR = True;

                            message.text = '';
                            message.wrapWidth=600;
                            message.alignHoriz='center';
                            message.alignVert='bottom';
                            test_rect.pos = [0, 435];

                            message2.pos = MESSAGE_POSITION;

                            message2.wrapWidth=600;
                            message2.alignHoriz='center';
                            message2.alignVert='bottom';

                            test_rect_bottom3.pos = [0, -450]

                            end_round_text_prompt.text = 'Press "return" when you have completed round 3.';
                            end_round_text_prompt.wrapWidth=800;
                            end_round_text_prompt.alignHoriz='center';
                            end_round_text_prompt.pos = (0,-440);

                            end_round_block.opacity = 0;
                            begin_round_block.opacity = 0;
                            begin_round_text_part1.pos = (4000,4000);
                            begin_round_text_part2.pos = (4000,4000);

                            sort01_vert.setOpacity(1);
                            sort02a_vert.setOpacity(1);
                            sort02b_vert.setOpacity(1);
                            sort03a_vert.setOpacity(1);
                            sort03b_vert.setOpacity(1);
                            sort03c_vert.setOpacity(1);
                            sort03d_vert.setOpacity(1);

                            r1_text.opacity = 1;
                            r2_text.opacity = 1;
                            r3_text.opacity = 1;
                            r4_text.opacity = 1;
                            r5_text.opacity = 1;
                            r6_text.opacity = 1;
                            r7_text.opacity = 1;
                            r8_text.opacity = 1;

                            r1_text_position = (-425, r1_y);
                            r2_text_position = (-300, r1_y);
                            r3_text_position = (-175, r1_y);
                            r4_text_position = (-60, r1_y);
                            r5_text_position = (60, r1_y);
                            r6_text_position = (175, r1_y);
                            r7_text_position = (300, r1_y);
                            r8_text_position = (425, r1_y);

                            r1_text.pos = r1_text_position;
                            r2_text.pos = r2_text_position;
                            r3_text.pos = r3_text_position;
                            r4_text.pos = r4_text_position;
                            r5_text.pos = r5_text_position;
                            r6_text.pos = r6_text_position;
                            r7_text.pos = r7_text_position;
                            r8_text.pos = r8_text_position;


                    if ROUND_FIVE_VAR == True and ROUND_FIVE_COUNT < 1:
                        ROUND_FIVE_COUNT = keyCounter(ROUND_FIVE_COUNT);

                        if ROUND_FIVE_COUNT == 1:
                            message2.pos = (4000, 4000);

                            image.opacity = 0;
                            bg.opacity = 0;
                            dealer.opacity = 0;
                            textBlock.opacity = 0;
                            small.opacity = 0;
                            large.opacity = 0;
                            image3.opacity = 0;
                            image4.opacity = 0;
                            zoomImage.opacity = 0;
                            zoomText.opacity = 0;
                            message.opacity = 1;
                            message.text = '';
                            zoomBackground.opacity = 1;
                            zoomText.opacity = 1;
                            zoomText.pos = (0, 0);

                            zoomText.height = 45;
                            zoomText.pos = (0, 100)
                            zoomText.text = 'Done!';

                            fileName = logFileDir + studyIDPrefix + subjectID + '_DISPLAYRANKED_sizeRanking';
                            savedFrame =  fileName + '.png';
                            win.getMovieFrame(buffer='front');
                            win.saveMovieFrames(savedFrame);
                            unzipper = zipfile.ZipFile(BG_FILE, 'r');
                            unzipper.extractall(BG_PATH); unzipper.close();
                            DONE = True;


                            # taskInfo['sizeRanking']=True;
                            taskInfo['sizeRanking']['taskCompleted']=True;
                            logFilePrefix = '_DATA_taskInfo.csv';
                            logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                            df = pd.DataFrame(taskInfo).T
                            df.to_csv(logFileName, index = True, header=True)

                    if DONE == True:

                        # index
                        index = range(N_TRIALS);
                        # images
                        POPPED_imKEYS = popped_images.keys()
                        POPPED_IMAGES = popped_images.values()
                        # points
                        POPPED_pointKEYS = popped_dictionary.keys()
                        POPPED_XYs = popped_dictionary.values()

                        # combine the data into one dictionary
                        dataDict = dict(zip(index,zip(

                                POPPED_imKEYS,
                                POPPED_IMAGES,
                                POPPED_pointKEYS,
                                POPPED_XYs

                                )));

                        saveData(dataDict);
                        end_task_text_prompt.pos = (0, -100);
                        ROUND_SIX_COUNT = keyCounter(ROUND_SIX_COUNT);
                        if ROUND_SIX_COUNT == 1:
                            print('...SIZE RANKING TASK COMPLETE')
                            break

            except:
                core.quit()

        ###########################
        ## TASK: distanceRanking ##
        ###########################

        if task == 'distanceRanking':

            # Setup Background Image
            BG_PATH = './stimuli/background';
            BG_FILE = './stimuli/background/background.png.zip';
            unzipper = zipfile.ZipFile(BG_FILE, 'r');
            unzipper.extractall(BG_PATH); unzipper.close();

            try:

                print('...STARTING DISTANCE RANKING TASK')

                IMAGE_RESIZE_VAR = .45
                IMAGE_DIR='./stimuli/size/';
                GRID_DATA='./stimuli/grid/task_grid.xlsx';
                TXT_PROMPT_HEIGHT = 25;
                TXT_USERLABEL_HEIGHT = 22;
                TXT_PROMPT_COLOR = 'white';
                TXT_PROMPT_UNITS = 'pix';
                TXT_PROMPT_FONTS = 'Arial';
                TXT_PROMPT_SMALL = 'SMALL';
                TXT_PROMPT_LARGE = 'LARGE';
                TXT_PROMPT_SMALL_POSITION = (-560, 0);
                TXT_PROMPT_LARGE_POSITION = (560, 0);
                SMALL_GREY_BLOCK_POS = (560, 0);
                LARGE_GREY_BLOCK_POS = (-560, 0);
                TXT_PROMPT_MESSAGE = 'input text';
                WIN_WIDTH= 1280;
                WIN_HEIGHT= 1024;
                WIN_FULL_SCREEN= True;
                WIN_MONITOR= 'testMonitor';
                WIN_UNITS = 'pix';
                WIN_COLOR = 'gray';
                MESSAGE_POSITION = (0, 385);
                DEALER_POSITION = (0, 450);
                IMAGE_RESIZE_VAR= 1;
                IMAGE_SIZE= 60;
                IMAGE_WIDTH= IMAGE_SIZE;
                IMAGE_HEIGHT= IMAGE_SIZE;
                IMAGE_UNITS= 'pix';
                VM_SHOW_LIMIT_BOX = False;
                VM_CLICK_ON_UP = True;
                VM_WIDTH = 1920;
                VM_HEIGHT = 1080;
                GRID_WIDTH = 1280;
                GRID_HEIGHT = 1024;
                GRID_ROWS = 8;
                GRID_COLUMNS  = 8;
                GRID_RESIZE_WPX_VAR = .65;
                GRID_RESIZE_HPX_VAR = .63;
                GRID_VERT_SHIFT_VAR = (-15);
                CHOICE_BOUNDARY_WIDTH = 480*2;
                CHOICE_BOUNDARY_HEIGHT = 365*2;
                CHOICE_BOUNDARY_POSITION_SHIFT = (0, -15);
                DBLOCK01_WIDTH = 50;
                DBLOCK01_HEIGHT = 50;
                DBLOCK01_FILL_COLOR = 'black';
                DBLOCK01_LINE_COLOR = 'black';
                DBLOCK01_UNITS = 'pix';
                DBLOCK02_FILL_COLOR = 'white';
                DBLOCK02_LINE_COLOR = 'white';
                DBLOCK02_UNITS = 'pix';
                TBLOCK_WIDTH = 1200;
                TBLOCK_HEIGHT = 50;
                TBLOCK_FILL_COLOR = 'gray';
                TBLOCK_LINE_COLOR = 'gray';
                TBLOCK_UNITS = 'pix';
                TBLOCK_POSITION = (0, 385);
                RESIZED_IMAGE_POSITION = (0, 0);
                RESIZED_IMAGE_SIZE = (300, 300);

                def makeCoords(n_rows, n_cols, win_wpx, win_hpx, grid_vert_shift):
                    GridRows = np.linspace(-win_hpx/2, +win_hpx/2, n_rows)
                    GridCols = np.linspace(-win_wpx/2, +win_wpx/2, n_cols)
                    xGridCoords, yGridCoords = np.meshgrid(GridCols, GridRows)
                    yGridCoords += grid_vert_shift
                    return(xGridCoords, yGridCoords)

                def stackCoords(x, y):
                    x_list = [];
                    for i in x:
                        row = i;
                        for j in row:
                            # print(j)
                            x_list.append(j)
                    y_list = [];
                    for i in y:
                        col = i;
                        for j in col:
                            # print(j)
                            y_list.append(j)
                    task_grid = np.column_stack((x_list, y_list))
                    return task_grid

                def saveGrid():
                    n_rows = GRID_ROWS;
                    n_cols = GRID_COLUMNS;
                    win_wpx = (GRID_WIDTH*GRID_RESIZE_WPX_VAR);
                    win_hpx = (GRID_HEIGHT*GRID_RESIZE_HPX_VAR);
                    filepath ='./stimuli/grid/task_grid.xlsx';
                    x, y = makeCoords(n_rows, n_cols, win_wpx, win_hpx, GRID_VERT_SHIFT_VAR);
                    task_grid = stackCoords(x, y);
                    ## convert your array into a dataframe
                    df = pd.DataFrame(task_grid)
                    ## save to xlsx file
                    df.to_excel(filepath, index=False)

                saveGrid()

                dealer_VAR = True; undealer_VAR = False; redealer_VAR = False;
                TASK_DONE = False;
                switcher_VAR = False;
                sCOUNTS = 0;
                switch_done = False;
                index = 0;
                grey_im = []; grey_xy = []; grey_point = [];
                zCOUNTS = 0; INC = 0;
                BG_PNG_ZIP = './stimuli/background/background.png.zip';
                BG_PNG = './stimuli/background/background.png';
                BG_DIR = '/stimuli/background/background.png.zip';
                GRID_DATA ='./stimuli/grid/task_grid.xlsx';

                def grid_data():
                    import numpy as np
                    import pandas as pd
                    grid_points = pd.read_excel(GRID_DATA)
                    grid_points = np.array(grid_points)
                    point_keys = []; point_values = [];
                    for i in range(len(grid_points)):
                        point_key = "p" + str(i)
                        point_x, point_y = grid_points[i][0], grid_points[i][1]
                        point_value = (point_x, point_y)
                        point_keys.append(point_key)
                        point_values.append(point_value)
                        point_dictionary = dict(zip(point_keys, point_values))
                    return point_dictionary

                point_dictionary = grid_data();

                dealer = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/dealer.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = DEALER_POSITION);

                bg = visual.ImageStim(win,
                            image=BG_PNG)

                pointer = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image2 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        pos = (2000, 2000),
                        units = 'pix');

                image3 = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                image4 = visual.ImageStim(
                        win,
                        image=  './stimuli/dealers/image.png',
                        size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                        units = IMAGE_UNITS,
                        pos = (2000, 2000));

                choice_boundary = visual.Rect(
                        win,
                        width=CHOICE_BOUNDARY_WIDTH,
                        height=CHOICE_BOUNDARY_HEIGHT,
                        units = 'pix');
                choice_boundary.pos += CHOICE_BOUNDARY_POSITION_SHIFT;

                def unzip(BG_PNG_ZIP):
                    CURRENT_DIR = os.getcwd()
                    zip_ref = zipfile.ZipFile(BG_PNG_ZIP, 'r')
                    zip_ref.extractall(CURRENT_DIR)
                    zip_ref.close()

                small = visual.TextStim(win,
                    height = TXT_PROMPT_HEIGHT,
                    pos=TXT_PROMPT_SMALL_POSITION,
                    text=TXT_PROMPT_SMALL,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    units=TXT_PROMPT_UNITS)

                large = visual.TextStim(win,
                    height = TXT_PROMPT_HEIGHT,
                    pos=TXT_PROMPT_LARGE_POSITION,
                    text=TXT_PROMPT_LARGE,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    units=TXT_PROMPT_UNITS)

                message = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    text=TXT_PROMPT_MESSAGE,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                dealerBlock1 = visual.Rect(win,
                        width=DBLOCK01_WIDTH,
                        height=DBLOCK01_HEIGHT,
                        fillColor = DBLOCK01_FILL_COLOR,
                        lineColor = DBLOCK01_LINE_COLOR,
                        units=DBLOCK01_UNITS);

                dealerBlock2 = visual.Rect(win,
                        width =IMAGE_WIDTH,
                        height =IMAGE_HEIGHT,
                        fillColor = DBLOCK02_FILL_COLOR,
                        lineColor = DBLOCK02_LINE_COLOR,
                        units = DBLOCK02_UNITS);

                textBlock = visual.Rect(win,
                        width=TBLOCK_WIDTH,
                        height=TBLOCK_HEIGHT,
                        fillColor = TBLOCK_FILL_COLOR,
                        lineColor = TBLOCK_LINE_COLOR,
                        units=TBLOCK_UNITS);

                dealerBlock2.autoDraw = True;

                dealerBlock1.pos = DEALER_POSITION;
                dealerBlock2.pos = DEALER_POSITION;
                textBlock.pos = TBLOCK_POSITION;

                dealerBlock1.setOpacity(1);
                dealerBlock2.setOpacity(0);

                def resizedImage(image):
                    resized_image = visual.ImageStim(
                            win,
                            image=image,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = RESIZED_IMAGE_POSITION);
                    resized_image.size = RESIZED_IMAGE_SIZE;
                    return resized_image

                zoomBackground = visual.Rect(
                        win,
                        fillColor = 'grey',
                        lineColor = None,
                        width=2000,
                        height=2000,
                        units = 'pix');

                zoomImage = visual.ImageStim(
                        win,
                        image= './stimuli/dealers/undealer.png',
                        size=(600, 600),
                        units = IMAGE_UNITS,
                        pos = (15, 50));

                zoomText = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    text='',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                zoomBackground.setOpacity(0);
                zoomImage.setOpacity(0);
                zoomText.setOpacity(0);

                selection = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 1.0,
                        units = 'pix');

                selection.setOpacity(0);

                selection2 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'gray',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 3,
                        units = 'pix');

                selection2.setOpacity(0);
                selection.autoDraw = True;
                selection2.autoDraw = True;

                selection3 = visual.Rect(
                        win,
                        fillColor = None,
                        lineColor = 'yellow',
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        lineWidth = 1.0,
                        units = 'pix');

                selection3.setOpacity(0);
                selection3.autoDraw = True;

                # import numpy as np
                # vert_lines = np.linspace(-480, 480, num=9);
                # for i in vert_lines:
                #     print(i)
                # -480.0
                # -360.0
                # -240.0
                # -120.0
                # 0.0
                # 120.0
                # 240.0
                # 360.0
                # 480.0

                sort01_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02a_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02b_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03a_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03b_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03c_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03d_vert = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')

                sort01_vert.start = [0, -380];
                sort01_vert.end = [0, +350];
                sort02a_vert.start = [-240, -380];
                sort02a_vert.end = [-240, +350];
                sort02b_vert.start = [240, -380];
                sort02b_vert.end = [240, +350];
                sort03a_vert.start = [-120, -380];
                sort03a_vert.end = [-120, +350];
                sort03b_vert.start = [120, -380];
                sort03b_vert.end = [120, +350];
                sort03c_vert.start = [-365, -380];
                sort03c_vert.end = [-365, +350];
                sort03d_vert.start = [365, -380];
                sort03d_vert.end = [365, +350];

                SORT_VERT_LINE_WIDTH = .9;

                sort01_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort02a_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort02b_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03a_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03b_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03c_vert.lineWidth = (SORT_VERT_LINE_WIDTH);
                sort03d_vert.lineWidth = (SORT_VERT_LINE_WIDTH);

                sort01_vert.setOpacity(1);
                sort02a_vert.setOpacity(0);
                sort02b_vert.setOpacity(0);
                sort03a_vert.setOpacity(0);
                sort03b_vert.setOpacity(0);
                sort03c_vert.setOpacity(0);
                sort03d_vert.setOpacity(0);

                sort01_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02a_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02b_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03a_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03b_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03c_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03d_vert_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')

                sort01_vert_grey.start = [0, -380];
                sort01_vert_grey.end = [0, +350];
                sort02a_vert_grey.start = [-240, -380];
                sort02a_vert_grey.end = [-240, +350];
                sort02b_vert_grey.start = [240, -380];
                sort02b_vert_grey.end = [240, +350];
                sort03a_vert_grey.start = [-120, -380];
                sort03a_vert_grey.end = [-120, +350];
                sort03b_vert_grey.start = [120, -380];
                sort03b_vert_grey.end = [120, +350];
                sort03c_vert_grey.start = [-365, -380];
                sort03c_vert_grey.end = [-365, +350];
                sort03d_vert_grey.start = [365, -380];
                sort03d_vert_grey.end = [365, +350];

                SORT_VERT_GREY_LINE_WIDTH = 1.1;

                sort01_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort02a_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort02b_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03a_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03b_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03c_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);
                sort03d_vert_grey.lineWidth = (SORT_VERT_GREY_LINE_WIDTH);

                sort01_vert_grey.setOpacity(0);
                sort02a_vert_grey.setOpacity(0);
                sort02b_vert_grey.setOpacity(0);
                sort03a_vert_grey.setOpacity(0);
                sort03b_vert_grey.setOpacity(0);
                sort03c_vert_grey.setOpacity(0);
                sort03d_vert_grey.setOpacity(0);

                # import numpy as np
                # horiz_lines = np.linspace(350, -380, num=9);
                # for i in horiz_lines:
                #     print(i)

                # 350.0
                # 258.75
                # 167.5
                # 76.25
                # -15.0
                # -106.25
                # -197.5
                # -288.75
                # -380.0

                sort01_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02a_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort02b_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03a_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03b_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03c_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')
                sort03d_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='white')

                sort01_horiz.start = [-480, 258.75];
                sort01_horiz.end = [480, 258.75];
                sort02a_horiz.start = [-480, 167.5];
                sort02a_horiz.end = [480, 167.5];
                sort02b_horiz.start = [-480, 76.25];
                sort02b_horiz.end = [480, 76.25];
                sort03a_horiz.start = [-480, -15.0];
                sort03a_horiz.end = [480, -15.0];
                sort03b_horiz.start = [-480, -106.25];
                sort03b_horiz.end = [480, -106.25];
                sort03c_horiz.start = [-480, -197.5];
                sort03c_horiz.end = [480, -197.5];
                sort03d_horiz.start = [-480, -288.75];
                sort03d_horiz.end = [480, -288.75];

                SORT_HORIZ_LINE_WIDTH = .9;

                sort01_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort02a_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort02b_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03a_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03b_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03c_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);
                sort03d_horiz.lineWidth = (SORT_HORIZ_LINE_WIDTH);

                # sort01_horiz.setOpacity(1);
                # sort02a_horiz.setOpacity(1);
                # sort02b_horiz.setOpacity(1);
                # sort03a_horiz.setOpacity(1);
                # sort03b_horiz.setOpacity(1);
                # sort03c_horiz.setOpacity(1);
                # sort03d_horiz.setOpacity(1);

                sort01_horiz.setOpacity(0);
                sort02a_horiz.setOpacity(0);
                sort02b_horiz.setOpacity(0);
                sort03a_horiz.setOpacity(0);
                sort03b_horiz.setOpacity(0);
                sort03c_horiz.setOpacity(0);
                sort03d_horiz.setOpacity(0);

                sort01_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02a_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort02b_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03a_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03b_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03c_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')
                sort03d_horiz_grey = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='grey')

                sort01_horiz_grey.start = [-480, 258.75];
                sort01_horiz_grey.end = [480, 258.75];
                sort02a_horiz_grey.start = [-480, 167.5];
                sort02a_horiz_grey.end = [480, 167.5];
                sort02b_horiz_grey.start = [-480, 76.25];
                sort02b_horiz_grey.end = [480, 76.25];
                sort03a_horiz_grey.start = [-480, -15.0];
                sort03a_horiz_grey.end = [480, -15.0];
                sort03b_horiz_grey.start = [-480, -106.25];
                sort03b_horiz_grey.end = [480, -106.25];
                sort03c_horiz_grey.start = [-480, -197.5];
                sort03c_horiz_grey.end = [480, -197.5];
                sort03d_horiz_grey.start = [-480, -288.75];
                sort03d_horiz_grey.end = [480, -288.75];

                sort01_horiz_grey.setOpacity(0);
                sort02a_horiz_grey.setOpacity(0);
                sort02b_horiz_grey.setOpacity(0);
                sort03a_horiz_grey.setOpacity(0);
                sort03b_horiz_grey.setOpacity(0);
                sort03c_horiz_grey.setOpacity(0);
                sort03d_horiz_grey.setOpacity(0);

                SORT_HORIZ_GREY_LINE_WIDTH = 1.1;

                sort01_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort02a_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort02b_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03a_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03b_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03c_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);
                sort03d_horiz_grey.lineWidth = (SORT_HORIZ_GREY_LINE_WIDTH);

                test_rect = visual.Rect(win,
                        width=800,
                        height=150,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect.pos = [4000, 4000];

                test_rect2 = visual.Rect(win,
                        width=1240,
                        height=155,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect2.pos = [4000, 4000];

                test_rect_bottom1 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom1.pos = [0, -450]

                test_rect_bottom2 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom2.pos = [4000, 4000];

                test_rect_bottom3 = visual.Rect(win,
                        width=800,
                        height=120,
                        fillColor = 'grey',
                        lineColor = 'grey',
                        units='pix');
                test_rect_bottom3.pos = [4000, 4000];

                end_round_block = visual.Rect(
                        win,
                        fillColor = 'white',
                        lineColor = 'white',
                        width=2000,
                        height=2000,
                        lineWidth = 1,
                        pos = (0, 0),
                        units = 'pix');
                end_round_block.setOpacity(0);

                begin_round_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'white',
                        width=500,
                        height=500,
                        lineWidth = 1,
                        pos = (0, 0),
                        units = 'pix');
                begin_round_block.setOpacity(0);

                begin_round_text_part1 = visual.TextStim(win,
                    height = 30,
                    pos=(0,100),
                    text="You have completed round 1",
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                begin_round_text_part2 = visual.TextStim(win,
                    height = 30,
                    pos=(0,-100),
                    text='...press "return" to begin round 2...',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)

                begin_round_text_part1.pos = (4000,4000);
                begin_round_text_part2.pos = (4000,4000);

                small_gray_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'gray',
                        width=100,
                        height=100,
                        lineWidth = 1,
                        units = 'pix');

                large_gray_block = visual.Rect(
                        win,
                        fillColor = 'gray',
                        lineColor = 'gray',
                        width=100,
                        height=100,
                        lineWidth = 1,
                        units = 'pix');

                small_gray_block.pos = SMALL_GREY_BLOCK_POS;
                large_gray_block.pos = LARGE_GREY_BLOCK_POS;

                small_size_ranking_line_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='yellow')
                small_size_ranking_line_horiz.start = [-480, -465];
                small_size_ranking_line_horiz.end = [-250, -465];

                large_size_ranking_line_horiz = visual.Line(
                    win=win,
                    units='pix',
                    lineColor='yellow')
                large_size_ranking_line_horiz.start = [480, -465];
                large_size_ranking_line_horiz.end = [250, -465];

                ROUND_TWO_TEXT = u"Sort the objects into 4 groups of roughly equi-distant objects. From left to right, object groups should reflect increases in viewing distance. After you're finished, press 'return'. "

                ROUND_THREE_TEXT = u"Sort the objects into 8 groups of roughly equi-distant objects. From left to right, object groups should reflect increases in viewing distance. After you're finished, press 'return'. "

                message2 = visual.TextStim(win,
                    height = TXT_USERLABEL_HEIGHT,
                    pos=MESSAGE_POSITION,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                message2.text = ROUND_THREE_TEXT;
                message2.pos = (4000, 4000);

                end_round_text_prompt = visual.TextStim(win,
                    height = 30,
                    text='',
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                end_round_text_prompt.pos = (4000, 4000);

                end_task_text_prompt = visual.TextStim(win,
                    height = 30,
                    font=TXT_PROMPT_FONTS,
                    color=TXT_PROMPT_COLOR,
                    alignVert='center',
                    alignHoriz='center',
                    units=TXT_PROMPT_UNITS)
                end_task_text_prompt.pos = (4000, 4000);
                END_TASK_PROMPT_TEXT = '...press "return" to quit...';
                end_task_text_prompt.text = END_TASK_PROMPT_TEXT;

                r1_y = -430;
                rtext_size = (50, 50);
                rtext_color = 'white';
                rtext_units = 'pix';

                r1_text = visual.TextStim(win, '1', color=rtext_color, units=rtext_units);
                r2_text = visual.TextStim(win, '2', color=rtext_color, units=rtext_units);
                r3_text = visual.TextStim(win, '3', color=rtext_color, units=rtext_units);
                r4_text = visual.TextStim(win, '4', color=rtext_color, units=rtext_units);
                r5_text = visual.TextStim(win, '5', color=rtext_color, units=rtext_units);
                r6_text = visual.TextStim(win, '6', color=rtext_color, units=rtext_units);
                r7_text = visual.TextStim(win, '7', color=rtext_color, units=rtext_units);
                r8_text = visual.TextStim(win, '8', color=rtext_color, units=rtext_units);

                class dictObj(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value1, value2):
                        self[key] = value1, value2
                switch_dict = dictObj();
                resize_COUNT = 0;
                def quit(win):
                    QUIT_KEYS = event.getKeys('0')
                    if len(QUIT_KEYS) > 0:

                        # imageName = image_value.replace('./stimuli/size/', '');
                        # imageName = imageName.replace('.jpg.png-gaussian.png', '');
                        # fileName = logFileDir + studyIDPrefix + subjectID + '_IMAGE_{}_sizeRanking'.format(imageName);
                        # savedFrame =  fileName + '.png';
                        # win.getMovieFrame(buffer='front');
                        # win.saveMovieFrames(savedFrame);

                        core.quit();
                        win.close()

                resize_VAR = False;
                point_dictionary_backup = grid_data();
                ROUND_TWO_VAR = False;
                ROUND_THREE_VAR = False;
                ZOOM_TEXT = '???';

                def getUserLabels():
                    logFilePrefix = '_DATA_objectNaming.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                    nameLib = pd.read_csv(logFileName);
                    nameLib = nameLib.T

                    nameLib = nameLib.drop(nameLib.index[0])
                    # nameLib.drop(nameLib.index[1])
                    cols = ['image', 'userLabel']
                    nameLib.columns = cols;
                    # nameLib.columns
                    fileNames = (nameLib['image'].values).tolist();
                    userLabels = (nameLib['userLabel'].values).tolist();
                    return fileNames, userLabels

                fileNames, userLabels = getUserLabels()

                def point_tools(vm):

                    sort01_KEYS = event.getKeys('t')
                    if len(sort01_KEYS) > 0:

                        print('image3.pos: ', image3.pos)
                        print('image3.image: ', image3.image)
                        print('image4.pos: ', image4.pos)
                        print('image4.image: ', image4.image)
                        print('image.pos: ', image.pos)
                        print('image.image: ', image.image)

                    sort02_KEYS = event.getKeys('y')
                    if len(sort02_KEYS) > 0:
                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);

                    sort03_KEYS = event.getKeys('u')
                    if len(sort03_KEYS) > 0:

                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);
                        sort03a_vert.setOpacity(1);
                        sort03b_vert.setOpacity(1);
                        sort03c_vert.setOpacity(1);
                        sort03d_vert.setOpacity(1);


                    sort01_horiz_KEYS = event.getKeys('t')
                    if len(sort01_horiz_KEYS) > 0:
                        sort01_vert.setOpacity(1);

                    sort02_horiz_KEYS = event.getKeys('y')
                    if len(sort02_KEYS) > 0:
                        sort01_vert.setOpacity(1);
                        sort02a_vert.setOpacity(1);
                        sort02b_vert.setOpacity(1);

                    sort03_horiz_KEYS = event.getKeys('u')
                    if len(sort03_horiz_KEYS) > 0:

                        sort01_horiz_vert.setOpacity(1);
                        sort02a_horiz_vert.setOpacity(1);
                        sort02b_horiz_vert.setOpacity(1);
                        sort03a_horiz_vert.setOpacity(1);
                        sort03b_horiz_vert.setOpacity(1);
                        sort03c_horiz_vert.setOpacity(1);
                        sort03d_horiz_vert.setOpacity(1);


                    N_POPPED_IMAGES = event.getKeys('1')
                    if len(N_POPPED_IMAGES) > 0:
                        print('N_POPPED_IMAGES: ', len(popped_images));

                    LIST_POPPED_IMAGES = event.getKeys('9')
                    if len(LIST_POPPED_IMAGES) > 0:
                        itemlist1=[];
                        itemlist2=[];
                        for i in popped_images:
                            print('LIST_POPPED_IMAGES: ', popped_images[i]);
                            itemlist.append(i, popped_images[i])

                        with open('LIST_POPPED_IMAGES', 'wb') as fp:
                            pickle.dump(itemlist, fp)


                    LIST_POPPED_IMAGES = event.getKeys('2')
                    if len(LIST_POPPED_IMAGES) > 0:

                        itemlist1=[];
                        itemlist2=[];
                        itemlist3=[];
                        itemlist4=[];

                        for i in popped_images:
                            print('LIST_POPPED_IMAGES: ', popped_images[i]);
                            itemlist1.append(i)
                            itemlist2.append(popped_images[i])

                        with open('LIST_POPPED_imKEYS', 'wb') as fp:
                            pickle.dump(itemlist1, fp)

                        with open('LIST_POPPED_IMAGES', 'wb') as fp:
                            pickle.dump(itemlist2, fp)

                        for i in popped_dictionary:
                            print('LIST_POPPED_POINTS: ', i);
                            print('LIST_POPPED_XYs: ', popped_dictionary[i]);
                            itemlist3.append(i)
                            itemlist4.append(popped_dictionary[i])

                        with open('LIST_POPPED_pKEYS', 'wb') as fp:
                            pickle.dump(itemlist3, fp)

                        with open('LIST_POPPED_XYs', 'wb') as fp:
                            pickle.dump(itemlist4, fp)

                    N_AVAILABLE_POINTS = event.getKeys('3')
                    if len(N_AVAILABLE_POINTS) > 0:
                        print('N_AVAILABLE_POINTS: ', len(point_dictionary));

                    CLOSEST_POINT = event.getKeys('4')
                    if len(CLOSEST_POINT) > 0:
                        closest_point = new_position(vm, point_dictionary_backup)
                        print('CLOSEST POINT: ', closest_point);

                    N_POPPED_POINTS = event.getKeys('5')
                    if len(N_POPPED_POINTS) > 0:
                        print('N_POPPED_POINTS: ', len(popped_dictionary));

                    LIST_POPPED_POINTS = event.getKeys('6')
                    if len(LIST_POPPED_POINTS) > 0:
                        itemlist=[];
                        for i in popped_dictionary:
                            print('LIST_POPPED_POINTS: ', i);
                            print('LIST_POPPED_(XY): ', popped_dictionary[i]);
                            itemlist.append(i, popped_dictionary[i])
                        # with open('LIST_POPPED_POINTS', 'wb') as fp:
                        #     pickle.dump(itemlist, fp)

                    N_POPPED_IMAGES = event.getKeys('7')
                    if len(N_POPPED_IMAGES) > 0:
                        print('N_POPPED_IMAGES: ', len(popped_images));

                def zoom(win, vm, zoomImage, selection2, selection):
                    zoomText.pos = (0, -365)
                    zoomText.height = 35;
                    message.setOpacity(0);

                    selection.setOpacity(0)
                    selection2.setOpacity(0)

                    point_key = new_position(vm, point_dictionary_backup)
                    imDict = set_images[point_key];

                    if imDict['image'] != None:
                        imageName = imDict['image'];
                        ZOOM_IMAGE = imageName;
                        zoomImage.image = ZOOM_IMAGE;
                        if imageName in fileNames:
                            index = fileNames.index(imageName)
                            userLabel = userLabels[index];
                            ZOOM_TEXT = userLabel;
                            message.setOpacity(0)
                            zoomBackground.setOpacity(1);
                            zoomImage.setOpacity(1);
                            zoomText.setOpacity(1);
                            win.mouseVisible = False;

                            return ZOOM_TEXT

                        elif imageName not in fileNames:

                            message.setOpacity(0)
                            zoomBackground.setOpacity(1);
                            zoomImage.setOpacity(1);
                            zoomText.setOpacity(1);

                            ZOOM_IMAGE = imageName;

                            print("elif imageName not in fileNames: ", ZOOM_IMAGE)
                            zoomImage.image = ZOOM_IMAGE;

                            userLabel = '???';
                            ZOOM_TEXT = userLabel;
                            win.mouseVisible = False;
                            return ZOOM_TEXT

                def shrink(win, vm, zoomImage, selection2, selection):

                    selection.setOpacity(0)
                    selection2.setOpacity(0);

                    zoomBackground.setOpacity(0);
                    zoomImage.setOpacity(0);
                    zoomImage.opacity = 0;
                    message.setOpacity(1)
                    win.mouseVisible = True;

                    message.opacity = 1;
                    zoomText.setOpacity(1);
                    zoomText.pos = (2000, 2000);

                    point_key = new_position(vm, point_dictionary_backup)
                    print(point_key)
                    imDict = set_images[point_key];

                    if imDict['image'] != None:
                        imageName = imDict['image'];
                        if imageName in fileNames:
                            ZOOM_IMAGE = imageName;
                            zoomImage.image = ZOOM_IMAGE;
                            index = fileNames.index(imageName)
                            userLabel = userLabels[index];
                            ZOOM_TEXT = userLabel;

                def imageZoomer(win, vm, resize_VAR, zoomImage, selection2, selection):

                    ZOOM_KEYS = event.getKeys('s');

                    if len(ZOOM_KEYS) > 0:

                        if resize_VAR == False:
                            ZOOM_TEXT = zoom(win, vm, zoomImage, selection2, selection);
                            resize_VAR = True;
                            return resize_VAR, ZOOM_TEXT

                        if resize_VAR == True:
                            ZOOM_TEXT = shrink(win, vm, zoomImage, selection2, selection);
                            resize_VAR = False;
                            return resize_VAR, ZOOM_TEXT

                            logFilePrefix = '_DATA_distanceRanking.csv';
                            logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                            point_dictionary_backup = grid_data();
                            nuu = None;
                            text = None;

                            SELF_DIR = os.path.dirname(__file__);
                            TASK_DIR = os.path.abspath(SELF_DIR);
                            TASK_DIR = SELF_DIR + TASK_DIR;

                fileNames, userLabels = getUserLabels()

                blank1 = [];
                blank2 = [];
                blank3 = [];

                sCOUNTS = 0;
                index = 0;
                switch_dict = dictObj();
                switch_dict2 = dictObj();

                class dictObj2(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value):
                        self[key] = value

                class dictObj3(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value1, value2, value3):
                        self[key] = value1, value2, value3

                def dealer_image(INC, obj):
                    if INC < N_TRIALS:
                        image_key = 'im'+ str(INC);
                        image_value = image_dict[image_key];
                        try:
                            imageName = image_value;
                            index = fileNames.index(imageName);
                            userLabel = userLabels[index];
                            obj.text = userLabel;
                        except (IndexError, ValueError):
                            userLabel = '???';
                            obj.text = userLabel;

                    if INC >= N_TRIALS:
                        image_value = './stimuli/dealers/image.png';
                    image = visual.ImageStim(win,
                                    image=image_value,
                                    pos  = DEALER_POSITION,
                                    size = (IMAGE_WIDTH,
                                            IMAGE_HEIGHT));

                    return image

                def update_image(INC):
                    image_key = 'im'+ str(INC);
                    image_value = image_dict[image_key];
                    popped_images.update({image_key: image_value})
                    image = visual.ImageStim(win,
                                    image=image_value,
                                    size = (IMAGE_WIDTH,
                                            IMAGE_HEIGHT));

                    return image

                def CHOICE_UPDATE(INC, dealerBlock2):
                    image = update_image(INC); dealerBlock2.opacity = 0.0;
                    point_key = new_position(vm, point_dictionary);
                    point_value = point_dictionary.pop(point_key);
                    popped_dictionary.update({point_key:point_value});
                    image.pos = point_value;
                    element = set_images[point_key];
                    element['(x, y)'] = point_value;
                    element['image'] = images_key[INC]
                    set_image_key = point_key.replace('p', 'im');
                    element['set_image_key'] = set_image_key;
                    switch_dict.add(point_key, point_value, image.image)
                    set_images.update(element); INC += 1;
                    save_background(); bg = update_background(BG_PNG);
                    pointer.setOpacity(0); dealer_VAR = True;
                    vm.pointer = pointer; vm.visible = True;
                    return image, bg, INC, vm, dealer_VAR

                def pointer_update(INC, pointer, vm, dealer):
                    del pointer, vm
                    pointer = update_image(INC)
                    return pointer

                def reset_vm(vm):
                    vm.visible = True;
                    return vm

                def dealer_tools(dealerBlock2, vm):
                    dealerBlock2.opacity = .60;
                    vm.visible = True;

                def get_setImages():
                    return set_images

                def unsetter_image(point_key, point_value):
                    image_key = set_images[point_key]['image'];
                    image = image_key;
                    grey_im.append(image);
                    return image

                def unsetter_pointer(image_key):
                    pointer = visual.ImageStim(win,
                                    image=image_key,
                                    size = (IMAGE_WIDTH, IMAGE_HEIGHT));
                    return pointer

                def unsetter_keys(undealer_VAR, zCOUNTS, sCOUNTS, image, INC):
                    popped_size = len(popped_dictionary);
                    UNSETTER_KEYS = event.getKeys('d')

                    if len(UNSETTER_KEYS) > 0 and popped_size > 0 and zCOUNTS == 0 and sCOUNTS == 0:
                        point_key = new_position(vm, popped_dictionary);
                        point_value = popped_dictionary.pop(point_key);
                        del switch_dict[point_key]
                        image_key = unsetter_image(point_key, point_value);
                        vm.pointer = unsetter_pointer(image_key);
                        vm.visible = True; undealer_VAR = True;
                        grey_point.append(point_key); grey_xy.append(point_value);
                        return undealer_VAR
                    else:
                        pass

                def resetter_keys(switcher_VAR, vm, sCOUNTS, zCOUNTS):
                    popped_size = len(popped_dictionary);
                    SWITCHER_KEYS = event.getKeys('f')

                    if len(SWITCHER_KEYS) > 0 and popped_size > 0 and sCOUNTS == 0 and zCOUNTS == 0 and switcher_VAR != True:
                        tmp_dict = dictObj2();
                        for i in switch_dict:
                            tmp_dict.add(i, switch_dict[i][0])
                        switcher_VAR = True;
                        point_key = new_position(vm, tmp_dict);
                        point_value = switch_dict[point_key][0];

                        imDict = set_images[point_key];

                        selection.setOpacity(1);
                        selection2.setOpacity(0);
                        selection.pos = point_value;
                        selection2.pos = point_value;
                        image_name = switch_dict[point_key][1];

                        blank1.append(point_key)
                        blank2.append(point_value)
                        blank3.append(image_name)
                        globals()['sCOUNTS']=1;

                        return switcher_VAR
                    else:
                        pass

                def buffer_stimuli(stimlist):
                    rect = (-1, 1, 1, -1);
                    stimulus_display = visual.BufferImageStim(win,
                                            stim=stimlist,
                                            rect=rect);
                    return stimulus_display

                def DEALER_UPDATE(pointer):
                    vm.pointer = pointer; dealer_VAR = False;
                    return dealer_VAR, vm

                def pop_task_variables():
                    point_key = grey_point.pop();
                    point_value = grey_xy.pop();
                    image_key = grey_im.pop();
                    return point_key, point_value, image_key

                def zUNDEALER_UPDATE(image3, image4):
                    image3.opacity = 0; image4.opacity = 0; redealer_VAR = True;
                    image = visual.ImageStim(win,
                        image='./stimuli/dealers/image.png',
                        size = (IMAGE_WIDTH,IMAGE_WIDTH),
                        pos = grey_xy);
                    save_background();bg = update_background(BG_PNG)
                    return image, bg, redealer_VAR

                def zUNDEAL_DATA(data_dict):
                    point_key, point_value, image_key = pop_task_variables();
                    point_dictionary[point_key] = point_value;
                    data_dict[image_key] = point_key;
                    return point_key, point_value, image_key

                def zRESETTER_UPDATE(image_key, data_dict):
                    point_key = new_position(vm, point_dictionary);
                    point_value = point_dictionary.pop(point_key);
                    popped_dictionary.update({point_key:point_value});
                    image = visual.ImageStim(win,
                        image=image_key,
                        size = (IMAGE_WIDTH,IMAGE_WIDTH),
                        pos = point_value);
                    element = set_images[point_key];
                    element['(x, y)'] = point_value;
                    element['image'] = image_key;
                    set_image_key = point_key.replace('p', 'im');
                    element['set_image_key'] = set_image_key;
                    set_images.update(element); undealer_VAR = False;
                    switch_dict.add(point_key, point_value, image_key);
                    save_background(); bg = update_background(BG_PNG);
                    return undealer_VAR, image, bg

                def sREDEAL_DATA(sCOUNTS, index):
                    index += 1;
                    # FIXED
                    # image3.opacity = 0; image4.opacity = 0;
                    switch_dict2 = dictObj3();
                    switch_dict2.add(index, blank1[0], blank2[0], blank3[0]);
                    blank1.pop(); blank2.pop(); blank3.pop();
                    switcher_VAR = False;
                    return sCOUNTS, index, switcher_VAR, switch_dict2

                def sRESETTER_UPDATE(index, switch_dict2):
                    tmp_dict = dictObj2();
                    for i in switch_dict:
                        tmp_dict.add(i, switch_dict[i][0])
                    switcher_VAR = True;
                    point_key = new_position(vm, tmp_dict);
                    point_value = switch_dict[point_key][0];
                    image_name = switch_dict[point_key][1];
                    index += 1;

                    switch_dict2.add(index, point_key, point_value, image_name);
                    set_images[switch_dict2[1][0]]['(x, y)']= switch_dict2[2][1];
                    set_images[switch_dict2[1][0]]['image']= switch_dict2[2][2];
                    set_images[switch_dict2[2][0]]['(x, y)']= switch_dict2[1][1];
                    set_images[switch_dict2[2][0]]['image']= switch_dict2[1][2];
                    tmp3 = switch_dict2[2][2];
                    tmp4 = switch_dict2[1][2];


                    globals()['image3'] = visual.ImageStim(
                            win,
                            image=tmp4,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = switch_dict2[2][1]);

                    globals()['image4'] = visual.ImageStim(
                            win,
                            image=tmp3,
                            size=(IMAGE_WIDTH, IMAGE_HEIGHT),
                            units = IMAGE_UNITS,
                            pos = switch_dict2[1][1]);

                    point_key1 = switch_dict2[1][0]
                    point_key2 = switch_dict2[2][0]
                    if point_key1 != point_key2:
                        tmp_point_key1 = switch_dict.pop(point_key1)
                        tmp_point_key2 = switch_dict.pop(point_key2)
                        switch_dict.add(point_key1, tmp_point_key1[0], tmp_point_key2[1])
                        switch_dict.add(point_key2, tmp_point_key2[0], tmp_point_key1[1])
                    # HERE HERE HERE
                    globals()['sCOUNTS']=0;
                    del switch_dict2

                popped_dictionary = {};
                set_images = {};
                for i in range(100):
                    popped_point_key = 'p' + str(i);
                    set_image_key = 'im' + str(i);
                    popped_point_value = None
                    set_image_value = None
                    element = {popped_point_key: {
                                        '(x, y)': popped_point_value,
                                        'image': set_image_value,
                                        'set_image_key': set_image_key}}
                    set_images.update(element)
                images_key = getTaskObjects('size')
                random.shuffle(images_key);
                image_dict={};
                for i in range(60):
                    try:
                        image_dict.update({'im'+str(i):images_key[i]})
                    except IndexError:
                        image_dict.update({'im'+str(i):None})
                    # continue
                popped_images = {};

                def mouse_pos(vm):
                    mouse_x, mouse_y = vm.getPos()[0], vm.getPos()[1]
                    return mouse_x, mouse_y

                def calc_distances(vm, dictionary):
                    mouse_x, mouse_y = mouse_pos(vm)
                    for i in dictionary:
                        point_key = i;
                        point_x, point_y = dictionary[i];
                        mouse_dist = math.sqrt(np.linalg.norm(mouse_x-point_x) + np.linalg.norm(mouse_y-point_y));
                        yield point_key, mouse_dist

                def find_closest(calculated_distances):
                    distance_keys = []; distance_values = [];
                    for i, j in calculated_distances:
                        distance_keys.append(i)
                        distance_values.append(j)
                    closest_point = distance_keys[distance_values.index(min(distance_values))];
                    del calculated_distances, distance_values, distance_keys
                    return closest_point

                def new_position(vm, dictionary):
                    vm.visible = False; vm.resetClicks();
                    calculated_distances = calc_distances(vm, dictionary);
                    closest_point = find_closest(calculated_distances);
                    return closest_point

                def update_background(BG_PNG):
                    background = visual.ImageStim(win, image=BG_PNG);
                    return background

                def save_background():
                    win.getMovieFrame(buffer='back'); win.saveMovieFrames(BG_PNG);

                BG_PATH = './stimuli/background';
                BG_FILE = './stimuli/background/background.png.zip';

                unzipper = zipfile.ZipFile(BG_FILE, 'r');
                unzipper.extractall(BG_PATH); unzipper.close();

                DONE = False;
                resize_COUNT=0;
                NEW2 = '';
                imageZoomer_VAR = None;
                ROUND_TWO_COUNT = 0;
                ROUND_THREE_COUNT = 0;
                ROUND_FOUR_VAR = False;
                ROUND_FOUR_COUNT = 0;
                ROUND_FIVE_VAR = False;
                ROUND_FIVE_COUNT = 0;
                ROUND_SIX_COUNT = 0;

                def saveData(dataDict):

                    logFilePrefix = '_DATA_distanceRanking.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                    cols = [
                        'sizeKey',
                        'image',
                        'pointKey',
                        'xy'
                    ];

                    df = pd.DataFrame.from_dict(dataDict, orient='index')
                    df.columns = cols;
                    df.to_csv(logFileName, index = False, header=True)

                def keyCounter(x):
                    if event.getKeys(["return"]):
                        x+=1
                    return x

                data_dict={};

                TASK_COMPLETE = False;
                vm.visible = False;
                undealer_VAR = False;
                redealer_VAR = False;
                blank1 = [];
                blank2 = [];
                blank3 = [];
                sCOUNTS = 0;
                index = 0;
                switch_dict = dictObj();
                switch_dict2 = dictObj();
                data_dict = {};

                while True:
                # try:
                    if INC < N_TRIALS:

                        r1_text.opacity = 1;
                        r2_text.opacity = 1;
                        r3_text.opacity = 0;
                        r4_text.opacity = 0;
                        r5_text.opacity = 0;
                        r6_text.opacity = 0;
                        r7_text.opacity = 0;
                        r8_text.opacity = 0;

                        r1_text_position = (-275, r1_y);
                        r2_text_position = (275, r1_y);
                        r3_text_position = (4000, 4000);
                        r4_text_position = (4000, 4000);
                        r5_text_position = (4000, 4000);
                        r6_text_position = (4000, 4000);
                        r7_text_position = (4000, 4000);
                        r8_text_position = (4000, 4000);

                        r1_text.pos = r1_text_position;
                        r2_text.pos = r2_text_position;
                        r3_text.pos = r3_text_position;
                        r4_text.pos = r4_text_position;
                        r5_text.pos = r5_text_position;
                        r6_text.pos = r6_text_position;
                        r7_text.pos = r7_text_position;
                        r8_text.pos = r8_text_position;

                    if INC >= N_TRIALS:
                        test_rect2.pos = [0, 432]
                        ROUND_TWO_VAR = True;
                        message.text = ROUND_TWO_TEXT;
                        message.wrapWidth=600;
                        message.alignHoriz='center';
                        message.alignVert='bottom';

                    dealer = dealer_image(INC, message);

                    image_name = 'im'+ str(INC);
                    message.pos = MESSAGE_POSITION;
                    stimlist = [bg, dealerBlock1, dealer, choice_boundary, image];

                    display = buffer_stimuli(stimlist);
                    display.draw();

                    textBlock.draw();

                    small_gray_block.draw();
                    large_gray_block.draw();

                    small.draw();
                    large.draw();

                    image3.draw();
                    image4.draw();

                    test_rect2.draw();

                    message.draw();

                    sort01_vert_grey.draw();
                    sort02a_vert_grey.draw();
                    sort02b_vert_grey.draw();
                    sort03a_vert_grey.draw();
                    sort03b_vert_grey.draw();
                    sort03c_vert_grey.draw();
                    sort03d_vert_grey.draw();

                    sort01_vert.draw();
                    sort02a_vert.draw();
                    sort02b_vert.draw();
                    sort03a_vert.draw();
                    sort03b_vert.draw();
                    sort03c_vert.draw();
                    sort03d_vert.draw();

                    sort01_horiz_grey.draw();
                    sort02a_horiz_grey.draw();
                    sort02b_horiz_grey.draw();
                    sort03a_horiz_grey.draw();
                    sort03b_horiz_grey.draw();
                    sort03c_horiz_grey.draw();
                    sort03d_horiz_grey.draw();

                    sort01_horiz.draw();
                    sort02a_horiz.draw();
                    sort02b_horiz.draw();
                    sort03a_horiz.draw();
                    sort03b_horiz.draw();
                    sort03c_horiz.draw();
                    sort03d_horiz.draw();

                    test_rect_bottom1.draw();
                    test_rect_bottom2.draw();
                    test_rect_bottom3.draw();

                    end_round_block.draw();
                    begin_round_block.draw();
                    begin_round_text_part1.draw();
                    begin_round_text_part2.draw();

                    test_rect.draw();

                    message2.draw();

                    r1_text.draw();
                    r2_text.draw();
                    r3_text.draw();
                    r4_text.draw();
                    r5_text.draw();
                    r6_text.draw();
                    r7_text.draw();
                    r8_text.draw();

                    zoomBackground.draw();
                    zoomImage.draw();
                    zoomText.draw();

                    end_task_text_prompt.draw();

                    switcher_VAR = resetter_keys(switcher_VAR, vm, sCOUNTS, zCOUNTS);
                    if switcher_VAR == True :
                        sCOUNTS, index, switcher_VAR, switch_dict2 = sREDEAL_DATA(sCOUNTS, index)

                    if vm.getClicks() and dealer.contains(mouse) and INC != N_TRIALS:
                        print('vmCLICKED: , dealer')
                        dealer_tools(dealerBlock2, vm); vm.resetClicks();
                        if dealer_VAR == True:
                            pointer = pointer_update(INC, pointer, vm, dealer);
                            dealer_VAR, vm = DEALER_UPDATE(pointer);

                    if vm.getClicks() and choice_boundary.contains(mouse):
                        print('vmCLICKED: , choice_boardary')

                        selection2.pos = selection.pos;
                        vm.resetClicks();
                        if dealer_VAR == False:
                            image, bg, INC, vm, dealer_VAR = CHOICE_UPDATE(INC, dealerBlock2);

                        if redealer_VAR == True and zCOUNTS == 1:
                            redealer_VAR = False;
                            zCOUNTS = 0;
                            index = 0;
                            undealer_VAR, image, bg = zRESETTER_UPDATE(image_key, data_dict);

                        if sCOUNTS == 1:
                            selection.setOpacity(1);
                            selection2.setOpacity(0);
                            sRESETTER_UPDATE(index, switch_dict2);
                            index = 0;
                            image.opacity = 0;
                            save_background();
                            bg = update_background(BG_PNG);
                            selection2.setOpacity(1);

                    if undealer_VAR == True and zCOUNTS == 1:
                        image, bg, redealer_VAR = zUNDEALER_UPDATE(image3, image4);
                        point_key, point_value, image_key = zUNDEAL_DATA(data_dict);

                    undealer_VAR = unsetter_keys(undealer_VAR, zCOUNTS, sCOUNTS, image, INC);
                    if zCOUNTS == 0 and undealer_VAR == True:
                        zCOUNTS += 1;

                    vm.draw();
                    win.flip();
                    quit(win);
                    text = point_tools(vm);
                    pointer = vm.pointer;
                    imageZoomer_VAR = imageZoomer(win, vm, resize_VAR, zoomImage, selection2, selection);

                    if type(imageZoomer_VAR) == tuple:
                        resize_VAR = imageZoomer_VAR[0];
                        zoomText.text = imageZoomer_VAR[1];

                    if ROUND_TWO_VAR == True and ROUND_TWO_COUNT < 1:

                        end_round_block.opacity = .35;
                        begin_round_block.opacity = 1;
                        begin_round_text_part1.pos = (0,75);
                        begin_round_text_part2.pos = (0,-75);

                        ROUND_TWO_COUNT = keyCounter(ROUND_TWO_COUNT)

                        if ROUND_TWO_COUNT == 1:

                            ROUND_THREE_VAR = True;

                            test_rect_bottom2.pos = [0, -450]

                            end_round_block.opacity = 0;
                            begin_round_block.opacity = 0;
                            begin_round_text_part1.pos = (4000,4000);
                            begin_round_text_part2.pos = (4000,4000);

                            sort01_vert.setOpacity(1);
                            sort02a_vert.setOpacity(1);
                            sort02b_vert.setOpacity(1);

                            r1_text.opacity = 1;
                            r2_text.opacity = 1;
                            r3_text.opacity = 1;
                            r4_text.opacity = 1;
                            r5_text.opacity = 0;
                            r6_text.opacity = 0;
                            r7_text.opacity = 0;
                            r8_text.opacity = 0;

                            r1_text_position = (-365, r1_y);
                            r2_text_position = (-120, r1_y);
                            r3_text_position = (120, r1_y);
                            r4_text_position = (365, r1_y);
                            r5_text_position = (4000, 4000);
                            r6_text_position = (4000, 4000);
                            r7_text_position = (4000, 4000);
                            r8_text_position = (4000, 4000);

                            r1_text.pos = r1_text_position;
                            r2_text.pos = r2_text_position;
                            r3_text.pos = r3_text_position;
                            r4_text.pos = r4_text_position;
                            r5_text.pos = r5_text_position;
                            r6_text.pos = r6_text_position;
                            r7_text.pos = r7_text_position;

                            end_round_text_prompt.text = 'Press "return" when you have completed round 2.';

                            end_round_text_prompt.wrapWidth=800;
                            end_round_text_prompt.alignHoriz='center';
                            end_round_text_prompt.pos = (0,-440);
                            print(ROUND_TWO_VAR)
                            print(ROUND_TWO_COUNT)

                    if ROUND_THREE_VAR == True and ROUND_THREE_COUNT < 1:
                        ROUND_THREE_COUNT = keyCounter(ROUND_THREE_COUNT);
                        if ROUND_THREE_COUNT == 1:

                            ROUND_THREE_VAR = False;
                            ROUND_FOUR_VAR = True;

                            end_round_block.opacity = .35;
                            begin_round_block.opacity = 1;
                            begin_round_text_part1.pos = (0,75);
                            begin_round_text_part1.text ="You have completed round 2";
                            begin_round_text_part2.pos = (0,-75);
                            begin_round_text_part2.text ='...press "return" to begin round 3...';
                            end_round_text_prompt.text = '';


                    if ROUND_FOUR_VAR == True and ROUND_FOUR_COUNT < 1:
                        ROUND_FOUR_COUNT = keyCounter(ROUND_FOUR_COUNT);
                        if ROUND_FOUR_COUNT == 1:


                            ROUND_FOUR_VAR = False;
                            ROUND_FIVE_VAR = True;

                            message.text = '';
                            message.wrapWidth=600;
                            message.alignHoriz='center';
                            message.alignVert='bottom';
                            test_rect.pos = [0, 435];

                            message2.pos = MESSAGE_POSITION;

                            message2.wrapWidth=600;
                            message2.alignHoriz='center';
                            message2.alignVert='bottom';

                            test_rect_bottom3.pos = [0, -450]

                            end_round_text_prompt.text = 'Press "return" when you have completed round 3.';
                            end_round_text_prompt.wrapWidth=800;
                            end_round_text_prompt.alignHoriz='center';
                            end_round_text_prompt.pos = (0,-440);

                            end_round_block.opacity = 0;
                            begin_round_block.opacity = 0;
                            begin_round_text_part1.pos = (4000,4000);
                            begin_round_text_part2.pos = (4000,4000);

                            sort01_vert.setOpacity(1);
                            sort02a_vert.setOpacity(1);
                            sort02b_vert.setOpacity(1);
                            sort03a_vert.setOpacity(1);
                            sort03b_vert.setOpacity(1);
                            sort03c_vert.setOpacity(1);
                            sort03d_vert.setOpacity(1);

                            r1_text.opacity = 1;
                            r2_text.opacity = 1;
                            r3_text.opacity = 1;
                            r4_text.opacity = 1;
                            r5_text.opacity = 1;
                            r6_text.opacity = 1;
                            r7_text.opacity = 1;
                            r8_text.opacity = 1;

                            r1_text_position = (-425, r1_y);
                            r2_text_position = (-300, r1_y);
                            r3_text_position = (-175, r1_y);
                            r4_text_position = (-60, r1_y);
                            r5_text_position = (60, r1_y);
                            r6_text_position = (175, r1_y);
                            r7_text_position = (300, r1_y);
                            r8_text_position = (425, r1_y);

                            r1_text.pos = r1_text_position;
                            r2_text.pos = r2_text_position;
                            r3_text.pos = r3_text_position;
                            r4_text.pos = r4_text_position;
                            r5_text.pos = r5_text_position;
                            r6_text.pos = r6_text_position;
                            r7_text.pos = r7_text_position;
                            r8_text.pos = r8_text_position;


                    if ROUND_FIVE_VAR == True and ROUND_FIVE_COUNT < 1:
                        ROUND_FIVE_COUNT = keyCounter(ROUND_FIVE_COUNT);

                        if ROUND_FIVE_COUNT == 1:
                            message2.pos = (4000, 4000);

                            image.opacity = 0;
                            bg.opacity = 0;
                            dealer.opacity = 0;
                            textBlock.opacity = 0;
                            small.opacity = 0;
                            large.opacity = 0;
                            image3.opacity = 0;
                            image4.opacity = 0;
                            zoomImage.opacity = 0;
                            zoomText.opacity = 0;
                            message.opacity = 1;
                            message.text = '';
                            zoomBackground.opacity = 1;
                            zoomText.opacity = 1;
                            zoomText.pos = (0, 0);

                            zoomText.height = 45;
                            zoomText.pos = (0, 100)
                            zoomText.text = 'Done!';

                            fileName = logFileDir + studyIDPrefix + subjectID + '_DISPLAYRANKED_distanceRanking';
                            savedFrame =  fileName + '.png';
                            win.getMovieFrame(buffer='front');
                            win.saveMovieFrames(savedFrame);
                            unzipper = zipfile.ZipFile(BG_FILE, 'r');
                            unzipper.extractall(BG_PATH); unzipper.close();
                            DONE = True;


                            # taskInfo['sizeRanking']=True;
                            taskInfo['distanceRanking']['taskCompleted']=True;
                            logFilePrefix = '_DATA_taskInfo.csv';
                            logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                            df = pd.DataFrame(taskInfo).T
                            df.to_csv(logFileName, index = True, header=True)

                    if DONE == True:

                        # index
                        index = range(N_TRIALS);
                        # images
                        POPPED_imKEYS = popped_images.keys()
                        POPPED_IMAGES = popped_images.values()
                        # points
                        POPPED_pointKEYS = popped_dictionary.keys()
                        POPPED_XYs = popped_dictionary.values()

                        # combine the data into one dictionary
                        dataDict = dict(zip(index,zip(

                                POPPED_imKEYS,
                                POPPED_IMAGES,
                                POPPED_pointKEYS,
                                POPPED_XYs

                                )));

                        saveData(dataDict);
                        end_task_text_prompt.pos = (0, -100);
                        ROUND_SIX_COUNT = keyCounter(ROUND_SIX_COUNT);
                        if ROUND_SIX_COUNT == 1:
                            print('...DISTANCE RANKING TASK COMPLETE')
                            break

            except:
                core.quit()


        #########################
        ## TASK: glossMatching ##
        #########################
        if task == 'glossMatching':
            try:

                print('...STARTING GLOSS MATCHING TASK')

                logFilePrefix = '_DATA_glossMatching.csv';
                logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;


                gls = [
                'g1',
                'g2',
                'g3',
                'g4',
                'g5',
                'g6',
                'g7',
                ];


                i = 0;
                next_inc = 0;
                text = None;
                rated = True;
                IMAGE_SIZE = (440, 440);
                IMAGE_SIZE_SCALAR = 1.7;
                r1_Yconst = -400;
                r1_text_position = (-300, r1_Yconst);
                r2_text_position = (-200, r1_Yconst);
                r3_text_position = (-100, r1_Yconst);
                r4_text_position = (0, r1_Yconst);
                r5_text_position = (100, r1_Yconst);
                r6_text_position = (200, r1_Yconst);
                r7_text_position = (300, r1_Yconst);

                sizeKey = getTaskObjects('size')

                dataDict = {};
                for index in range(len(sizeKey)):
                    image = sizeKey[index];

                    element = {index: {
                                'image': image,
                                'glossRating':None}
                                };

                    dataDict.update(element);

                def findImageIndex(imageName):
                    try:
                        for index in range(len(dataDict)):
                            image = dataDict[index]['image']
                            if imageName == image:
                                return(index)
                    except:
                        index = 'NULL'
                        return

                dim_value_width, dim_value_height = (1920, 1080);

                sizeKey = getTaskObjects('size')
                glossKey = getTaskObjects('gloss')
                layerKey = getTaskObjects('layer')

                userLabel = 'object name';

                objectName = visual.TextStim( win,
                                        userLabel,
                                        height = 30);
                objectName.pos = (0, 415);

                endBlock = visual.Rect(win=win,
                    width=2000,
                    height=2000,
                    lineColor='grey',
                    lineWidth=3.0,
                    fillColor='grey',
                    units='pix');
                endBlock.setOpacity(0);

                endText = visual.TextStim(win,
                                        text='',
                                        height = 30);
                endText.pos = (0, 0);
                endText.setOpacity(0);

                def sizeImage(win, key):
                        im = visual.ImageStim(win,
                                            image=key,
                                            size = IMAGE_SIZE,
                                            pos= (-350, 50),
                                            units='pix');
                        return im

                match = visual.Circle(win,
                              radius=25,
                              edges=26,
                              units='pix',
                              lineColor='gray',
                              fillColor='gray');

                match_position = (350, 50);
                match.pos = match_position;

                g1 = visual.ImageStim(win, image=glossKey[0], units='pix');
                g2 = visual.ImageStim(win, image=glossKey[1], units='pix');
                g3 = visual.ImageStim(win, image=glossKey[2], units='pix');
                g4 = visual.ImageStim(win, image=glossKey[3], units='pix');
                g5 = visual.ImageStim(win, image=glossKey[4], units='pix');
                g6 = visual.ImageStim(win, image=glossKey[5], units='pix');
                g7 = visual.ImageStim(win, image=glossKey[6], units='pix');

                def glObjEval(glStrPrefix):
                    for gl in gls:
                        glo = eval(gl + glStrPrefix);

                g1.size = g1.size * 1;
                g2.size = g2.size * 1;
                g3.size = g3.size * 1;
                g4.size = g4.size * 1;
                g5.size = g5.size * 1;
                g6.size = g6.size * 1;
                g7.size = g7.size * 1;

                g1.pos = match_position;
                g2.pos = match_position;
                g3.pos = match_position;
                g4.pos = match_position;
                g5.pos = match_position;
                g6.pos = match_position;
                g7.pos = match_position;

                g1.opacity = 0;
                g2.opacity = 0;
                g3.opacity = 0;
                g4.opacity = 0;
                g5.opacity = 0;
                g6.opacity = 0;
                g7.opacity = 0;

                choice = visual.Circle(win,
                                radius=25,
                                edges=52,
                                units='pix',
                                lineColor='white',
                                fillColor=None)

                choice.opacity = 1;

                rtext_size = (50, 50);
                rtext_color = 'white';
                rtext_units = 'pix';

                r1_text = visual.TextStim(win, '1', color=rtext_color, units=rtext_units);
                r2_text = visual.TextStim(win, '2', color=rtext_color, units=rtext_units);
                r3_text = visual.TextStim(win, '3', color=rtext_color, units=rtext_units);
                r4_text = visual.TextStim(win, '4', color=rtext_color, units=rtext_units);
                r5_text = visual.TextStim(win, '5', color=rtext_color, units=rtext_units);
                r6_text = visual.TextStim(win, '6', color=rtext_color, units=rtext_units);
                r7_text = visual.TextStim(win, '7', color=rtext_color, units=rtext_units);

                r1_text.size = rtext_size
                r2_text.size = rtext_size
                r3_text.size = rtext_size
                r4_text.size = rtext_size
                r5_text.size = rtext_size
                r6_text.size = rtext_size
                r7_text.size = rtext_size

                r1_text.pos = r1_text_position;
                r2_text.pos = r2_text_position;
                r3_text.pos = r3_text_position;
                r4_text.pos = r4_text_position;
                r5_text.pos = r5_text_position;
                r6_text.pos = r6_text_position;
                r7_text.pos = r7_text_position;

                r1_text.autoDraw = True;
                r2_text.autoDraw = True;
                r3_text.autoDraw = True;
                r4_text.autoDraw = True;
                r5_text.autoDraw = True;
                r6_text.autoDraw = True;
                r7_text.autoDraw = True;

                scrnText = visual.TextStim(win,
                                text='',
                                color=rtext_color,
                                units=rtext_units);
                scrnText.pos = (0, -275);

                match.autoDraw = True;

                g1.autoDraw = True;
                g2.autoDraw = True;
                g3.autoDraw = True;
                g4.autoDraw = True;
                g5.autoDraw = True;
                g6.autoDraw = True;
                g7.autoDraw = True;

                choice.autoDraw = True;
                scrnText.autoDraw = True;
                endBlock.autoDraw = True;
                endText.autoDraw = True;

                # reset_inc = 0;

                def quit():
                    QUIT_KEYS = event.getKeys('0')
                    if len(QUIT_KEYS) > 0:
                        core.quit();
                        win.close()

                def next(next_inc):
                    NEXT_KEYS = event.getKeys('return')
                    if len(NEXT_KEYS) > 0:
                        next_inc += 1
                    return next_inc

                def nextEval(next_inc, i, im, message, rated, win, dataDict, logFilePrefix, ans):
                    next_inc=next(next_inc);

                    if next_inc == 1:
                        message = 'Are you sure?';

                    if next_inc == 2:
                        i += 1
                        next_inc = 0;
                        message = '';
                        rated = True;

                        imageName = im.image;

                        index = findImageIndex(imageName);

                        nuissance = './stimuli/size/';
                        imageName = imageName.replace(nuissance, '');
                        nuissance = '.jpg.png-gaussian.png';
                        imageName = imageName.replace(nuissance, '');

                        logFilePrefix = 'IMAGE_{}_glossMatching.png'.format(imageName);
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                        savedFrame = logFileName;
                        win.getMovieFrame(buffer='front');
                        win.saveMovieFrames(savedFrame);

                        dataDict[index]['glossRating']=ans;
                        del im

                    return next_inc, i, message, rated


                def ratingEval(rgb_layer2, key, i):
                    if rgb_layer2 == (255, 0, 0):
                        ans = 'gloss level 1'
                        g1.opacity = 1;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 0;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        r1_text_position = (300, r1_Yconst);
                        return r1_text_position

                    if rgb_layer2 == (0, 128, 0):
                        ans = 'gloss level 2'
                        g1.opacity = 0;
                        g2.opacity = 1;
                        g3.opacity = 0;
                        g4.opacity = 0;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        r2_text_position = (200, r1_Yconst);
                        return r2_text_position

                    if rgb_layer2 == (0, 255, 255):
                        ans = 'gloss level 3'
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 1;
                        g4.opacity = 0;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        r3_text_position = (100, r1_Yconst);
                        return r3_text_position

                    if rgb_layer2 == (0, 165, 255):
                        ans = 'gloss level 4'
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 1;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        r4_text_position = (0, r1_Yconst);
                        return r4_text_position

                    if rgb_layer2 == (0, 0, 255):
                        ans = 'gloss level 5'
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 0;
                        g5.opacity = 1;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        r5_text_position = (-100, r1_Yconst)
                        return r5_text_position

                    if rgb_layer2 == (128, 0, 128):
                        ans = 'gloss level 6'
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 0;
                        g5.opacity = 0;
                        g6.opacity = 1;
                        g7.opacity = 0;
                        r6_text_position = (-200, r1_Yconst)
                        return r6_text_position

                    if rgb_layer2 == (203, 192, 255):
                        ans = 'gloss level 7'
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 0;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 1;
                        r7_text_position = (-300, r1_Yconst)
                        return r7_text_position

                def restartTrial(rated, choice):
                    if rated == True:
                        g1.opacity = 0;
                        g2.opacity = 0;
                        g3.opacity = 0;
                        g4.opacity = 1;
                        g5.opacity = 0;
                        g6.opacity = 0;
                        g7.opacity = 0;
                        choice.pos = r4_text_position
                        rated = False;
                    return rated

                def saveData(dataDict):
                    logFilePrefix = '_DATA_glossMatching.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;


                    for index in range(len(dataDict)):

                        if dataDict[index]['glossRating'] == 'gloss level 1':
                            ans = 7;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 2':
                            ans = 6;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 3':
                            ans = 5;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 4':
                            ans = 4;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 5':
                            ans = 3;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 6':
                            ans = 2;
                            dataDict[index]['glossRating'] = ans;

                        elif dataDict[index]['glossRating'] == 'gloss level 7':
                            ans = 1;
                            dataDict[index]['glossRating'] = ans;

                    df = pd.DataFrame.from_dict(dataDict, orient='index');
                    df.to_csv(logFileName, index = True, header=True)

                TASK_DONE = False;
                dim_value_width, dim_value_height = (1920, 1080);
                sizeKey = getTaskObjects('size')

                random.shuffle(sizeKey);

                glossKey = getTaskObjects('gloss')
                layerKey = getTaskObjects('layer')

                def vmX_to_imX(dim_value_width):
                    mousePx = np.arange((-1*dim_value_width*.50), (dim_value_width*.50), 1);
                    imagePx = np.arange(0, dim_value_width, 1);
                    class my_dictionary(dict):
                        def __init__(self):
                            self = dict()
                        def add(self, key, value):
                            self[key] = value
                    dict_obj = my_dictionary()
                    for i in range(len(mousePx)):
                        dict_obj.add(mousePx[i], imagePx[i])
                    return dict_obj

                def vmY_to_imY(dim_value_height):
                    mousePx = np.arange((-1*dim_value_height*.50)+1, (dim_value_height*.50)+1, 1);
                    imagePx = np.arange(0, dim_value_height+1, 1);
                    class my_dictionary(dict):
                        def __init__(self):
                            self = dict()
                        def add(self, key, value):
                            self[key] = value
                    dict_obj = my_dictionary()
                    for i in range(len(mousePx)):
                        dict_obj.add(mousePx[i], imagePx[i])
                    return dict_obj

                dX = vmX_to_imX(dim_value_width);
                dY = vmY_to_imY(dim_value_height);

                layer1=layerKey[0];
                layer2=layerKey[1];

                def pixelColor_layer1(x, y):
                    import cv2
                    import numpy as np
                    im = cv2.imread(layer1);
                    im = cv2.flip(im,-1)
                    rgb = cv2.resize(im, (dim_value_width,dim_value_height))
                    color = rgb[y, x]
                    r=color[0];
                    g=color[1];
                    b=color[2];
                    return r, g, b

                def pixelColor_layer2(x, y):
                    import cv2
                    import numpy as np
                    im = cv2.imread(layer2);
                    im = cv2.flip(im,-1);
                    rgb = cv2.resize(im,((dim_value_width,dim_value_height)))
                    color = rgb[y, x]
                    r=color[0];
                    g=color[1];
                    b=color[2];
                    return r, g, b

                data_dict = {};
                DONE_DONE = False;

                def object_names(imageName):

                    try:

                        logFilePrefix = '_DATA_objectNaming.csv';
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        nameLib = pd.read_csv(logFileName);
                        nameLib = nameLib.T
                        nameLib = nameLib.drop(nameLib.index[0])
                        cols = ['image', 'userLabel']
                        nameLib.columns = cols;

                        index = findImageIndex(imageName);
                        userLabel = nameLib['userLabel'][index];

                    except:
                        userLabel = '???'
                    return userLabel


                while True:

                    vm.visible = False;

                    if i < N_TRIALS:

                        key = sizeKey[i];
                        objectName.text = object_names(key);

                        im = sizeImage(win, key);

                    if i >= N_TRIALS:

                        objectName.text = 'Done!';
                        objectName.pos=(0,0);

                        im.opacity=0;
                        endBlock.opacity=1;
                        endText.opacity=1;
                        endText.text = 'Done!';
                        TASK_DONE = True;

                        fileNames = data_dict.keys();
                        glossLevels = data_dict.values();

                    im.draw();
                    vm.draw();
                    rated = restartTrial(rated, choice);

                    if vm.getClicks():

                        mXY = vm.getPos();
                        print('gloss level: ', ans)
                        vm.resetClicks();
                        mX=int(mXY[0]);
                        mY=int(mXY[1]);
                        x = dX[mX];
                        y = dY[mY];

                        rgb_layer1 = pixelColor_layer1(x, y);

                        if rgb_layer1 == (255, 0, 0):
                            rgb_layer2 = pixelColor_layer2(x, y);
                            key = im.image;
                            choice_position = ratingEval(rgb_layer2, key, i);
                            choice.pos = choice_position;

                    objectName.draw();
                    win.flip();
                    quit();

                    image = im.image;

                    for gl in gls:
                        glo = eval(gl + '.opacity');
                        if glo == 1:
                            ans = 'gloss level ' + (gl.replace('g', ''));
                            data_dict[key] = ans;

                    next_inc, i, text, rated = nextEval(next_inc, i, im, text, rated, win, dataDict, logFilePrefix, ans);

                    scrnText.text = text;
                    if TASK_DONE == True:
                        saveData(dataDict);
                        print('...GLOSS MATCHING TASK COMPLETE')
                        event.waitKeys();

                        match.autoDraw = False;
                        g1.autoDraw = False;
                        g2.autoDraw = False;
                        g3.autoDraw = False;
                        g4.autoDraw = False;
                        g5.autoDraw = False;
                        g6.autoDraw = False;
                        g7.autoDraw = False;
                        choice.autoDraw = False;
                        scrnText.autoDraw = False;
                        endBlock.autoDraw = False;
                        endText.autoDraw = False;

                        r1_text.autoDraw = False;
                        r2_text.autoDraw = False;
                        r3_text.autoDraw = False;
                        r4_text.autoDraw = False;
                        r5_text.autoDraw = False;
                        r6_text.autoDraw = False;
                        r7_text.autoDraw = False;

                        del endText, im, objectName, endBlock, match, choice, scrnText
                        del g1, g2, g3, g4, g5, g6, g7
                        del r1_text, r2_text, r3_text, r4_text, r5_text, r6_text, r7_text

                        taskInfo['glossMatching']['taskCompleted']=True;

                        # WRITE
                        logFilePrefix = '_DATA_taskInfo.csv';
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        df = pd.DataFrame(taskInfo).T
                        df.to_csv(logFileName, index = True, header=True)

                        break

            except:
                core.quit()


        #########################
        ## TASK: shineMapping  ##
        #########################
        if task == 'shineMapping':
            vm.visible = False;
            try:

                print('...STARTING SHINE MAPPING TASK')

                def saveData(dataDict):

                    logFilePrefix = '_DATA_shineMapping.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                    cols = [
                        'pointKey',
                        'image',
                        'xyCoords',
                        'stim.xys',
                        'opacity'
                    ];

                    df = pd.DataFrame.from_dict(data, orient='index')
                    df.columns = cols;
                    df.to_csv(logFileName, index = False, header=True)


                sizeKey = getTaskObjects('size');

                dataDict = {};
                for index in range(len(sizeKey)):
                    image = sizeKey[index];
                    element = {index: {'image': image}};
                    dataDict.update(element);

                def findImageIndex(imageName):
                    try:
                        for index in range(len(dataDict)):
                            image = dataDict[index]['image']
                            if imageName == image:
                                return(index)
                    except:
                        index = 'NULL'
                        return

                def saveGrid(gridInfo, imageName):

                    nuissance = './stimuli/size/';
                    imageName = imageName.replace(nuissance, '')
                    nuissance = '.jpg.png-gaussian.png';
                    imageName = imageName.replace(nuissance, '')

                    logFilePrefix = '_DATA_shineMapping.csv';
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;

                    df = pd.DataFrame.from_dict(gridInfo, orient='index')
                    df.to_csv(logFileName, index = False, header=True)

                userLabel = 'object name';
                objectName = visual.TextStim( win,
                                        userLabel,
                                        height = 30,
                                        alignVert='center',
                                        alignHoriz='center',
                                        units='pix');

                objectName.pos = (0, 365);

                gridImg = getTaskObjects('grid')[0];

                im = visual.ImageStim(
                        win,
                        image= gridImg,
                        size = (500, 500),
                        units = 'pix');

                grid = visual.ImageStim(
                        win=win,
                        image=gridImg);

                bWidth= 600
                bHeight= 600
                border = visual.Rect(win=win,
                    width=bWidth,
                    height=bHeight,
                    fillColor=None,
                    lineColor='black',
                    units='pix');

                def quit():
                    QUIT_KEYS = event.getKeys('0')
                    if len(QUIT_KEYS) > 0:
                        core.quit();
                        win.close();


                # array of coordinates for each element
                xMIN = (575/2) * -1; xMAX = (575/2);
                yMIN = (575/2) * -1; yMAX = (575/2);
                xDist, yDist = (25, 25);
                xDim = np.linspace(xMIN, xMAX, xDist)
                yDim = np.linspace(yMIN, yMAX, yDist)
                xCoords, yCoords = np.meshgrid(xDim, yDim, indexing = 'ij')
                xyCoords = np.transpose(np.vstack([xCoords.ravel(), yCoords.ravel()]))
                num_check = len(xyCoords)
                check_size = [23, 23]
                location = [0, 0]
                loc = np.array(location) + np.array(check_size) // 2
                # array of rgbs for each element (2D)
                colors = np.random.random((num_check, 3))
                colors = colors * 0;
                colors = colors + [255, 130, 0];
                # array of rgbs for each element (2D)
                colors = np.random.random((num_check, 3))
                stim = visual.ElementArrayStim(win,
                                               xys=xyCoords,
                                               colors='yellow',
                                               nElements=len(xyCoords),
                                               elementMask=None,
                                               elementTex=None,
                                               colorSpace='rgb',
                                               sizes=(check_size[0],check_size[1]));

                stim.size = (check_size[0] * num_check,
                             check_size[1] * num_check)

                gridInfo = {};
                for i in range(len(xyCoords)):
                    stim.opacities[i] = 0.0;
                    key = 'p' + str(i);
                    element = {key: {
                                'image': None,
                                'index': i,
                                'xyCoords': None,
                                'stim.xys': None,
                                'opacity': 0.0,
                                'clickCount':None}}
                    gridInfo.update(element);

                class dictObj(dict):
                    def __init__(self):
                        self = dict()
                    def add(self, key, value):
                        self[key] = value
                point_dict = dictObj();
                for i in range(len(xyCoords)):
                    point_dict.add('p'+str(i), (xyCoords[i][0], xyCoords[i][1]));

                def getClicked_dict():
                    nxClicked_dict = dictObj();
                    for i in range(len(xyCoords)):
                        nxClicked_dict.add('p'+str(i), 0);
                    return nxClicked_dict

                nxClicked_dict = getClicked_dict();

                xMIN = (600/2) * -1; xMAX = (600/2);
                yMIN = (600/2) * -1; yMAX = (600/2);

                block = visual.Rect(win=win,
                    width=600,
                    height=50,
                    lineColor='gray',
                    lineWidth=1.0,
                    fillColor='gray',
                    units='pix');
                block.pos = (0, 365);

                endBlock = visual.Rect(win=win,
                    width=600,
                    height=600,
                    lineColor='grey',
                    lineWidth=3.0,
                    fillColor='grey',
                    units='pix');
                endBlock.setOpacity(0);

                endText = visual.TextStim(win,
                                        text='',
                                        height = 30,
                                        alignVert='center',
                                        alignHoriz='center',
                                        units='pix');
                endText.pos = (2000, 2000);
                endText.setOpacity(0);

                def save_background(imageName):

                    nuissance = './stimuli/size/';
                    imageName = imageName.replace(nuissance, '')
                    nuissance = '.jpg.png-gaussian.png';
                    imageName = imageName.replace(nuissance, '')
                    logFilePrefix = 'IMAGE_{}_shineMapping.png'.format(imageName);
                    logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                    savedFrame = logFileName;
                    win.getMovieFrame(buffer='front');
                    win.saveMovieFrames(savedFrame);

                    return mappedFile

                def update_background(mappedFile):
                    background = visual.ImageStim(win, image=mappedFile);
                    return background

                clickCount_block = visual.Rect(win=win,
                    width=175,
                    height=100,
                    fillColor='grey',
                    lineColor='grey',
                    units='pix');
                clickCount_block.pos = (0, -415)

                clickCount_text = visual.TextStim( win,
                                        height = 30,
                                        text = '',
                                        units='pix');
                clickCount_text.pos = (0, -415)

                message_block = visual.Rect(win=win,
                    width=250,
                    height=80,
                    fillColor='grey',
                    lineColor='grey',
                    units='pix');
                message_block.pos = (2000, 2000);

                message = visual.TextStim( win,
                                        height = 30,
                                        text = 'Are you sure?',
                                        alignVert='center',
                                        alignHoriz='center',
                                        units='pix');
                message.pos = (2000, 2000);
                message.setOpacity = (0);

                begin_block = visual.Rect(win=win,
                    width=250,
                    height=80,
                    fillColor='grey',
                    lineColor='grey',
                    units='pix');
                begin_block.pos = (0, -415);

                def mouse_pos(vm, mouse):
                    mouse_x, mouse_y = mouse.getPos()[0], mouse.getPos()[1]
                    return mouse_x, mouse_y

                def calc_distances(vm, dictionary, mouse):
                    mouse_x, mouse_y = mouse_pos(vm, mouse)
                    for i in dictionary:
                        point_key = i;
                        point_x, point_y = dictionary[i];
                        mouse_dist = math.sqrt(np.linalg.norm(mouse_x-point_x) + np.linalg.norm(mouse_y-point_y));
                        yield point_key, mouse_dist

                def find_closest(calculated_distances):
                    distance_keys = []; distance_values = [];
                    for i, j in calculated_distances:
                        distance_keys.append(i)
                        distance_values.append(j)
                    closest_point = distance_keys[distance_values.index(min(distance_values))];
                    del calculated_distances, distance_values, distance_keys
                    return closest_point

                def new_position(vm, dictionary, mouse):
                    vm.visible = False; vm.resetClicks();
                    calculated_distances = calc_distances(vm, dictionary, mouse);
                    closest_point = find_closest(calculated_distances);
                    return closest_point

                TASK_DONE = False;
                DONE = False;
                clickCount_var = 0;
                next_inc = 0;
                counter_var = 0;

                sizeKey = getTaskObjects('size')

                random.shuffle(sizeKey);

                def getClicked_dict():
                    nxClicked_dict = dictObj();
                    for i in range(len(xyCoords)):
                        nxClicked_dict.add('p'+str(i), 0);
                    return nxClicked_dict

                nxClicked_dict = getClicked_dict();


                def object_names(imageName):
                    try:
                        logFilePrefix = '_DATA_objectNaming.csv';
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        nameLib = pd.read_csv(logFileName);
                        nameLib = nameLib.T
                        nameLib = nameLib.drop(nameLib.index[0])
                        cols = ['image', 'userLabel']
                        nameLib.columns = cols;
                        index = findImageIndex(imageName);
                        userLabel = nameLib['userLabel'][index];
                    except:
                        userLabel = '???'
                    return userLabel

                def next(next_inc, nxClicked_dict, im, counter_var, win):
                    NEXT_KEYS = event.getKeys('d')
                    if len(NEXT_KEYS) > 0:
                        counter_var+=1;
                        if counter_var == 2:
                            next_inc += 1
                        for i in nxClicked_dict:
                            nxClicked_dict[i]=0;
                    return next_inc, counter_var

                def sizeImage(win, key):
                    im = visual.ImageStim(win,
                                        image=key,
                                        size= (600, 600),
                                        units='pix');
                    return im


                index = 0;

                while True:
                    try:

                        if next_inc <= N_TRIALS:
                            objectName.text = object_names(key);

                            key = sizeKey[next_inc];
                            im = sizeImage(win, key);
                            objectName.text = object_names(key);

                            for i in gridInfo:
                                gridInfo[i]['image'] = im.image;

                        if next_inc >= N_TRIALS:
                            objectName.text = 'Done!';
                            objectName.pos=(0,0);
                            im.opacity=0;
                            grid.opacity=0;
                            border.opacity=0;
                            endText.text='Done';
                            endBlock.opacity=1;
                            TASK_DONE = True;

                    except (IndexError, ValueError):
                        objectName.text = 'Done!';
                        objectName.pos=(0,0);
                        im.opacity=0;
                        grid.opacity=0;
                        border.opacity=0;
                        endText.text='Done';
                        endBlock.opacity=1;
                        TASK_DONE = True;

                    im.draw();
                    grid.draw();
                    border.draw();

                    if next_inc < N_TRIALS:
                        objectName.text = object_names(key);

                    if vm.getClicks():
                        point_key = new_position(vm, point_dict, mouse);

                        if  gridInfo[point_key]['opacity'] == 0.50:
                            clickCount_var-=1;
                            if clickCount_var < 0:
                                clickCount_var = 0;

                            gridInfo[point_key]['opacity'] = 0.0;
                            index = gridInfo[point_key]['index']
                            stim = visual.ElementArrayStim(win,
                                                           xys=xyCoords,
                                                           colors='yellow',
                                                           nElements=len(xyCoords),
                                                           elementMask=None,
                                                           elementTex=None,
                                                           colorSpace='rgb',
                                                           sizes=(check_size[0],check_size[1]));
                            stim.size = (check_size[0] * num_check,
                                         check_size[1] * num_check)

                            for i in range(len(gridInfo)):
                                point_key = 'p' + str(i);
                                index = gridInfo[point_key]['index']
                                opacity = gridInfo[point_key]['opacity']
                                stim.opacities[index] = opacity;

                            del point_key;
                            vm.resetClicks();


                        elif  gridInfo[point_key]['opacity'] == 0 and clickCount_var < 30:

                                clickCount_var+=1;

                                gridInfo[point_key]['opacity'] = 0.50;
                                index = gridInfo[point_key]['index']
                                stim = visual.ElementArrayStim(win,
                                                               xys=xyCoords,
                                                               colors='yellow',
                                                               nElements=len(xyCoords),
                                                               elementMask=None,
                                                               elementTex=None,
                                                               colorSpace='rgb',
                                                               sizes=(check_size[0],check_size[1]));
                                stim.size = (check_size[0] * num_check,
                                             check_size[1] * num_check)

                                for i in range(len(gridInfo)):
                                    point_key = 'p' + str(i);
                                    index = gridInfo[point_key]['index']
                                    opacity = gridInfo[point_key]['opacity']
                                    stim.opacities[index] = opacity;

                        elif  gridInfo[point_key]['opacity'] == 0 and clickCount_var == 30:
                            pass

                            del point_key;
                            vm.resetClicks();

                    stim.draw();
                    grid.draw();
                    border.draw()
                    vm.draw();

                    block.draw();
                    endBlock.draw();
                    objectName.draw();
                    clickCount_block.draw();
                    clickCount_text.draw();
                    message_block.draw();
                    message.draw()
                    clickCount_text.text = str(clickCount_var);
                    win.flip();
                    quit();
                    next_inc, counter_var = next(next_inc, nxClicked_dict, im, counter_var, win);
                    if counter_var == 0:

                        clickCount_block.pos = (0, -415)
                        clickCount_text.pos = (0, -415)

                        message_block.pos = (2000, 2000);
                        message_block.opacity = 0;

                        message.pos = (2000, 2000);
                        message.opacity = 0;

                    if counter_var == 1:

                        clickCount_block.pos = (2000, 2000);
                        clickCount_text.pos = (2000, 2000);

                        message_block.pos = (0, -415)
                        message_block.opacity = 1;

                        message.pos = (0, -400);
                        message.opacity = 1;

                    if counter_var == 2:
                        for i in gridInfo:
                            gridInfo[i]['clickCount'] = clickCount_var;

                        clickCount_var = 0;
                        counter_var = 0;

                        clickCount_block.pos = (0, -415)
                        clickCount_text.pos = (0, -415)

                        message_block.pos = (2000, 2000);
                        message_block.opacity = 0;

                        message.pos = (2000, 2000);
                        message.opacity = 0;

                        imageName = im.image;
                        nuissance = './stimuli/size/';
                        imageName = imageName.replace(nuissance, '')
                        nuissance = '.jpg.png-gaussian.png';
                        imageName = imageName.replace(nuissance, '')
                        logFilePrefix = 'IMAGE_{}_shineMapping.png'.format(imageName);
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        savedFrame = logFileName;

                        win.getMovieFrame(buffer='front');
                        win.saveMovieFrames(savedFrame);

                        DONE = True;

                    if DONE == True:
                        saveGrid(gridInfo, image);

                        del stim

                        stim = visual.ElementArrayStim(win,
                                                       xys=xyCoords,
                                                       colors='yellow',
                                                       nElements=len(xyCoords),
                                                       elementMask=None,
                                                       elementTex=None,
                                                       colorSpace='rgb',
                                                       sizes=(check_size[0],check_size[1]));
                        stim.size = (check_size[0] * num_check,
                                     check_size[1] * num_check)

                        gridInfo = {};

                        for i in range(len(xyCoords)):
                            stim.opacities[i] = 0.0;
                            key = 'p' + str(i);
                            element = {key: {
                                        'image': None,
                                        'index': i,
                                        'xyCoords': None,
                                        'stim.xys': None,
                                        'opacity': 0.0,
                                        'clickCount':None}}
                            gridInfo.update(element);


                        for i in range(len(gridInfo)):
                            point_key = 'p' + str(i);
                            index = gridInfo[point_key]['index']
                            opacity = 0;
                            stim.opacities[index] = opacity;

                        DONE = False;

                    RESET_KEYS = event.getKeys('f')
                    if len(RESET_KEYS) > 0:
                        stim = visual.ElementArrayStim(win,
                                                       xys=xyCoords,
                                                       colors='yellow',
                                                       nElements=len(xyCoords),
                                                       elementMask=None,
                                                       elementTex=None,
                                                       colorSpace='rgb',
                                                       sizes=(check_size[0],check_size[1]));
                        stim.size = (check_size[0] * num_check,
                                     check_size[1] * num_check)
                        gridInfo = {};
                        for i in range(len(xyCoords)):
                            stim.opacities[i] = 0.0;
                            key = 'p' + str(i);
                            element = {key: {

                                                'index': i,
                                                'xyCoords': xyCoords[i],
                                                'stim.xys': stim.xys[i],
                                                'opacity': stim.opacities[i]}}

                            gridInfo.update(element);

                        message.opacity = 0;
                        clickCount_var = 0;
                        counter_var = 0;
                        win.flip()

                    if TASK_DONE == True:
                        print('...SHINE MAPPING TASK COMPLETE')
                        taskInfo['shineMapping']['taskCompleted']=True;

                        # WRITE
                        logFilePrefix = '_DATA_taskInfo.csv';
                        logFileName = logFileDir + studyIDPrefix + subjectID + logFilePrefix;
                        df = pd.DataFrame(taskInfo).T
                        df.to_csv(logFileName, index = True, header=True)
                        event.waitKeys()
                        break

            except:
                break

    except:
        break

print('...EXPERIMENT COMPLETE')

core.quit()
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
################################################################################

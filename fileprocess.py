#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Aug 30 11:01:46 2015
@authors: C-M Svensson and Anna Medyukhina
@email: carl-magnus.svensson@leibniz-hki.de or cmgsvensson@gmail.com

Copyright by Dr. Anna Medyukhina

Research Group Applied Systems Biology - Head: Prof. Dr. Marc Thilo Figge
https://www.leibniz-hki.de/en/applied-systems-biology.html
HKI-Center for Systems Biology of Infection
Leibniz Institute for Natural Product Research and Infection Biology -
Hans Knöll Insitute (HKI)
Adolf-Reichwein-Straße 23, 07745 Jena, Germany

License: BSD-3-Clause, see ./LICENSE or
https://opensource.org/licenses/BSD-3-Clause for full details
"""
import os, sys, re, json
from pathlib import Path

def get_args():
    '''
    Analyzes the input arguments and drops all the arguments before the script name.
    Returns the extracted arguments.
    '''
    args=[]
    isArgsStarted=False
    for i in range(len(sys.argv)):
        if isArgsStarted:
            args.append(sys.argv[i])
        else:
            parts=sys.argv[i].split('.')
            if parts[-1]=='py':
                isArgsStarted=True

    return args

def printUsage():
    print('Usage:\npython droplet_segmentation.py <input folder name> <output folder name> or')
    print('python droplet_segmentation.py <parameter_file> in the json format')
    return
        
def process_input_bg():
    '''
    Checks whether the input arguments are correct. Returns input and output folder names, and bg-path
    '''
    args=get_args()
    if len(args)<3:
        print('Not enough input arguments\n')
        printUsage()
        return 0
    if os.path.exists(args[0]):
        inputfolder=args[0]
        if not inputfolder[-1]=='/':
            inputfolder+='/'
    else:
        print('Input folder does not exist')
        printUsage()
        return [0,0]
    outputfolder=args[1]
    if not outputfolder[-1]=='/':
        outputfolder+='/'
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)    
    bgname = args[2]
    return [inputfolder, outputfolder, bgname]

def check_json_file(jf):
    if not 'inputfolder' in jf.keys():
        print('Json file have to specify inputfolder')
        return False
    else:
        jf['inputfolder'] = Path(jf['inputfolder'])
    if not 'outputfolder' in jf.keys():
        print('Json file have to specify outputfolder')
        return False
    else:
        jf['outputfolder'] = Path(jf['outputfolder'])
    
    return True
    
def process_input():
    '''
    Checks whether the input arguments are correct. Returns input and output folder names.
    '''
    args=get_args()
    if len(args) < 1:
        print('Not enough input arguments\n')
        printUsage()
        return 0
    if len(args) == 1:
        if not (Path(args[0]).suffix == '.json'):
            print('Single argument is not a json-file.')
            printUsage()
        else:
            with open(Path(args[0])) as json_file:
                parameters = json.load(json_file)
            check_json_file(parameters)
                
    else:
        inputfolder=Path(args[0])
        print(inputfolder)
        if not inputfolder.exists():    
            print('Input folder does not exist')
            printUsage()
            return [0,0]
        outputfolder=Path(args[1])
        if not outputfolder.exists():
            outputfolder.mkdir()    
        
        parameters = {'inputfolder': inputfolder,
                      'outputfolder': outputfolder} 
    return parameters
        
def process_input_file():
    '''
    Checks whether the input arguments are correct. Returns input and output folder names.
    '''
    args=get_args()
    if len(args)<3:
        print('Not enough input arguments\n')
        printUsage()
        return 0
    if os.path.exists(args[0]):
        imgfile=args[0]
    else:
        print('Image does not exist')
        printUsage()
        return [0,0]
    if os.path.exists(args[1]):
        inputfolder=args[1]
        if not inputfolder[-1]=='/':
            inputfolder+='/'
    else:
        print('Input folder does not exist')
        printUsage()
        return [0,0]
    outputfolder=args[2]
    if not outputfolder[-1]=='/':
        outputfolder+='/'
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)    
    return [imgfile, inputfolder, outputfolder]
    
def process_input_radius():
    '''
    Checks whether the input arguments are correct. Returns input and output folder names
    '''
    args=get_args()
    if len(args)<3:
        print('Not enough input arguments\n')
        printUsage()
        return 0
    if os.path.exists(args[0]):
        inputfolder=args[0]
        if not inputfolder[-1]=='/':
            inputfolder+='/'
    else:
        print('Input folder does not exist')
        printUsage()
        return [0,0]
    outputfolder=args[1]
    if not outputfolder[-1]=='/':
        outputfolder+='/'
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)
    radius = args[2]
    return [inputfolder, outputfolder, radius]

def sortkey(s):
    '''
        sorts files
    '''
    parts = re.split("(\d+)", s)
    parts[1::2] = map(int, parts[1::2])
    return parts


def list_image_files(inputfolder):
    '''
    lists image files in an input folder
    returns list of image files with paths to them
    '''
    global image_extenstions
    image_extensions=['png','jpg','jpeg','bmp','PNG','JPG','JPEG','BMP', 'tif', 
                     'TIF', 'tiff', 'TIFF']
    files = sorted(os.listdir(inputfolder), key = sortkey)
    files = inputfolder.glob('*')
    imgfiles=[]
    for i_file in files:
        extension=i_file.suffix
        if (str(extension)[1:] in image_extensions):
            imgfiles.append(i_file)
    return imgfiles


def list_image_files_recursive(inputfolder):
    '''
    lists image files in an input folder and all sub folders
    returns list of image files with paths to them
    '''
    global image_extenstions
    image_extensions=['png','jpg','jpeg','bmp','PNG','JPG','JPEG','BMP']
    files=sorted(os.listdir(inputfolder), key = sortkey)
    imgfiles=[]
    for i_file in files:
        if i_file.find(' ') > -1:               # ersetze leerzeichen durch unterstriche
            i_file2 = i_file.replace(' ', '_')
            os.rename(inputfolder+i_file, inputfolder+i_file2)
            i_file = i_file2
        if os.path.isdir(inputfolder+i_file) == True: # falls directory, rekursiver aufruf
            subfiles = list_image_files_recursive(inputfolder+i_file+'/')
            for i_subfile in subfiles:
                imgfiles.append(i_subfile)
        elif os.path.isfile(inputfolder+i_file) == True:
            parts=i_file.split(".")
            extension=parts[-1]
            if (extension in image_extensions):
                imgfiles.append(inputfolder+i_file)
    return imgfiles


def list_csv_files(inputfolder):
    '''
    lists csv files in an input folder
    returns list of csv files with paths to them
    '''
    global tab_extenstions
    tab_extensions=['csv']
    files=sorted(os.listdir(inputfolder), key = sortkey)
    csvfiles=[]
    for i_file in files:
        parts=i_file.split(".")
        extension=parts[-1]
        if (extension in tab_extensions):
            csvfiles.append(inputfolder+i_file)
    return csvfiles



def readfolders(inputfolder):
    """
    author: Stefanie Dietrich
    description: read all folders and their subfolders from a path
    input: path to folder 
    output: array with paths of all sub folders on lowest level
    """
    
    files = sorted(os.listdir(inputfolder), key=sortkey)
    folders = []
    for i_files in files:
        if i_files.find(' ') > -1:
            i_files2 = i_files.replace(' ','_')
            os.rename(inputfolder+i_files, inputfolder+i_files2)
            i_files = i_files2
        if os.path.isdir(inputfolder+i_files) == True:
            subfiles = readfolders(inputfolder+i_files+'/')#, allfolders)
            if len(subfiles) == 0:  # if no more subfolders, then current folder is lowest level  
                folders.append(inputfolder+i_files+'/') # save current folder
            else: # pass already found folders upward
                for i_subfile in subfiles:
                    folders.append(i_subfile)
            
    return folders
      

def matchImageNumberAndTable(folders, csvfiles, endung):

    csvNum = {}
    num = 0
    
    for i_csv in csvfiles:
        name = str.split(str.split(i_csv, '/')[-1], endung)[0]
        with open(i_csv) as f:
            lines = f.readlines()
        m = re.search(r"0[0-9]+$", str.split(lines[-1], ';')[0])
        csvNum[name] = int(m.group())

    for i_folder in folders:
        name = str.split(i_folder, '/')[-2]
        imageNum = len(list_image_files(i_folder))
        if imageNum-1 != csvNum[name]: 
            print("Keine Übereinstimmung:",name)
            print("Image number:" ,imageNum,"csv Number:", csvNum[name])
        else:
            num = num + 1

    return str(num*1./len(folders)*100)+"% image numbers matched csv result lines"
    






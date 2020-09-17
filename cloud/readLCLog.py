#
# read LCwrapper log
# CourcewareHub version
#
# 2019/6/12
# kuwata@mmm.muroran-it.ac.jp
#

import re
import pandas as pd
import datetime

'''
read xxx.log file format , return df
'''
def readlogFiles(files):
    l = []
    for log in files:
        logtext = readlogFile(log)
        if (len(logtext) > 1):
            l.append(logtext)
            df= pd.DataFrame(l, columns=['user','cell_name','program_code', 'path_logfile', 'file_name', 'lc_notebook_meme', 'server_signature', 'uid', 'gid','start_time', 'output', 'end_time', 'results', 'error'])
    df.replace('None', pd.np.nan, inplace=True) # replace 'None' -> NoN
    return df


'''
read xxx.log file format , return list of reading text
'''
def readlogFile(file):
    pat = re.compile(r'.*(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)') # date & time encoder
    f = open(file, 'r')
    state = 0
    # us = re.search(r'\/home\/(.*?)\/',file) # extract user name
    # Courceware teacher only
    user = re.search(r'\/home\/jupyter\/workspace\/(.*?)\/',file) # extract user name (actually, name of home folder)
    loglist = [user.group(1)]
    command = ""
    output = ""
    result = ""
    for line in f:
        if re.search(r'----', line): # identify separator
            state += 1
            line = "" # delete
            if state == 2:
                loglist.append(command) # flash before next state
                continue
            if state == 4:
                loglist.append(output) # flash before next state
                continue
            
        if state == 0:
            m = re.search(r'{\"lc_cell_meme\": {\"current\": \"(.*)\"}}', line)
            if m:
                loglist.append(m.group(1)) # cell name
            else:
                return []  # error 'no uuid'
                
        if state == 1:
            command += line # add command line
            
        if state == 2:
            m = re.search(r'^path:(.*)', line)
            if m:
                loglist.append(m.group(1)) # path
            m = re.search(r'^notebook_path:(.*)', line)
            if m:
                loglist.append(m.group(1)) # notebook_path
            m = re.search(r'^lc_notebook_meme:(.*)', line)
            if m:
                loglist.append(m.group(1)) # lc_notebook_meme
            m = re.search(r'^server_signature:(.*)', line)
            if m:
                loglist.append(m.group(1)) # server_signature
            m = re.search(r'^uid:(.*)', line)
            if m:
                loglist.append(m.group(1)) # uid
            m = re.search(r'^gid:(.*)', line)
            if m:
                loglist.append(m.group(1)) # gid
            m = re.search(r'^start time:(.*)', line)
            if m:
                date_text = pat.search(m.group(1))
                start = datetime.datetime.strptime(date_text.group(1), '%Y-%m-%d %H:%M:%S') # decode date&time
                loglist.append(start) # start time
                
        if state == 3:
            output += line # add output
            
        if state == 4:
            m = re.search(r'^end time:(.*)', line)
            if m:
                date_text = pat.search(m.group(1)) 
                end = datetime.datetime.strptime(date_text.group(1), '%Y-%m-%d %H:%M:%S') # decode date&time
                loglist.append(end) # end time
            m = re.search(r'0 chunks with matched keywords or errors', line)
            if m:
                continue # ignore
            
        if state == 5:
            m = re.search(r'result:[\s*](.*)', line)
            if m:
                result = m.group(1) # result (path to output file)
                
    if state == 5:
        loglist.append(result)
        if (len(result) > 0): # if an output file exists
            # Courceware teacher only
            # rewrite path to file '/home/*' --> '/home/jupyter/workspace/*'
            resultpath = re.sub(r'/home/(.*)', r'/home/jupyter/workspace/\1', result)
            error = readResults(resultpath)
        else:
            error = 'None'
        loglist.append(error)
        
    return loglist


'''
read output file
'''
def readResults(file):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]') # fuzzy way to strip ANSI Escape sequences

    d = open(file, 'r',errors='ignore')
    error = ''
    for line in d:
        linestrip = ansi_escape.sub('', line)
        m = re.search(r'[Ee]rror:', linestrip)
        if m:
            error += linestrip.strip('\n')
    if (len(error) == 0):
        error = 'None'
    return error

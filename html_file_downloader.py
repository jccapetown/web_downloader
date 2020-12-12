#!/usr/bin/python
#Author: Jacques Coetzee
#www.jacquescoetzee.co.za
#Description:
#This tool allows you to give a webpage that contains download links to files and will automatically download thos files for you.
#It is proxy ready

import urllib, urllib.request, urllib.parse
import getpass
import sys, os
import re
from filesize import size



mainurl = input('Url to scan for downloadable files?: ')
if mainurl[-1] != '/':
    mainurl = '%s%s' % (mainurl , '/')
response = urllib.request.urlopen(mainurl).read().decode('utf-8')
#search response for files
#print response

print('Finding files....')
flags = re.I
#urls = re.findall(r'href=[\'"]?([^\'">]+)', response, flags)
urls = re.findall(r'href=[\"]?([^\">]+)', response, flags)

located_files = {}

#print "\n ".join(urls)

print ('Extracting files')
for url in urls:
    file_name = url.split('/')[-1]
    if '.' in file_name:
        ext = file_name.split('.')[-1]
        if len(ext) > 4:
            continue
        if ext not in located_files:
            located_files[ext] = []
        #print 'adding', url
        located_files[ext].append(url)


for ix,ext in enumerate(located_files):
    print('  %s.%s - %s Files Found' % (str(ix+1), ext, len(located_files[ext]) )    )

userext = 'NONE'
while not userext.lower() in located_files:
    if userext == 'NONE':
        userext = input('Which extension files do you want to download?: eg. txt :')
    else:
        userext = input('Did not find extension. Try Again: eg. txt :')
    if userext.lower() == 'exit':
        print('cheers!')
        sys.exit()


#Lets parse this response
Totalrecords = len(located_files[userext])
print("Found %s files" % Totalrecords)
        
lastcompletion = 0
for ix,file_url in enumerate(located_files[userext]):
    try:
        splitfile = False
        if '/' in file_url:
            splitfile = True
            
        file_name = file_url.split('/')[-1]
        
        if not splitfile:
            filedownload = '%s%s' % (mainurl, file_url)
        else:
            filedownload = '%s%s' % (mainurl, file_name)
        if 'ftp://' in file_url.lower():
            filedownload = file_url
        if '.com/' in file_url.lower():
            filedownload = file_url

        
        filedownload = urllib.parse.quote(filedownload)
        filedownload = filedownload.replace('%7', '~')
        filedownload = filedownload.replace('%2528', '(')
        filedownload = filedownload.replace('%2529', ')')
        filedownload = filedownload.replace('%3A', ':')
        filedownload = filedownload.replace('%255B', '[')
        filedownload = filedownload.replace('%255D', ']')
        filedownload = filedownload.replace('%2520', '%20')
        

        #print "Fetching: %s.%s" % (str(ix+1),file_name)

        
        
        u = urllib.request.urlopen(filedownload)

        decodename = urllib.parse.unquote(file_name)
        #print decodename
        
        if os.path.exists(decodename):
            print('  File %s exists... skipping' % decodename)
            continue
        f = open(decodename , 'wb')
        meta = u.info()
        file_size = int(meta.get("Content-Length"))
        #print ix+1, 'of',Totalrecords, " - Downloading: %s Bytes: %s" % (decodename, file_size)
        print('  Downloading ' + str(ix+1) + ' of ' + str(Totalrecords) + " - %s Bytes: %s" % (decodename, size(file_size)))
        file_size_dl = 0
        block_sz = 8192
        current_interval_size = 0
        while True:
            buffer = u.read(block_sz)
            current_interval_size += 1
            if not buffer:
                break
           
            
            file_size_dl += len(buffer)
            f.write(buffer)
            
            if current_interval_size == 128*10:
              print('   -> Downloaded %s of %s' % (size(file_size_dl), size(file_size)))
              current_interval_size = 0
              #printProgressBar('Downloaded %s of %s' % (size(file_size_dl), size(file_size)))


        f.close()
        #raw_input('next')
    except Exception as e:
        print(filedownload, "Exception: %s" % e)

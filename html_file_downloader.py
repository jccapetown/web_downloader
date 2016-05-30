#!/usr/bin/python
#Author: Jacques Coetzee
#www.jacquescoetzee.co.za
#Description:
#This tool allows you to give a webpage that contains download links to files and will automatically download thos files for you.
#It is proxy ready

import urllib2, urllib, getpass
import sys, os
import re
import ConfigParser



#if you use a proxy
if not os.path.exists('proxy.conf'):
    useproxy = raw_input('Do you use a proxy?: ')
    if useproxy.lower() in ['yes', 'y']:
        host = raw_input('Proxy host: ')
        port = raw_input('Proxy port: ')

        needauth = raw_input('Does the proxy require authentication?: ')
        if needauth.lower() in ['yes','y']:
            user = raw_input('Proxy user: ')
            password = getpass.getpass('Proxy Password?: ')
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@%s:%s' % (user, password, host, port)})
        
        else:
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s' % (host, port)})
        
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
else:
    config = ConfigParser.ConfigParser()
    config.read('proxy.conf')
    enabled = config.get('proxy', 'enabled')
    host = config.get('proxy', 'host')
    port = config.get('proxy', 'port')
    useauth = config.get('proxy', 'useauth')
    user = config.get('proxy', 'user')
    if enabled in ['y','Y']:
        if useauth in ['y', 'Y']:
            password = getpass.getpass('Proxy Password?: ')
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@%s:%s' % (user, password, host, port)})
        else:
            proxy = urllib2.ProxyHandler({'http': 'http://%s:%s' % (host, port)})
                    
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        


mainurl = raw_input('Url to scan for downloadable files?: ')
if mainurl[-1] != '/':
    mainurl = '%s%s' % (mainurl , '/')
response = urllib2.urlopen(mainurl).read()
#search response for files
#print response

print 'Finding files....'
flags = re.I
#urls = re.findall(r'href=[\'"]?([^\'">]+)', response, flags)
urls = re.findall(r'href=[\"]?([^\">]+)', response, flags)

located_files = {}

#print "\n ".join(urls)

print 'Extracting files'
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
    print '  %s.%s - %s Files Found' % (str(ix+1), ext, len(located_files[ext]) )    

userext = 'NONE'
while not userext.lower() in located_files:
    if userext == 'NONE':
        userext = raw_input('Which extension files do you want to download?: eg. txt :')
    else:
        userext = raw_input('Did not find extension. Try Again: eg. txt :')
    if userext.lower() == 'exit':
        print 'cheers!'
        sys.exit()


#Lets parse this response
Totalrecords = len(located_files[userext])
print "Found %s files" % Totalrecords
        
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

        
        filedownload = urllib.quote(filedownload)
        filedownload = filedownload.replace('%7', '~')
        filedownload = filedownload.replace('%2528', '(')
        filedownload = filedownload.replace('%2529', ')')
        filedownload = filedownload.replace('%3A', ':')
        filedownload = filedownload.replace('%255B', '[')
        filedownload = filedownload.replace('%255D', ']')
        filedownload = filedownload.replace('%2520', '%20')
        

        #print "Fetching: %s.%s" % (str(ix+1),file_name)

        
        
        u = urllib2.urlopen(filedownload)

        decodename = urllib2.unquote(file_name)
        #print decodename
        
        if os.path.exists(decodename):
            print '  File %s exists... skipping' % decodename
            continue
        f = open(decodename , 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        #print ix+1, 'of',Totalrecords, " - Downloading: %s Bytes: %s" % (decodename, file_size)
        print 'Downloading ' + str(ix+1) + ' of ' + str(Totalrecords) + " - %s Bytes: %s" % (decodename, file_size)
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            completion = round(file_size_dl * 100. / file_size)
            
            if round(completion) % 20 == 0:
                if completion != lastcompletion:
                    status = "  %s completed \n" % (completion)
                    print status,
                    lastcompletion = completion

        f.close()
        #raw_input('next')
    except Exception, e:
        print filedownload, "Exception: %s" % e

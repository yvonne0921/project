# coding=utf-8
disk_path = '/Users/SungChihSu/Documents/Group1'
baseurl = 'https://graph.facebook.com/v2.4/'
#access_token = '1595407670713448|4995fb85f3133d83e407f5bf36a34a7b'
access_token = 'CAAWrA8t8HGgBAJ3G7oFbHtK8VsglgpdG9uYtNuJ8ZBwtHRqcpz5R1vkGz20wDFZAYphU8zTpmy6wXhXP99HWbFZAQMyczjJ4T6wZA2HuObMuqYnB2HsDrdcIMvtMyaAlqmxeoFwA5kARTibPOWIlYZA8To4huFOZAkQzHgxdeifzkE80HQZBUTPnZBbUBwuLckg79VVPBO7DCgZDZD'
import requests
import json
import os
import re
import easygui
import datetime
import time
import urllib2
import sys
#創專案資料夾
def createProject():
    if not os.path.exists(disk_path):
        os.makedirs(disk_path)
    if not os.path.exists(disk_path + '/pic'):
        os.makedirs(disk_path + '/pic')
    if not os.path.exists(disk_path + '/comments'):
        os.makedirs(disk_path + '/comments')
    if not os.path.exists(disk_path + '/message'):
        os.makedirs(disk_path + '/message')
    if not os.path.exists(disk_path + '/link'):
        os.makedirs(disk_path + '/link')

#將fanpages的粉絲團連結轉成粉絲團ID
def getFBid(url):
    url = url.replace('www','graph').replace('pages/','')
    url_tmp1 = re.search('([?])([\d\w\W]+)',url)
    url_tmp2 = re.search('(com)(/)([\d\w\W]+)(/)',url)
    if url_tmp1:
        url = url.replace(url_tmp1.group(1) + url_tmp1.group(2),'')
    if url_tmp2:
        url = url.replace(url_tmp2.group(2) +url_tmp2.group(3),'')
    url +=  '?access_token=' + access_token    
    res = requests.get(url)
    data = res.json()
    return data['id']

#抓取json(一開始查詢的連接)
def url_res(url):
    header = {'Authorization':'Bearer {}'.format(access_token)}
    res = requests.get(url,headers = header)
    data = res.json()
    return data['posts']

#讀取json(next的連接)
def url_res_noposts(url):
    header = {'Authorization':'Bearer {}'.format(access_token)}
    res = requests.get(url,headers = header)
    data = res.json()
    return data

#判斷是否還有下一頁
def nextfrompage(data):    
    if 'paging' not in data:
        return False
    else:
        return True

#抓取下一頁連接
def nexturl(data):
    data = data['paging']
    return data['next']
# The progress bar
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()
#下載圖並回傳儲存大小
def download(file_path,file_size,u):
    f = open(file_path,'wb')
    file_size_dl = 0
    block_sz = 8192
    while True:
        bufferInMemory = u.read(block_sz)
        if not bufferInMemory:
            break
        file_size_dl += len(bufferInMemory)
        f.write(bufferInMemory)
        progress(file_size_dl, file_size, suffix='_')
    f.close()
    statinfo =os.stat(file_path)

    return statinfo.st_size


#抓取picture
def picture(data,fbid):
    #作業中的資料夾尾端加上(working)，以方便確認進度
    if not os.path.exists(disk_path + '/pic/' + fbid):
        if not os.path.exists(disk_path + '/pic/' + fbid + '(working)'):
            os.makedirs(disk_path + '/pic/' + fbid + '(working)')
    try:
        for data in data['data']:
            if 'full_picture' in data:
                pic_url = data['full_picture']
                filename = data['id']
                m = re.search('(?P<picname>[\d_]+)',filename)
                if m:
                    picname = m.group('picname')
                    file_name = '/{}.jpg'.format(picname)
                    
                    u = urllib2.urlopen(pic_url)
                    meta = u.info()
                    file_size = int(meta.getheaders("Content-Length")[0])
                    goodFile=True
                    file_path=disk_path + '/pic/' + fbid + '(working)' + file_name;
    
                    if file_size==0:
                        u = urllib2.urlopen(pic_url)
                        meta = u.info()
                        file_size = int(meta.getheaders("Content-Length")[0])
                        if file_size ==0:
                            goodFile=False
                            log=open(disk_path+'error.log',"a")
                            log.write(datetime.datetime.now())
                            log.write(' '+file_path+': Responsed file size is error.\r\n')
                            log.close()
                            
                    if goodFile==True:   
                        print "Downloading: %s Bytes: %s\r\n" % (file_name, file_size)
                        if download(file_path,file_size,u)!=file_size:
                            u = urllib2.urlopen(pic_url)
                            print "Wrong Size, download it again!"
                            if download(file_path,file_path,file_size,u)!=file_size:
                                print "Wrong file or missing"
                                log=open(disk_path+'error.log',"a")
                                log.write(datetime.datetime.now())
                                log.write(' '+file_path+': Downloaded size is error.\r\n')
                                log.close()
    except:
        print "fail to load data, excute picture again"
        log=open(disk_path+'error.log',"a")
        log.write(datetime.datetime.now())
        log.write('loading'+fbid+'is error.\r\n')
        log.close()

#抓取PO文
def message(data,fbid):
    #作業中的資料夾尾端加上(working)，以方便確認進度
    if not os.path.exists(disk_path + '/message/' + fbid):
        if not os.path.exists(disk_path + '/message/' + fbid + '(working)'):
            os.makedirs(disk_path + '/message/' + fbid + '(working)')
    
    for data in data['data']:
        if 'full_picture' in data:
            if 'message' in data:               
                message = data['message']
                filename = data['id']
                m = re.search('(?P<messname>[\d_]+)',filename)
                if m:
                    messname = m.group('messname')
                messf = open(disk_path + '/message/' + fbid + '(working)' + '/{}.txt'.format(messname),'w')
                messf.write(message.encode('utf8'))   
                messf.close()
        
#抓取PO文link
def link(data,fbid):
    #作業中的資料夾尾端加上(working)，以方便確認進度
    if not os.path.exists(disk_path + '/link/' + fbid):
        if not os.path.exists(disk_path + '/link/' + fbid + '(working)'):
            os.makedirs(disk_path + '/link/' + fbid + '(working)')
   
    for data in data['data']:
        if 'full_picture' in data:
            if 'message' in data:
                messtime = data['created_time']
                messlink = data['link']
                filename = data['id']
                m = re.search('(?P<messname>[\d_]+)',filename)
                if m:
                    messname = m.group('messname')
                linkf = open(disk_path + '/link/' + fbid + '(working)' + '/{}.txt'.format(messname),'w')
                linkf.write(messlink.encode('utf8') + '\n' + messtime.encode('utf8'))
                linkf.close()

#抓取評論
def comments(data,fbid):
    #作業中的資料夾尾端加上(working)，以方便確認進度
    if not os.path.exists(disk_path + '/comments/' + fbid):
        if not os.path.exists(disk_path + '/comments/' + fbid + '(working)'):
            os.makedirs(disk_path + '/comments/' + fbid + '(working)')
   
    for ele in data['data']:
        if 'full_picture' in ele:
            commlist = []
            if 'comments' in ele:
                filename = ele['id']
                for data in ele['comments']['data']:
                    message = data['message']
                    m = re.search('(?P<commname>[\d_]+)',filename)
                    commlist.append(data['created_time'].encode('utf8') + '\n' + data['from']['id'].encode('utf8') + '\n' + data['message'].encode('utf8') + '\n' + '=================================================' + '\n')
                    if m:
                        commname = m.group('commname')
                commf = open(disk_path + '/comments/' + fbid + '(working)' + '/{}.txt'.format(commname),'w')
                for ele in commlist:
                    commf.write(ele)   
                commf.close()

#主程式
def main():
    #創建專案資料夾
    createProject()
    start = str(datetime.datetime.now())    
   
    #取得粉絲團連結
    f = open(disk_path + '/fanpages.txt','r')
    while(True):
        fanpage_link = f.readline().strip('\r\n').strip('\n')
        if fanpage_link == '':            
            break
        else:
            #取得粉絲團ID
            fbid = getFBid(fanpage_link)

            #設定連結
            res_url = baseurl + fbid + '?fields=id,posts{full_picture,message,likes{name},created_time,link}'
            comm_url = baseurl + fbid + '?fields=posts{full_picture,comments}'    
            data = url_res(res_url)
            comm_data = url_res(comm_url)

            while(True):
                #抓取圖片、PO文、回覆和PO文連結
                if 'data' in data.keys():
                    picture(data,fbid)
                    message(data,fbid)
                    link(data,fbid)
                    comments(comm_data,fbid)
                else:
                    print "fail to load data, excute picture again"
                    log=open(disk_path+'error.log',"a")
                    log.write(datetime.datetime.now())
                    log.write('loading'+fbid+'is error.\r\n')
                    log.close()
                    

                #判斷comments是否還有下一頁，有的話抓取下一頁連接 
                while(nextfrompage(comm_data)):
                    comm_next_url = nexturl(comm_data)
                    comm_data = url_res_noposts(comm_next_url)
                    comments(comm_data,fbid)                        

                #判斷message是否還有下一頁，有的話抓取下一頁連接
                if(nextfrompage(data)):             
                    normal_next_url = nexturl(data)
                    data = url_res_noposts(normal_next_url)
                else:
                    break

            #休息5秒
            time.sleep(5)

            #完成下載後，更改資料夾檔名
            os.rename(disk_path + '/pic/' + fbid + '(working)',disk_path + '/pic/' + fbid)
            os.rename(disk_path + '/message/' + fbid + '(working)',disk_path + '/message/' + fbid)
            os.rename(disk_path + '/comments/' + fbid + '(working)',disk_path + '/comments/' + fbid)
            os.rename(disk_path + '/link/' + fbid + '(working)',disk_path + '/link/' + fbid)
    
    f.close()
    easygui.msgbox('Starting : ' + start + '\nEnding : ' + str(datetime.datetime.now()), title='作業結束')
                
if __name__ == '__main__':
    main()
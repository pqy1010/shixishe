from requests_html import HTMLSession
import json
import sqlite3
import sqlalchemy
import time

import logging


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='./my.log', level=logging.DEBUG, format=LOG_FORMAT)
session=HTMLSession()



#获取配置
with open('caiji.config','r') as f:
    configjson=f.read()
configdict=json.loads(configjson)

with open('time.config','r') as f:
    timejson=f.read()
timedict=json.loads(timejson)




con=sqlite3.connect('../instance/flaskr.db')
creatvideosql='''CREATE TABLE video (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  img TEXT,
  jishu TEXT,
  othername TEXT,
  director TEXT,
  actor TEXT,
  genre TEXT,
  region TEXT,
  language TEXT,
  screen TEXT,
  mlen TEXT,
  updatet TEXT,
  clicknum TEXT,
  todayclicknum TEXT,
  score TEXT,
  scorenum TEXT,
  introduction TEXT,
  yun1 TEXT,
  m3u8 TEXT,
  download TEXT,
  platform TEXT,
  other TEXT,
  other1 TEXT,
  other2 TEXT,
  other3 TEXT,
  permituid TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);'''

c=con.cursor()
tablelist=c.execute("select * from sqlite_master where type = 'table' and name = 'video'").fetchall()
if not tablelist:
    c.execute(creatvideosql)
    con.commit()


def insertdb(c,jsondata):#将json文件插入数据库
    columnname=''
    values=""
    para=[]
    for key,vals in jsondata.items():
        columnname+=(key+',')
        values+='?,'
        if isinstance(vals, dict):
            tempvals=json.dumps(vals)
            para.append(tempvals)
        else:
            para.append(jsondata[key])

    columnname+='author_id'
    values+='?'
    para.append(1)
    tempsql='INSERT INTO video (%s) VALUES (%s)'%(columnname,values)
    c.execute(tempsql,para)



ignortime=0


updatelist=[]
savepath='./data/'
for keyset,valset in configdict.items():
    pagenum=1
    url_av=[]

    url=keyset
    logging.info('processing '+url)
    
    stopflag=1
    righttime=None
    deadline=float(timedict[url]['deadline'])# 提取截至日期
    while(stopflag):
        try :
            r=session.get(url)
        except:
            logging.warning(url+'not response')
            continue
        
        if righttime == None:
            righttime=time.time()
            logging.info('processing time is '+str(righttime))
            timedict[keyset]['deadline']=str(righttime)
            json.dump(timedict, open('time.config', "w"))

        urllist=r.html.links#获取所有链接
        for temp in urllist:#寻找详情页的url列表
            if configdict[keyset]['useful_url'] in temp:
                url_av.append(temp)

        for suburl in url_av:#电影详情页
            try:
                ph=session.get(keyset+suburl)
            except:
                logging.warning(keyset+suburl+'not response')
                continue
            moviedict={}#一条数据信息
            moviedict["platform"]=keyset
            for info,rule in configdict[keyset]['target_xpath'].items():#获取当前电影的详细信息
                if info =="img":
                    if(ph.html.xpath(rule)):
                        moviedict[info]=ph.html.xpath(rule)[0]
                    else:
                        moviedict[info]=''
                elif info =="m3u8" or info=="yun1" or info == "download":
                    moviedict[info]={}
                    for subset in ph.html.xpath(rule):
                        sep=subset.text.find('$')
                        if sep:
                            subsetlabel=subset.text[:sep]
                            subseturl=subset.text[sep+1:]
                            moviedict[info][subsetlabel]=subseturl
                        else:
                            moviedict[info][subsetlabel]=subset
                elif info=="name":
                    tempname=ph.html.xpath(rule)[0].text
                    tempname=tempname.split(' ')
                    moviedict[info]=tempname[0]

                else:
                    if(ph.html.xpath(rule)):
                        moviedict[info]=ph.html.xpath(rule)[0].text
                    else:
                        moviedict[info]=''
            updatelist.append(moviedict)
            sqlres=c.execute("SELECT id,platform,screen FROM video WHERE name=?",[moviedict['name']]).fetchall()
            if(not sqlres):
                insertdb(c,moviedict)
                logging.info(moviedict['name']+'insert int db success')
                con.commit()
            else:
                logging.info(moviedict['name']+'insert int db faile')
            updatet=time.mktime(time.strptime(moviedict['updatet'],"%Y-%m-%d %H:%M:%S"))
            if updatet<deadline :
                if ignortime==1:
                    logging.info('spyder whole web data')
                stopflag=0
                break
        #next page
        if(0):
            pagenum+=1
            url=keyset+configdict[keyset]['nextpage']%pagenum
        try:
            alinklist=r.html.xpath("//a[@href]")
        except:
            logging.warning(url+'get a links faile.')
            break
        url=None
        for tempa in alinklist:
            if tempa.text=="下一页":
                url=keyset[0:-1]+tempa.attrs['href']
        if url==None:
            logging.info(configdict[keyset]+'has no next page')
            break





'''
for tempdata in updatelist:
    sqlres=c.execute("SELECT id,platform,screen FROM video WHERE name=?",[tempdata['name']]).fetchall()
    if(not sqlres):
        insertdb(c,tempdata)
'''
con.commit()
con.close()
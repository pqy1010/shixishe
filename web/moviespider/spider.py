from requests_html import HTMLSession
import json
import os
import time
from requests_html import HTML
import pandas
import csv
import sqlite3
#from ..boss.movie import insertfromspider


class WebMovie():
    urllists=[]
    movieclass=['剧情','喜剧','动作','爱情','科幻','动画','悬疑','惊悚','恐怖','犯罪','同性','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠','情色','av']
    znfield=['名称','更新','封面','描述','别名','状态', '时间', '主演', '导演', '类型', '扩展', '地区', '年份', '语言', '集数', '时长', '点击']
    enfiled=['moviename','updatetime','movieimg','moviedescrib','othername','moviestatus','movieborntime','actor','director','movieclass','classextant','country','year','lang','episodr','movielen','click']
    def __init__(self):
        self.urllists=[]
        with open('url.txt','r') as f:
            self.urllists.append(f.read())
        for root, dirs, files in os.walk(".", topdown=False):
            if 'rrzy_startdate.tim' in files:
                self.rrzy_state='update'
            else:
                self.rrzy_state='all'
        
    def get_rrzy(self,url,rrzy_state):#获取rrzy的电影目录和链接
        if rrzy_state=='update':
            with open('rrzy_startdate.tim','r') as f:
                startdate=float(f.read())
                savedate=None
        elif rrzy_state=='all':
            startdate=None
        else:
            startdate=None
        movielist={}
        spiderflag=True
        count=0
        session = HTMLSession()
        print('geting web')
        absoluteurl=url
        while(spiderflag and absoluteurl!=None):
            
            r=session.get(absoluteurl)
            print('get web %s'%absoluteurl)
            for li in (r.html.xpath("//li[@class='clearfix']")):#li laber
                movieinfo={}
                count+=1
                try:
                    #获取电影列表
                    lihtml=HTML(html=li.html)
                    a_ele=lihtml.xpath("//h3//a")[0]
                    moviename=a_ele.attrs['title']
                    movielink=a_ele.attrs['href']
                    
                    movieinfo['moviename']=moviename#保存电影名称
                    updatetime=lihtml.xpath("//span[@class='time']")[0].text
                    movieinfo['updatetime']=time.mktime(time.strptime(updatetime,"%Y-%m-%d %H:%M:%S"))#保存上传时间戳
                    if savedate==None:
                        print('update savedate')
                        savedate=movieinfo['updatetime']
                    if startdate!=None and movieinfo['updatetime']<=startdate:
                        print('save savedate')
                        with open('rrzy_startdate.tim','w') as f:
                            f.write(str(savedate))
                            spiderflag=False
                            continue
                    #获取电影详情
                    moviepage=session.get(url+movielink)
                    movieimageurl=moviepage.html.xpath("//a[@class='copy_btn text-muted']")[0].attrs['data-text']
                    movieinfo['movieimg']=movieimageurl#封面

                    movieinfo['moviedescrib']=moviepage.html.xpath("//div[@class='stui-content__desc col-pd clearfix']")[0].text

                    for movestate in moviepage.html.xpath("//p[@class='data hidden-xs']|//p[@class='data']"):
                        for i in movestate.text.split(' '):
                            sep=i.find('：')
                            if sep<=1:
                                continue
                            if i[:sep] in self.znfield:
                                index=self.znfield.index(i[:sep])
                                movieinfo[self.enfiled[index]]=i[sep+1:]
                            else:
                                movieinfo[i[:sep+1]]=i[sep+1:]


                    movieinfo['links']={}
                    for subset in moviepage.html.xpath("//a[@class='copy_text']"):
                        sep=subset.text.find('$')
                        subsetlabel=subset.text[:sep]
                        subseturl=subset.text[sep+1:]
                        movieinfo['links'][subsetlabel]=subseturl
                except:
                    print('some error')
                    spiderflag=False
                    continue
                movielist[str(count)]=movieinfo
                del movieinfo
        
            #寻找下一页
            stui_page=r.html.xpath("//ul[@class='stui-page text-center clearfix']//li")
            absoluteurl=None
            for pageli in stui_page:
                if pageli.text=='下一页':
                    absoluteurl=url+HTML(html=pageli.html).links.pop()#获取下一页，set集合
        #存储数据
        savedata=json.dumps(movielist)
        with open('rrxy'+time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())+'.json','+w') as f:
            f.write(savedata)





    def spiderrun(self):
        for url in self.urllists:
            if 'www.rrzy.cc' in url:
                print('begain get data')
                self.get_rrzy(url,self.rrzy_state)





class uptoflask():
    def __init__(self,mode=1):
        #moviename,updatetime,movieimg,moviedescrib,othername,moviestatus,movieborntime,actor,director,movieclass,classextant,country,year,lang,episodr,movielen,click,links
        self.znfield=['名称','更新','封面','描述','别名','状态', '时间', '主演', '导演', '类型', '扩展', '地区', '年份', '语言', '集数', '时长', '点击']
        self.enfield=['moviename','updatetime','moviedescrib','movieimg','othername','moviestatus','movieborntime','actor','director','movieclass','classextant','country','year','lang','episodr','movielen','click']
        self.insertfield='moviename,updatetime,movieimg,moviedescrib,othername,moviestatus,movieborntime,actor,director,movieclass,classextant,country,year,lang,episodr,movielen,click,links,author_id'
        self.dbpath='../instance/flaskr.sqlite'
        #self.dbpath='./test.sqlite'
        self.mode=mode
        self.jsonfilelist=[]
        for root, dirs, files in os.walk(".", topdown=False):
            for temp in files:
                if os.path.splitext(temp)[1]=='.json':
                    self.jsonfilelist.append(temp)
            
        
    

    def insertdb(self,jsondata):#将json文件插入数据库
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
        print(tempsql)
        self.con.execute(tempsql,para)


    def readdata(self):#读取json数据
        self.jsondata={}
        if len(self.jsonfilelist)==0:
            return
        for tempfile in self.jsonfilelist:
            with open(tempfile,'r') as f:
                jsontxt=f.read()
            jsondata=json.loads(jsontxt)
            self.jsondata.update(jsondata)
            #os.remove(tempfile)

    def run(self):
        self.readdata()
        if self.mode==1:
            self.con=sqlite3.connect(self.dbpath)
        for data in self.jsondata.values():
            self.insertdb(data)
        self.con.commit()
        self.con.close()

#['id','author_id','更新时间','影片名称','电影简介','电影封面','别名','状态', '时间','扩展','年份', '语言','集数', '点击','主演', '类型','地区', '评分','链接','时长', '导演']
    def creattablesql(self):
        creatsql='''CREATE TABLE video (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER NOT NULL,

                updatetime TEXT,
                moviename TEXT NOT NULL,
                moviedescrib TEXT,
                movieimg TEXT,
                othername TEXT,
                moviestatus TEXT,
                movieborntime TEXT,
                classextant TEXT,
                year TEXT,
                lang TEXT,
                episodr TEXT,
                click TEXT,
                actor TEXT,
                movieclass TEXT,
                country TEXT,
                score TEXT,
                links TEXT,
                movielen INTEGER,
                director TEXT,
                other TEXT,
                other1 TEXT,
                other2 TEXT,
                other3 TEXT,
                permituid TEXT,
                FOREIGN KEY (author_id) REFERENCES user (id)
                )'''
        if self.mode==1:
            self.con=sqlite3.connect(self.dbpath)

        tablelist=self.con.execute("select * from sqlite_master where type = 'table' and name = 'video'").fetchall()
        if len(tablelist)==0:
            self.con.execute(creatsql)

        self.con.commit()





if __name__ == "__main__":
    print(os.getcwd())
    spider=WebMovie()
    spider.spiderrun()#爬取数据并存储文件
    flaskmovie=uptoflask(mode=1)
    flaskmovie.run()








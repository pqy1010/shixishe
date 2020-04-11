from boss.db import get_db
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for,current_app
import json


bp = Blueprint('movie', __name__, url_prefix='/movie')

#movieclass=['全部','剧情','喜剧','动作','爱情','科幻','动画','悬疑','惊悚','恐怖','犯罪','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠']
movieclass={'1':'全部','2':'剧情','3':'喜剧','4':'动作','5':'爱情','6':'科幻','7':'动画','8':'悬疑','9':'惊悚','10':'恐怖','11':'犯罪','12':'音乐','13':'歌舞','14':'传记','15':'历史',
'16':'战争','17':'西部','18':'奇幻','19':'冒险','20':'灾难','21':'武侠'}
@bp.route('/insertfromspider',methods=('GET','POST'))
def insertfromspider():#将爬虫传送过来的数据存入数据库
    db = get_db()
    moviestr=''
    
    if request.method=='POST':
        jsondata= json.loads(request.get_data(as_text=True))


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
        para.append(session['user_id'])
        tempsql='INSERT INTO video (%s) VALUES (%s)'%(columnname,values)
        db.con.execute(tempsql,para)
    return 'insert done'



#insertfield='name,updatet,img,introduction,othername,moviestatus,screen,actor,director,movieclass,genre,region,year,lang,episodr,movielen,click,links,author_id'
@bp.route('/movielist/',methods=('GET','POST'))
@bp.route('/movielist/<int:cmd>/<int:page>',methods=('GET','POST'))
def movielist(cmd=1,page=1):#电影列表主页

    db=get_db()
    posts={}
    pagecount_def=12
    if request.method=='POST' or request.method=='GET':
        jsonstr=request.get_data(as_text=True)
        print(jsonstr)
        query=''
        if len(jsonstr)==0:
            print('no jsondata')
            jsondata={'pagenum':page,'pagecount':pagecount_def}
        else:
            jsondata= json.loads(jsonstr)       
            for key,vals in jsondata.items():
                if vals !='' and key !='pagenum' and key != 'pagecount':
                    if len(query)==0:
                        query='%s=%s'%(key,vals)
                    else:
                        query+='and %s=%s'%(key,vals)
            
            offset=(jsondata['pagenum']-1)*jsondata['pagecount']

        if len(query)==0:
            searchsql='SELECT id,name, updatet, img, introduction,genre,screen,region from video ORDER BY id DESC limit %d offset %d'%(
                jsondata['pagecount'],jsondata['pagenum'])
        else:
            searchsql='SELECT id,name, updatet, img, introduction,genre,screen,region from video WHERE %s ORDER BY id DESC limit %d offset %d'%(
                query,jsondata['pagecount'],jsondata['pagenum'])
    searchres=db.execute(searchsql).fetchall()
    print(len(searchres))
    if jsondata['pagenum']==1:
        totallist=searchres[0]['id']
        totalpagenum=round(totallist/jsondata['pagecount']+0.5)
        posts['totalpage']=totalpagenum
    else:
        posts['totalpage']=jsondata['totalpage']
    
    posts['pagenum']=jsondata['pagenum']
    
    posts['seachres']=searchres

    posts['movieclass']=list(movieclass.values())

    posts['searchcmd']={}
    posts['cmd']=cmd


    return render_template('movie/movielist.html',posts=posts)
    
a=["名称","封面","集数","别名","导演","主演","类型","地区","语言","上映","片长","更新","总播放量","今日播放量","总评分","评分次数","简介","yun1","m3u8","下载","来源"]
e=["name","img","jishu","othername","director","actor","genre","region","language","screen","mlen","updatet","clicknum","todayclicknum","score","scorenum","introduction","yun1","m3u8","download","platform"]

@bp.route('/detail/<int:id>/',methods=('GET','POST'))
def detail(id):


    movid=int(id)
    db=get_db()
    searchsql='SELECT * from video where id=%d'%movid
    searchres=db.execute(searchsql).fetchall()

    posts={}
    posts['searchres']=searchres
    posts['movieclass']=list(movieclass.values())
    posts['displayname']=["id","author_id","名称","封面","集数","别名","导演","主演","类型","地区","语言","上映","片长","更新","总播放量","今日播放量","总评分","评分次数","简介","yun1","m3u8","下载","来源"]
                        #   0      1         2      3     4     5      6      7     8      9     10     11      12   13        14        15         16       17       18     19     20
    posts['displaynum']=[2,11,10,7,6,8,9,13]

    if 'm3u8' in searchres[0]['m3u8']:# ok zuida 有时候两个列表会混
        posts['m3u8']=json.loads(searchres[0]['m3u8'])
    else:
        posts['m3u8']=json.loads(searchres[0]['yun1'])


    return render_template('movie/moviedetail.html',posts=posts)

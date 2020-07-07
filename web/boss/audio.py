from boss.db import get_db
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for,current_app
import numpy as np
import scipy.io as scio
import json

bp = Blueprint('audio', __name__, url_prefix='/audio')


@bp.route('/h3d',methods=('GET','POST'))
def hrir3D():
    print('debug1')
    if request.method=='POST' or request.method=='GET':
        hrirdata=scio.loadmat('./boss/static/hrir/subject_003/hrir_final.mat')
        azimuths=np.array([-80,-65,-55]+[i for i in range(-45,46,5)]+[55,65,80])
        elmax=50
        elindices=np.arange(elmax)
        elevations=-45+5.625*elindices
        posts={}
        posts['azi']=azimuths.tolist()
        posts['ele']=elevations.tolist()
        
        posts['hr']=hrirdata['hrir_r'].tolist()
        posts['hl']=hrirdata['hrir_l'].tolist()
        testposts={'test1':12,'test2':'abc'}
    return render_template('audio/audio3d.html',posts=posts)

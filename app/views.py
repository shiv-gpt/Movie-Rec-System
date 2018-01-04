from flask import render_template, flash, redirect
import flask as f
from app import app
from .forms import LoginForm
import subprocess
import time
from flask import Flask, Response
from flask.ext.socketio import SocketIO, emit
from multiprocessing import Process
from threading import Thread
#import qinit
socketio = SocketIO(app)
# index view function suppressed for brevity
@app.route('/index')
def index():
    return render_template('index.html',title='Movie Recommendation')
import qinit as q
"""def call_async(t_user_id,t_Lamda,t_delta,t_n):
    thr = Thread(target = q.recommender(t_user_id,t_Lamda,t_delta,t_n))
    thr.start()"""
@app.route('/login', methods=['GET', 'POST'])
def login():
	#import qinit
    form = LoginForm()
    q.initMatrix()
    movie_name = q.calcGenre()
    if form.validate_on_submit():
        flash('Movie recommendations for userID="%s", Lambda=%s Delta = %s Number of Recommendations : %s' %(form.user_id.data, str(form.Lambda.data), str(form.delta.data), str(form.n.data)))
        t_user_id = int(form.user_id.data)
        t_Lamda = float(form.Lambda.data)
        t_delta = float(form.delta.data)
        t_n = int(form.n.data)
        """def inner():
            proc = subprocess.Popen(q.recommender(t_user_id,t_Lamda,t_delta,t_n),shell = True, stdout = subprocess.PIPE)
            for line in iter(proc.stdout.readline,''):
                yield line.rstrip() + '<br>/n'

        return Response(inner(),mimetype='text/html')
        
        print 'I am here'
        p2 = Process(target = fun())
        p2.start()
        print 'Now here'
        p1 = Process(target = q.recommender(t_user_id,t_Lamda,t_delta,t_n))
        p1.start()
        print 'Finally here'
        """
        #call_async(t_user_id,t_Lamda,t_delta,t_n)
        #import Queue as Q
        #pr = Q.PriorityQueue()
        pr = q.recommender(t_user_id,t_Lamda,t_delta,t_n)
        flash('Your Recommendations are')
        for i in range(t_n):
            (r,name) = pr.get()
            flash(str(i+1) + ". " + str(movie_name[name]) + " " + str(-r) + "\n")

        return redirect('/index')
        #p1.start()
        #q.recommender(t_user_id,t_Lamda,t_delta,t_n)
        #return redirect('/index')"""
    return render_template('login.html',title='Sign In',form=form)

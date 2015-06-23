# -*- coding: utf-8 -*-

POSTS_PER_PAGE = 5

def get_category():
    category_name = request.args(0)
    category = db.category(name=category_name)
    if not category:
        session.flash = 'page not found '
        redirect(URL('index'))
    return category

def index():
    rows = db(db.category).select()
    return locals()

@auth.requires_login()
def create_post():
    category = get_category()
    db.post.category.default = category.id
    form = SQLFORM(db.post).process(next='view_post/[id]')
    return locals()


#@auth.requires_login()
#def edit_post():
 #   id = request.args(0,cast=int)
  #  form = SQLFORM(db.post, id).process(next='view_post/[id]')
   # return locals()

def list_posts_by_datetime():
    response.view = 'default/list_posts_by_votes.html'
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.created_on,limitby=(start,stop))
    return locals()

def list_posts_by_votes():
    if request.args(0)=='trailers':
        #response.flash=request.args(0)
        redirect(URL('dekho'))
    else:
        category = get_category()
        page = request.args(1,cast=int,default=0)
        start = page*POSTS_PER_PAGE
        stop = start+POSTS_PER_PAGE
        rows = db(db.post.category==category.id).select(orderby=~db.post.votes,limitby=(start,stop))
    return locals()

#def list_posts_by_author():
 #   user_id = request.args(0,cast =int)
  #  page = request.args(1,cast=int,default=0)
   # start = page*POSTS_PER_PAGE
    #stop = start+POSTS_PER_PAGE
#    rows = db(db.post.created_by==user_id).select(orderby=~db.post.created_on,limitby=(start,stop))
 #   return locals()

def view_post():
    id = request.args(0,cast=int)
    post = db.post(id) or redirect(URL('index'))
    #response.flash=post.created_by
    comments = db(db.comm.post==post.id).select(orderby=~db.comm.created_on)
    return locals()

# http://hostname/app/default/vote_callback?id=2&direction=up

#def vote_callback():
 #   vars = request.post_vars
  #  print vars
   # if vars:
    #    id = vars.id
     #   direction = +1 if vars.direction == 'up' else -1
      #  post = db.post(id)
       # if post:
        #    post.update_record(votes=post.votes+direction)
       # print post.votes
 #   return str(post.votes)

#def comm_vote_callback():
 #  id = request.args(0,cast=int)
  # direction = request.args(1)
    ## TODO
   #return locals()

def voteformovie():
    """AJAX callback!"""
    response.flash="thankyou!"
    if request.args(0)=='add':
        #response.flash=request.args(1)
        db(db.post.Movie_name==request.args(1)).update(votes=db.post.votes + 1)
    if request.args(0)=='sub':
        #response.flash=request.args(1)
        db(db.post.Movie_name==request.args(1)).update(votes=db.post.votes - 1)

def dekho():
	records=db().select(db.videos.ALL)
	return dict(videos=records)

#def show():
#	id=request.vars.id
#	videos=db(db.videos.id==id).select()
#	if not len(videos):
#		session.flash='Could not find cooresponding video'
#		redirect(URL('show'))
#	return dict(video=videos)

def delete():
	id=request.vars.id
	db(db.videos.id==id).delete()
	session.flash='V@deo Deleted'
	redirect(URL('index'))
	return dict()

@auth.requires_membership('admins')
def new_video():
   form=SQLFORM(db.videos, fields=['movie_name','converted_image','uploaded_video'])
   if form.accepts(request,session):
		session.flash='Video successfully uploaded'
		redirect(URL('dekho'))
   return dict(form=form)

def user():
    """
    exposes:  
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

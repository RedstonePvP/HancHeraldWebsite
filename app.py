from flask import Flask, render_template, session, flash, redirect, url_for, request, abort, send_file
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_admin import Admin
from profanity_check import predict
from flask_mobility import Mobility
from fuzzywuzzy import fuzz
from functools import wraps
from jinja2 import Markup
import requests
import datetime
import random
import forms
import json
import api
import re
import os

app = Flask(__name__, static_url_path='/static')
app.secret_key = json.load(open("config.json"))["secret-key"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
db = SQLAlchemy(app)

app.config["UPLOADED_PHOTOS_DEST"] = "/static/images"
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

Mobility(app)

admin = Admin(app=app, url="/secadminpass")

cdn = api.CDNManager(username="herald", password=json.load(open("config.json"))["cdnPassword"])


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.String(4294000000), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    publisher_id = db.Column(db.Integer, nullable=False)
    writer_id = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    views = db.Column(db.Integer, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Integer, nullable=False)


class CatgRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(120), nullable=False)


class Sports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    when = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    orderstate = db.Column(db.Integer)
    home = db.Column(db.Integer, nullable=False)
    team2 = db.Column(db.String(120), nullable=False)
    score1 = db.Column(db.Integer)
    score2 = db.Column(db.Integer)
    sport = db.Column(db.String(120), nullable=False)
    gamenum = db.Column(db.Integer, nullable=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.String(500), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)


class CommentsArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    arch_id = db.Column(db.Integer, nullable=False)
    art_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.String(500), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)


class ArticleArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    arch_id = db.Column(db.Integer, nullable=False)
    art_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.String(4294000000), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    publisher_id = db.Column(db.Integer, nullable=False)
    writer_id = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    views = db.Column(db.Integer, nullable=False)


class ArchiveBatches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    time = db.Column(db.DateTime, nullable=False)


class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(120), nullable=False)


class MedrashaHanc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    file = db.Column(db.String(120), nullable=False)


class AskAdam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(300), nullable=False)
    headers = db.Column(db.String(100), nullable=False)
    state = db.Column(db.Integer, nullable=False)


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(100))
    sport = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    league = db.Column(db.String(10), nullable=False)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    val1 = db.Column(db.Integer)
    val2 = db.Column(db.Integer)


class SiteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.DateTime, nullable=False)
    day_comp = db.Column(db.String(50), nullable=False)
    visitors = db.Column(db.Integer, nullable=False)


class RefLinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    uses = db.Column(db.Integer, nullable=False)


class RefData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.DateTime, nullable=False)
    day_comp = db.Column(db.String(50), nullable=False)
    uses = db.Column(db.Integer, nullable=False)


class EmailSubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_date = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    state = db.Column(db.Integer, nullable=False)


admin.add_view(ModelView(Articles, db.session))
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(CatgRelationship, db.session))
admin.add_view(ModelView(Sports, db.session))
admin.add_view(ModelView(Comments, db.session))
admin.add_view(ModelView(CommentsArchive, db.session))
admin.add_view(ModelView(ArticleArchive, db.session))
admin.add_view(ModelView(ArchiveBatches, db.session))
admin.add_view(ModelView(Images, db.session))
admin.add_view(ModelView(Announcements, db.session))
admin.add_view(ModelView(MedrashaHanc, db.session))
admin.add_view(ModelView(AskAdam, db.session))
admin.add_view(ModelView(Teams, db.session))
admin.add_view(ModelView(Settings, db.session))
admin.add_view(ModelView(SiteHistory, db.session))
admin.add_view(ModelView(RefLinks, db.session))
admin.add_view(ModelView(RefData, db.session))
admin.add_view(ModelView(EmailSubs, db.session))


def log_visit(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        now = datetime.datetime.now()
        if "logged" in session:
            return f(*args, **kwargs)
        else:
            exist = SiteHistory.query.filter_by(day_comp=now.strftime("%d %m %Y")).first()
            if exist:
                exist.visitors += 1
                db.session.commit()
                session["logged"] = True
            else:
                newDay = SiteHistory(day=datetime.datetime.today().date(), visitors=1, day_comp=now.strftime("%d %m %Y"))
                db.session.add(newDay)
                db.session.commit()
                session["logged"] = True

            return f(*args, **kwargs)

    return wrap


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele+" "

        # return string
    return str1


def slug_valid(slug):
    valid = re.findall(r"{|[|]|}|\|^|~|;|/|:|@|&|=|$|,", slug)
    if valid:
        return True
    return False


def update_sports():
    slist = []
    nexts = Sports.query.filter_by(orderstate=2).first()
    if not nexts:
        return None

    elif nexts.gamenum == 1:

        team = Teams.query.filter_by(id=nexts.team2).first()
        if not nexts.score1:
            s1 = "-"
            s2 = "-"
        else:
            s1 = nexts.score1
            s2 = nexts.score2
        slist.append([nexts.sport, nexts.home, nexts.when.strftime("%B %d"), team.logo, team.name, s1, s2])
        return slist

    else:
        if nexts.when + datetime.timedelta(days=1) >= datetime.datetime.now():
            nextgame = Sports.query.filter_by(gamenum=nexts.gamenum + 1).first()
            if nextgame:
                nexts.orderstate = 1
                nextgame.orderstate = 2
                db.session.commit()

        team1 = Teams.query.filter_by(id=nexts.team2).first()
        if not nexts.score1:
            s1 = "-"
            s2 = "-"
        else:
            s1 = nexts.score1
            s2 = nexts.score2
        slist.append([nexts.sport, nexts.home, nexts.when.strftime("%B %d"), team1.logo, team1.name, s1, s2])
        game2 = Sports.query.filter_by(gamenum=nexts.gamenum-1).first()
        team2 = Teams.query.filter_by(id=game2.team2).first()
        if not game2.score1:
            s1 = "-"
            s2 = "-"
        else:
            s1 = game2.score1
            s2 = game2.score2
        slist.append([game2.sport, game2.home, game2.when.strftime("%B %d"), team2.logo, team2.name, s1, s2])
        return slist


def update_medrash():
    active = MedrashaHanc.query.filter_by(state=2).first()
    if active:
        print("is active")
        print(active.state)
        now = datetime.datetime.now()
        if active.time <= now:
            active.state = 1
            db.session.commit()
        else:
            print("returning 2 value")
            return [active.id, active.title]
    return None


def update_announcments_list():
    allanno = Announcements.query.filter_by(state=1, type="scroll").all()
    anno = []
    for annof in allanno:
        now = datetime.datetime.now()
        if annof.time <= now:
            annof.state = 0
            db.session.commit()
        else:
            print("ann active")
            anno.append(annof.text)

    if not anno:
        anno = None

    return anno


def update_announcments():
    allanno = Announcements.query.filter_by(state=1, type="scroll").all()
    anno = ""
    for annof in allanno:
        now = datetime.datetime.now()
        if annof.time <= now:
            annof.state = 0
            db.session.commit()
        else:
            print("ann active")
            anno = "Announcement: "+annof.text+" "

    if anno == "":
        anno = None

    return anno


def retrieve_comments(id):
    allcomments = Comments.query.filter_by(art_id=int(id)).all()
    alist = []
    for com in allcomments:
        days = datetime.datetime.now() - com.time
        if days.days == 0:
            days = "Commented less than a day ago"
        else:
            days = f"Commented {days.days} days ago"
        alist.append([com.name, com.comment, days])
    return alist


@app.errorhandler(404)
@app.errorhandler(500)
def error_404_500(e):
    print(f"error: {e}")
    return render_template("error_page.html")


@app.route("/fix-cookies")
def fix_cookies_route():
    session.clear()
    return "done"


@app.route("/m/writers/<id>")
def mobile_writers_route(id):
    if not request.MOBILE: return redirect(url_for("all_art_writer_route", id=id))
    allart = Articles.query.filter_by(writer_id=int(id)).all()
    name = Users.query.filter_by(id=int(id)).first()
    artlist = []
    for art in allart:
        text = art.content
        text = text.split(" ")
        if len(text) >= 30:
            text = text[:31]
            newtext = listToString(text)
        else:
            newtext = listToString(text)
        newtext = Markup(newtext).striptags()
        artlist.append([art.img, art.title, newtext, art.slug])
    artlist = artlist[::-1]
    print(artlist)
    return render_template("m_articles.html", artlist=artlist, author=name.name)


@app.route("/m/sports")
def mobile_sports():
    sports = update_sports()
    return render_template("m_sports.html", sports=sports)


@app.route("/m/medrash/post/<id>")
def mobile_medrash_post_route(id):
    if not request.MOBILE: return redirect(url_for("medrash_post_id_route", id=id))
    med = MedrashaHanc.query.filter_by(id=int(id)).first()
    if not med:
        return "Oops, Looks like this page doesnt exist! maybe it's been deleted"
    return redirect(f"https://hancherald.b-cdn.net/medrash/{med.file}")


@app.route("/m/medrash")
@log_visit
def mobile_medrash_route():
    if not request.MOBILE: return redirect(url_for("medrash_route"))
    allmed = MedrashaHanc.query.all()
    alist = []
    for med in allmed:
        alist.append([med.id, med.title])
    return render_template("m_midrash_list.html", alist=alist)


@app.route("/m/search", methods=["GET", "POST"])
@log_visit
def mobile_search_route():
    if not request.MOBILE: return redirect(url_for("search_route"))
    form = forms.SearchForm()
    if not session["search_query"] or ["search_query"] == "":
        return render_template("m_search.html", form=form)

    if form.validate_on_submit():
        session["search_query"] = form.query.data

    allart = Articles.query.all()

    artlist = []

    for art in allart:
        # name1 = Users.query.all().name
        # name = fuzz.token_set_ratio(session["search_query"], name1)
        title = fuzz.token_set_ratio(session["search_query"], art.title)
        desc = fuzz.token_set_ratio(session["search_query"], art.desc)
        print(session["search_query"])
        print(title)
        print(desc)
        if title >= 70 or desc >= 50:
            newtext = ""
            thisart = Articles.query.filter_by(id=art.id).first()
            text = thisart.content
            text = text.split(" ")
            if len(text) >= 30:
                text = text[:31]
                newtext = listToString(text)
            else:
                newtext = listToString(text)
            newtext = Markup(newtext).striptags()
            artlist.append([thisart.img, thisart.title, newtext, thisart.slug])

    artlist = artlist[::-1]
    return render_template("m_search.html", form=form, artlist=artlist, valabc=session["search_query"])


@app.route("/m/article/<slug>", methods=["GET", "POST"])
@log_visit
def mobile_article_slug_route(slug):
    if not request.MOBILE: return redirect(url_for("article_slug_route", slug=slug))
    form = forms.Comment()
    article = Articles.query.filter_by(slug=slug.lower()).first()
    if form.validate_on_submit():
        time = datetime.datetime.now()
        newComment = Comments(art_id=article.id, name=form.name.data, comment=form.comment.data, state=1, time=time)
        db.session.add(newComment)
        db.session.commit()
    print("in route")
    print(article)
    if not article:
        return redirect(url_for("index_route"))
    author = Users.query.filter_by(id=article.writer_id).first()
    full = article.time
    full = full.strftime("%B %d, %Y")
    print(full)
    print(article.content)
    clist = retrieve_comments(article.id)
    return render_template("m_article.html", title=article.title, author=author.name, date=full, auid=author.id,
                           img=article.img, contents=Markup(article.content), aid=article.id, form=form, clist=clist)


@app.route("/m")
@log_visit
def mobile_home_route():
    if not request.MOBILE: return redirect(url_for("index_route"))
    artid = Articles.query.limit(9).all()
    artlist = []
    for thisart in artid:
        text = thisart.desc
        text = text.split(" ")
        text = text[:16]
        thistext = listToString(text)
        full = thisart.time
        full = full.strftime("%B %d, %Y")
        artlist.append([thisart.img, thisart.title, thistext, thisart.slug, full])
    medrash = update_medrash()
    anno = update_announcments()
    artlist.reverse()

    return render_template("m_home.html", artic=artlist, medrash=medrash, annol=anno)


@app.route("/ref/<reflink>")
@log_visit
def ref_link_route(reflink):
    ref = RefLinks.query.filter_by(slug=reflink).first()
    if not ref:
        return redirect(url_for("index_route"))
    ref.uses += 1
    db.session.commit()
    now = datetime.datetime.now()
    todaydata = RefData.query.filter_by(day_comp=now.strftime("%d %m %Y")).first()
    if todaydata:
        todaydata.uses += 1
        db.session.commit()
    else:
        newDay = RefData(day=datetime.datetime.today().date(), day_comp=now.strftime("%d %m %Y"), uses=1)
        db.session.add(newDay)
        db.session.commit()
    return redirect(url_for("index_route"))


@app.route("/random")
@log_visit
def random_article_route():
    lastid = Articles.query.order_by("id").limit(1).first().id
    firstid = 1
    ranid = random.randint(firstid, lastid)
    ranarticle = Articles.query.filter_by(id=ranid).first()
    return redirect("/article/"+ranarticle.slug)


@app.route("/announcement")
@log_visit
def announcement_route():
    annol = update_announcments_list()
    return render_template("announce.html", annol=annol)


@app.route("/")
@log_visit
def index_route():
    if request.MOBILE: return redirect(url_for("mobile_home_route"))
    artid = Articles.query.limit(9).all()
    artlist = []
    for thisart in artid:
        text = thisart.desc
        text = text.split(" ")
        text = text[:16]
        thistext = listToString(text)
        full = thisart.time
        full = full.strftime("%B %d, %Y")
        artlist.append([thisart.img, thisart.title, thistext, thisart.slug, full])
    medrash = update_medrash()
    anno = update_announcments()
    artlist.reverse()
    firstart = artlist.pop(0)
    slist = update_sports()
    print(slist)

    return render_template("home_c_2.html", artic=artlist, medrash=medrash, first=firstart, annol=anno, sports=slist)


@app.route("/medrash/post/<id>")
@log_visit
def medrash_post_id_route(id):
    if request.MOBILE: return redirect(url_for("mobile_medrash_post_route", id=id))
    med = MedrashaHanc.query.filter_by(id=int(id)).first()
    if not med:
        return "Oops, Looks like this page doesnt exist! maybe it's been deleted or moved"
    return render_template("medrash_view.html", filename=med.file)


@app.route("/medrash")
@log_visit
def medrash_route():
    if request.MOBILE: return redirect(url_for("mobile_medrash_route"))
    allmed = MedrashaHanc.query.all()
    alist = []
    for med in allmed:
        alist.append([med.file, med.title])
    first = alist.pop(0)
    return render_template("medrash_list.html", first=first, alist=alist)


@app.route("/comment/new/<id>", methods=["GET", "POST"])
@log_visit
def new_comment(id):
    if request.method == "POST":
        name = request.form.get("name")
        text = request.form.get("text")
        profane = predict([text])
        if profane[0] == 1:
            return abort(500)
        newComment = Comments(art_id=int(id), name=name, comment=text, state=1, time=datetime.datetime.now())
        db.session.add(newComment)
        db.session.commit()
        return "done"


@app.route("/writers/<id>")
@log_visit
def all_art_writer_route(id):
    if request.MOBILE: return redirect(url_for("mobile_writers_route", id=id))
    allart = Articles.query.filter_by(writer_id=int(id)).all()
    name = Users.query.filter_by(id=int(id)).first()
    artlist = []
    for art in allart:
        text = art.content
        text = text.split(" ")
        if len(text) >= 30:
            text = text[:31]
            newtext = listToString(text)
        else:
            newtext = listToString(text)
        newtext = Markup(newtext).striptags()
        artlist.append([art.img, art.title, newtext, art.slug])
    artlist = artlist[::-1]
    print(artlist)
    return render_template("articles.html", artlist=artlist, author=name.name)


@app.route("/search", methods=["GET", "POST"])
@log_visit
def search_route():
    if request.MOBILE: return redirect(url_for("mobile_search_route"))
    form = forms.SearchForm()
    if not session["search_query"] or ["search_query"] == "":
        return render_template("search.html", form=form)

    if form.validate_on_submit():
        session["search_query"] = form.query.data

    allart = Articles.query.all()

    artlist = []

    for art in allart:
        # name1 = Users.query.all().name
        # name = fuzz.token_set_ratio(session["search_query"], name1)
        title = fuzz.token_set_ratio(session["search_query"], art.title)
        desc = fuzz.token_set_ratio(session["search_query"], art.desc)
        print(session["search_query"])
        print(title)
        print(desc)
        if title >= 70 or desc >= 50:
            newtext = ""
            thisart = Articles.query.filter_by(id=art.id).first()
            text = thisart.content
            text = text.split(" ")
            if len(text) >= 30:
                text = text[:31]
                newtext = listToString(text)
            else:
                newtext = listToString(text)
            newtext = Markup(newtext).striptags()
            artlist.append([thisart.img, thisart.title, newtext, thisart.slug])

    artlist = artlist[::-1]
    return render_template("search.html", form=form, artlist=artlist, valabc=session["search_query"])


@app.route("/api/search", methods=["GET", "POST"])
@log_visit
def api_search_route():
    if request.method == "POST":
        query = request.form.get("query")
        print(f"this is the query bring saved, {query}")
        session["search_query"] = query
        return "done"
    abort(405)


@app.route("/catg/Ask-Adam")
@log_visit
def ask_adam_catg_route():
    form = forms.AskAdam()
    catg="Ask Adam"
    artid = CatgRelationship.query.filter_by(category=catg).all()
    artlist = []
    for art in artid:
        newtext = ""
        thisart = Articles.query.filter_by(id=art.article).first()
        text = thisart.content
        text = text.split(" ")
        if len(text) >= 30:
            text = text[:31]
            newtext = listToString(text)
        else:
            newtext = listToString(text)
        newtext = Markup(newtext).striptags()
        artlist.append([thisart.img, thisart.title, newtext, thisart.slug])
    artlist = artlist[::-1]
    print(artlist)
    return render_template("articles.html", catg=catg, artlist=artlist, askadam=True, form=form)


@app.route("/catg/<catg>")
@log_visit
def view_catg_route(catg):
    catg = catg.replace("-", " ")
    print(catg)
    artid = CatgRelationship.query.filter_by(category=catg).all()
    artlist = []
    for art in artid:
        newtext = ""
        thisart = Articles.query.filter_by(id=art.article).first()
        text = thisart.content
        text = text.split(" ")
        if len(text) >= 30:
            text = text[:31]
            newtext = listToString(text)
        else:
            newtext = listToString(text)
        newtext = Markup(newtext).striptags()
        artlist.append([thisart.img, thisart.title, newtext, thisart.slug])
    artlist = artlist[::-1]
    print(artlist)
    return render_template("articles.html", catg=catg, artlist=artlist)


@app.route("/article/<slug>", methods=["GET", "POST"])
@log_visit
def article_slug_route(slug):
    if request.MOBILE: return redirect(url_for("mobile_article_slug_route", slug=slug))
    form = forms.Comment()
    article = Articles.query.filter_by(slug=slug.lower()).first()
    if form.validate_on_submit():
        time = datetime.datetime.now()
        newComment = Comments(art_id=article.id, name=form.name.data, comment=form.comment.data, state=1, time=time)
        db.session.add(newComment)
        db.session.commit()
    print("in route")
    print(article)
    if not article:
        return redirect(url_for("index_route"))
    author = Users.query.filter_by(id=article.writer_id).first()
    full = article.time
    full = full.strftime("%B %d, %Y")
    print(full)
    print(article.content)
    clist = retrieve_comments(article.id)
    article.views += 1
    db.session.commit()
    return render_template("article.html", title=article.title, author=author.name, date=full,
                           img=article.img, contents=Markup(article.content), aid=article.id, form=form, clist=clist, auid=author.id)


@app.route("/new/image", methods=["GET", "POST"])
@log_visit
def new_image_rote():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    form = forms.NewImage()
    if form.validate_on_submit():
        print(form.img.data)
        fln = str(form.img.data.filename).split(".")
        print(fln)
        fln = fln[1]
        print(fln)
        filename = str(random.randint(1,9000)) + \
                   requests.get("https://helloacm.com/api/random/?n=12").text.strip('"') + "." + fln
        print(filename)
        form.img.data.save(f"{os.getcwd()}/static/images/{filename}")
        cdn.new_cover_image(filename)
        os.remove(f"{os.getcwd()}/static/images/{filename}")

        newImg = Images(name=filename, time=datetime.datetime.now())
        db.session.add(newImg)
        db.session.commit()
        return redirect(url_for("new_article_route"))

    return render_template("newimage.html", form=form)


@app.route("/new/article", methods=["GET", "POST"])
@log_visit
def new_article_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    allusers = Users.query.all()
    images = Images.query.all()
    images = images[::-1]
    images = images[0]
    if request.method == "POST":
        title = request.form.get("title")
        writer = request.form.get("writer")
        contents = request.form.get("contents")
        categories = request.form.get("catg")
        description = request.form.get("desc")
        categories = categories.split(",")
        print(title)
        print(writer)
        print(contents)
        print(categories)
        cur = datetime.datetime.now()
        usr_id = Users.query.filter_by(name=writer).first()
        slug = title.split(" ")
        if len(slug) > 1:
            slug = slug[0]+"-"+slug[1]+"-"+str(random.randint(1, 9999))
        else:
            slug = slug[0]+"-"+str(random.randint(1, 9999))
        newArticle = Articles(title=title, time=cur, content=contents,
                              writer_id=usr_id.id, publisher_id=1, img=images.name,
                              slug=slug.lower(), desc=description, views=0)
        db.session.add(newArticle)
        db.session.commit()
        curart = Articles.query.filter_by(slug=slug.lower()).first()
        for cat in categories:
            newRelationship = CatgRelationship(article=curart.id, category=cat)
            db.session.add(newRelationship)
            db.session.commit()

    userlist = []
    for user in allusers:
        userlist.append(user.name)

    print(images)
    imagest = images.time.date()
    filename = images.name

    return render_template("newarticle.html", userlist=userlist, date=imagest, filename=filename)


@app.route("/error")
@log_visit
def error_route():
    return render_template("error_page.html")


@app.route("/logout")
@log_visit
def logout_route():
    session.clear()
    return redirect(url_for("index_route"))


@app.route("/login", methods=["GET", "POST"])
@log_visit
def login_route():
    form = forms.LoginForm()
    if "logged_in" in session:
        return redirect(url_for("index_route"))
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data,
                                     password=form.password.data).first()
        if user:
            session["logged_in"] = True
            session["id"] = user.id
            if 6 > user.admin > 0:
                session["admin"] = True
                session["admin_type"] = user.admin
            return redirect(url_for("index_route"))
        else:
            flash("Sorry, the Username or Password was invalid, please try again")
    return render_template("login.html", form=form)


@app.route("/admin/printout/gen")
def admin_printout_generate_route():
    arts = Articles.query.limit(15).all()
    artlist = []
    for art in arts:
        artlist.append([art.slug, art.img, art.title])
    print(artlist)
    artlist = artlist[::-1]
    firstart = artlist.pop(0)
    data = Articles.query.filter_by(slug=firstart[0]).first()
    firstart = [data.title, data.img, data.time.strftime("%B %d, %Y"), Markup(data.content)]

    return render_template("printout_gen.html", first=firstart, artlist=artlist)


@app.route("/admin/archive/delete/<id>")
def admin_archive_delete_route(id):
    return "In progress"


@app.route("/admin/archive/trigger", methods=["GET", "POST"])
def admin_archive_trigger_route():
    if request.method == "POST":
        print(request.form.get("title"))
        print(request.form.get("slug"))
        if not slug_valid(request.form.get("slug")):
            return "invalid_slug"

        newBatch = ArchiveBatches(title=request.form.get("title"), slug=request.form.get("slug"), date=datetime.datetime.now())
        db.session.add(newBatch)
        db.session.commit()
        batch = ArchiveBatches.query.filter_by(title=request.form.get("title")).first()
        allart = Articles.query.all()
        for article in allart:
            allcomm = Comments.query.filter_by(art_id=article.id).all()
            ArchArt = ArticleArchive(arch_id=batch.id, art_id=article.id, title=article.title, time=article.time,
                                     content=article.content, desc=article.desc, publisher_id=article.publisher_id,
                                     writer_id=article.writer_id, img=article.img, slug=article.slug, views=article.views)
            db.session.add(ArchArt)
            db.session.commit()
            for comm in allcomm:
                ArchComm = CommentsArchive(arch_id=batch.id, art_id=article.id, name=comm.name, comment=comm.comment,
                                           state=comm.state, time=comm.time)
                db.session.add(ArchComm)
                db.session.commit()

    return "done"


@app.route("/admin/archive")
def admin_archive_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))

    return render_template("admin_manage_archive.html")


@app.route("/admin/settings/update", methods=["GET", "POST"])
def admin_settings_update_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))

    if request.method == "POST":
        comm = request.form.get("allow_comments")
        commq = Settings.query.filter_by(setting="allow_comments").first()
        commq.status = int(comm)
        db.session.commit()
        return "done"

    abort(500)


@app.route("/admin/settings")
def admin_settings_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    comment = Settings.query.filter_by(setting="allow_comments").first()
    if not comment:
        newSetting = Settings(setting="allow_comments", status="0")
        db.session.add(newSetting)
        db.session.commit()
        comment = Settings.query.filter_by(setting="allow_comments").first()

    comment_stat = None
    if comment.status == 1:
        comment_stat = "checked"

    return render_template("admin_general_settings.html", comment=comment_stat)


@app.route("/admin/ref/del/<id>")
def admin_del_ref_route(id):
    if "admin" not in session:
        return redirect(url_for("index_route"))

    RefLinks.query.filter_by(id=int(id)).delete()
    db.session.commit()

    return redirect(url_for("admin_ref_route"))


@app.route("/admin/ref/new", methods=["GET", "POST"])
def admin_new_ref_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    if request.method == "POST":
        slug = request.form.get("link")
        newRef = RefLinks(slug=slug, uses=0)
        db.session.add(newRef)
        db.session.commit()
        return "done"
    return "ERROR"


@app.route("/admin/ref")
def admin_ref_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    allref = RefLinks.query.all()
    reflist = []
    for ref in allref:
        reflist.append([ref.id, ref.slug, ref.uses])

    reflist = reflist[::-1]
    return render_template("admin_reflinks_manage.html", reflist=reflist)


@app.route("/admin/sports/games/score/<id>", methods=["GET", "POST"])
def admin_sports_game_score_route(id):
    form = forms.Score()
    game = Sports.query.filter_by(id=int(id)).first()
    team2 = Teams.query.filter_by(id=int(game.team2)).first().name

    if form.validate_on_submit():
        game.score1 = int(form.team1.data)
        game.score2 = int(form.team2.data)
        db.session.commit()
        return redirect(url_for("admin_sports_game_route", sport="all"))

    return render_template("admin_games_manage_scores.html", form=form, team2=team2)


@app.route("/admin/sports/games/<sport>", methods=["GET", "POST"])
def admin_sports_game_route(sport):
    orgsport = sport
    if "admin" not in session:
        return redirect(url_for("index_route"))
    if sport == "all":
        allgames = Sports.query.filter_by(status=1).all()
        alist = []
        for game in allgames:
            team = Teams.query.filter_by(id=int(game.team2)).first()
            if team.sport == "b":
                sport = "Basketball"
            elif team.sport == "h":
                sport = "Hockey"
            else:
                sport = "Soccer"

            if team.gender == "m":
                gender = "Boys"
            else:
                gender = "Girls"

            if game.home == 1: where = "Home Game"
            else: where = "Away Game"

            if not game.score1:
                score1 = "-"
                score2 = "-"
            else:
                score1 = game.score1
                score2 = game.score2

            when = game.when.strftime("%a, %b %d at %I:%M %p")
            alist.append([game.id, sport, when, where, team.name, gender, team.league, score1, score2, game.gamenum])
            alist = alist[::-1]
        return render_template("admin_games_manage.html", alist=alist)
    else:
        form = forms.NewGame()
        games = Sports.query.filter_by(sport=sport, status=1).all()
        teams = Teams.query.filter_by(sport=sport).all()

        choices = []
        for team in teams:
            if team.gender == "m":
                gender = "Boys"
            else:
                gender = "Girls"

            if team.sport == "b":
                sport = "Basketball"
            elif team.sport == "h":
                sport = "Hockey"
            else:
                sport = "Soccer"

            choices.append((str(team.id), f"{team.name}, {gender} {team.league}"))

        form.team2.choices = choices

        if form.validate_on_submit():
            print("form valid")
            if not games:
                orderstate = 2
                gamenum = 1
            else:
                orderstate = 1
                gamenum = int(games.query.filter_by(sport=sport, status=1).first().gamenum)+1
            if form.ishome.data:
                ishome = 1
            else:
                ishome = 0
            selectedteam = Teams.query.filter_by(id=int(form.team2.data)).first()

            print("no issuses at new game")
            when = datetime.datetime.combine(form.date.data, form.time.data)
            newGame = Sports(when=when, status=1, orderstate=orderstate, home=ishome, team2=selectedteam.id, sport=selectedteam.sport, gamenum=gamenum)
            db.session.add(newGame)
            db.session.commit()

        games = Sports.query.filter_by(status=1, sport=orgsport).all()

        print(form.team2.choices)
        print(games)
        alist = []
        for game in games:
            team = Teams.query.filter_by(id=int(game.team2)).first()

            if team.sport == "b":
                sport = "Basketball"
            elif team.sport == "h":
                sport = "Hockey"
            else:
                sport = "Soccer"

            if team.gender == "m":
                gender = "Boys"
            else:
                gender = "Girls"

            if game.home == 1:
                where = "Home Game"
            else:
                where = "Away Game"

            if not game.score1:
                score1 = "-"
                score2 = "-"
            else:
                score1 = game.score1
                score2 = game.score2

            when = game.when.strftime("%a, %b %d at %I:%M %p")
            alist.append([game.id, sport, when, where, team.name, gender, team.league, score1, score2, game.gamenum])
            print(alist)
            alist = alist[::-1]
        return render_template("admin_games_manage.html", alist=alist, notall=True, form=form)


@app.route("/admin/sports/teams", methods=["GET", "POST"])
def admin_sports_team_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))

    form = forms.NewTeam()
    if form.validate_on_submit():
        print(form.file.data)
        filename = str(form.file.data.filename)
        filename = str(random.randint(1, 9000))+filename
        form.file.data.save(f"{os.getcwd()}/static/sport_logos/{filename}")
        cdn.new_team_logo(filename)
        os.remove(f"{os.getcwd()}/static/sport_logos/{filename}")

        newTeam = Teams(name=form.schoolname.data, logo=filename, sport=form.sport.data, gender=form.gender.data,
                        league=form.league.data)
        db.session.add(newTeam)
        db.session.commit()

    ateams = Teams.query.all()
    alist = []
    for team in ateams:
        if team.sport == "b": sport = "Basketball"
        elif team.sport == "h": sport = "Hockey"
        else: sport = "Soccer"

        if team.gender == "m": gender = "Boys"
        else: gender = "Girls"
        alist.append([team.id, team.name, sport, gender, team.league, team.logo])

    alist.reverse()

    return render_template("admin_teams_manage.html", form=form, alist=alist)


@app.route("/admin/announcements/del/<id>")
def admin_announcements_del_route(id):
    if "admin" not in session:
        return redirect(url_for("index_route"))

    Announcements.query.filter_by(id=int(id)).delete()

    return redirect(url_for("admin_announcements_route"))


@app.route("/admin/announcements", methods=["GET", "POST"])
def admin_announcements_route():
    form = forms.NewAnnouncement()
    if "admin" not in session:
        return redirect(url_for("index_route"))

    if form.validate_on_submit():
        print(form.enddate.data, type(form.enddate.data))
        print(form.endtime.data, type(form.endtime.data))
        fulldate = datetime.datetime.combine(form.enddate.data, form.endtime.data)
        newAnn = Announcements(text=form.content.data, state=1, time=fulldate, type="scroll")
        db.session.add(newAnn)
        db.session.commit()

    allano = Announcements.query.filter_by(state=1).all()
    alist = []
    for ano in allano:
        ending = ano.time.strftime("%a, %b %d at %I:%M %p")
        alist.append([ano.id, ano.text, str(ending)])

    return render_template("admin_announcments_manage.html", form=form, alist=alist)


@app.route("/admin/medrash/del/<id>")
def admin_medrash_del_route(id):
    if "admin" not in session:
        return redirect(url_for("index_route"))
    medrash = MedrashaHanc.query.filter_by(id=int(id)).delete()
    db.session.commit()

    return redirect(url_for("admin_route"))


@app.route("/admin/medrash")
def admin_medrash_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    medrashim = MedrashaHanc.query.all()
    alist = []
    for medrash in medrashim:
        date = medrash.time - datetime.timedelta(days=1)
        fdate = str(date.strftime("%b %d, %Y"))
        if medrash.state == 2:
            state = "On Homepage"
        elif medrash.state == 1:
            state = "Active"
        else:
            state = "Inactive"
        alist.append([medrash.id, medrash.title, fdate, state])
        alist = alist[::-1]

    return render_template("admin_medrash_manage.html", alist=alist)


@app.route("/admin/medrash/new", methods=["GET", "POST"])
def admin_medrash_new_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    form = forms.NewMedrash()
    now = datetime.datetime.now()
    downtime = now + datetime.timedelta(days=1)
    downtime1 = "Announced Until " + str(downtime.strftime("%a, %w at %I:%M %p"))
    if form.validate_on_submit():
        print(form.file.data)
        filename = form.parsha.data+str(now.year)+str(random.randint(1, 9000)+str(random.randint(1, 9999)))+".pdf"
        print(filename)
        form.file.data.save(f"{os.getcwd()}/static/medrash/{filename}")
        cdn.new_medrash(filename)
        os.remove(f"{os.getcwd()}/static/medrash/{filename}")

        newMed = MedrashaHanc(title=form.parsha.data, state=2, time=downtime, file=filename)
        db.session.add(newMed)
        db.session.commit()
        return redirect(url_for("index_route"))
    return render_template("admin_medrash.html", form=form, ti=downtime1)


@app.route("/admin/articles/del/<id>")
def admin_article_del_route(id):
    if "admin" not in session:
        return redirect(url_for("index_route"))

    Articles.query.filter_by(id=int(id)).delete()
    db.session.commit()

    return redirect(url_for("admin_article_route"))


@app.route("/admin/articles")
def admin_article_route():
    if "admin" not in session:
        return redirect(url_for("index_route"))
    articlelist = []
    arti = Articles.query.all()
    for art in arti:
        articlelist.append([art.title, art.id])
    articlelist = articlelist[::-1]
    print(articlelist)
    return render_template("admin_articles.html", alist=articlelist)


@app.route("/admin/users/edit/<id>", methods=["GET", "POST"])
def admin_user_edit_route(id):
    if "admin" in session:
        if request.method == "GET":
            selected = ["", "", "", "", ""]
            user = Users.query.filter_by(id=int(id)).first()
            admin = "Error"
            if user.admin == 1:
                admin = "Full Admin"
                selected[0] = "selected"
            elif user.admin == 2:
                admin = "Writer"
                selected[1] = "selected"
            elif user.admin == 3:
                admin = "Moderator"
                selected[2] = "selected"
            elif user.admin == 4:
                admin = "School Administrator"
                selected[3] = "selected"
            elif user.admin == 5:
                admin = "Medrasha Hanc Admin"
                selected[4] = "selected"
            userdata = [user.id, user.name, user.username, user.password, admin]
            return render_template("admin_user_manage_edit.html", data=userdata, selected=selected)
        if request.method == "POST":
            name = request.form.get("name")
            username = request.form.get("username")
            password = request.form.get("password")
            typeof = request.form.get("typeof")

            user = Users.query.filter_by(id=int(id)).first()
            user.name = name
            user.username = username
            user.password = password
            user.admin = typeof

            db.session.commit()

            return "1"
    return redirect(url_for("index_route"))


@app.route("/admin/users/new", methods=["GET", "POST"])
def admin_user_new_route():
    if "admin" in session:
        if request.method == "POST":
            name = request.form.get("name")
            username = request.form.get("username")
            password = request.form.get("password")
            typeof = request.form.get("typeof")

            newuser = Users(name=name, username=username, password=password,
                           admin=int(typeof))
            db.session.add(newuser)
            db.session.commit()
            return "1"
    return redirect(url_for("index_route"))


@app.route("/admin/users/del/<id>")
def admin_user_del_route(id):
    if "admin" in session:
        Users.query.filter_by(id=int(id)).delete()
        db.session.commit()
        return redirect(url_for("admin_user_route"))
    return redirect(url_for("index_route"))


@app.route("/admin/users")
def admin_user_route():
    if "admin" in session:
        users = Users.query.all()
        userlist = []
        selected = ["", "", "", "", ""]
        for user in users:
            admin = "Error"
            if user.admin == 1:
                admin = "Full Admin"
            elif user.admin == 2:
                admin = "Writer"
            elif user.admin == 3:
                admin = "Moderator"
            elif user.admin == 4:
                admin = "School Administrator"
            elif user.admin == 5:
                admin = "Medrasha Hanc Admin"
            userlist.append([user.id, user.name, user.username,
                             admin])
        userlist = userlist[::-1]
        print(userlist)
        return render_template("admin_user_manage.html", list=userlist)
    return redirect(url_for("index_route"))


@app.route("/admin")
def admin_route():
    if "admin" in session:
        if session["admin_type"] == 5:
            return redirect(url_for("admin_medrash_route"))
        return render_template("admin_home.html")
    return redirect(url_for("index_route"))


@app.route("/staff")
@log_visit
def staff_page_route():
    pass


if "__main__" == __name__:
    app.run()

# -*- coding: UTF-8 -*-
from flask import (
    Blueprint,flash,g,redirect,render_template,request,url_for
)
from werkzeug.exceptions import abort
from blue7accoon.auth import login_required
from blue7accoon.db import get_db
import os,datetime
import random,re

bp = Blueprint("models",__name__)


@bp.route("/video_play/<string:video_dir>",methods=("GET","POST"))
def video_play(video_dir):
    db = get_db()
    error = None

    if request.method == "POST":
        if g.user:
            body = request.form["body"]

            if not body:
                error = "请评论后再提交！"
            else:
                db = get_db()
                video = db.execute(
                    "SELECT * FROM video_info WHERE video_dir = ?", (video_dir,)
                ).fetchone()
                db.execute(
                    "INSERT INTO comment (body,author_id,video_id)"
                    " VALUES (?,?,?)",
                    (body, g.user["id"], video["id"])
                )
                db.commit()
                return redirect(url_for("models.video_play",video_dir=video_dir))
        else:
            error = "请先登录后再评论！"
        if error is not None:
            flash(error)

    comments = None
    video = db.execute(
        "SELECT id,video_name,video_type,video_dir FROM video_info"
        " WHERE video_dir = ?",(video_dir,)
    ).fetchone()
    if db.execute(
        "SELECT id FROM comment WHERE video_id=?",(video["id"],)
    ).fetchone is not None:
        comments = db.execute(
           """SELECT c.id,body,datetime(created,"localtime"),author_id,video_id,username,icon
              FROM comment c JOIN user u ON c.author_id = u.id
              WHERE video_id = ?
              ORDER BY created ASC""",(video["id"],)
        ).fetchall()

    total = db.execute(
        "SELECT COUNT(*) n FROM video_info"
    ).fetchone()
    random_int = random.sample(range(total["n"]),3)

    recommend = []
    for i in random_int:
        random_video = db.execute(
            "SELECT * FROM video_info WHERE id = ?",(i,)
        ).fetchone()
        recommend.append(random_video)

    db.execute(
        "UPDATE video_info SET video_view_times = video_view_times + 1"
        " WHERE video_dir = ?",(video_dir,)
    )
    db.commit()
    print(comments)
    return render_template("models/video_play.html",video=video,comments=comments,recommend=recommend)


def get_video_name(video_dir):
    video_list = []
    for root,dirs,files in os.walk(video_dir):
        for file in files:
            filename = os.path.splitext(file)[0]
            video_list.append(filename)
    return video_list

def video_update(video_dirs=()):
    db = get_db()
    for video_dir in video_dirs:
        video_list = get_video_name(video_dir)
        subdir = os.listdir(video_dir)
        videos = list(zip(video_list,subdir))

        for video in videos:
            if db.execute(
                "SELECT * FROM video_info WHERE video_dir = ?",(video[1],)
            ).fetchone() is None:
                video_type = re.search(r".*video\\(.*)",video_dir).group(1)

                db.execute(
                    "INSERT INTO video_info (video_name,video_dir,video_type)"
                    " VALUES (?,?,?)",(video[0],video[1],video_type)
                )
                db.commit()


@bp.route("/",methods=("GET",))
@bp.route("/index",methods=("GET",))
def index():
    db = get_db()

    video = db.execute(
        "SELECT * FROM video_info WHERE video_type = 'new'"
    ).fetchall()
    return render_template("models/index.html",video=video)


@bp.route("/index/edm")
def edm():
    db = get_db()
    video = db.execute(
        "SELECT * FROM video_info WHERE video_type = 'edm'"
    ).fetchall()
    return render_template("models/edm.html",video=video)


@bp.route("/index/trailer")
def trailer():
    db = get_db()
    video = db.execute(
        "SELECT * FROM video_info WHERE video_type = 'trailer'"
    ).fetchall()
    return render_template("models/trailer.html",video=video)


@bp.route("/index/discover")
def discover():
    db = get_db()

    total = db.execute(
        "SELECT COUNT(*) n FROM video_info"
    ).fetchone()
    random_int = random.sample(range(total["n"]),10)

    discover = []
    for i in random_int:
        random_video = db.execute(
            "SELECT * FROM video_info WHERE id = ?", (i,)
        ).fetchone()
        discover.append(random_video)

    return render_template("models/discover.html",discover=discover)

@bp.route("/index/external_link")
def external_link():
    return render_template("models/external-link.html")


@bp.route("/index/billboard")
def billboard():
    db = get_db()
    data = db.execute(
        "SELECT * FROM video_info ORDER BY video_view_times DESC"
    ).fetchall()
    return render_template("models/billboard.html",data=data)

@bp.route("/search")
def search():
    db = get_db()
    content = (request.args.get("keyword")).upper()
    print(content)
    video_list = []
    for dir in [
        ".\\blue7accoon\\static\\video\\other",
        ".\\blue7accoon\\static\\video\\trailer",
        ".\\blue7accoon\\static\\video\\edm",
        ".\\blue7accoon\\static\\video\\new"
    ]:
        for item in get_video_name(dir):
            if item.upper().find(content) > -1:
                video_list.append(item)

    rst = []
    for item in video_list:
        video = db.execute(
            "SELECT * FROM video_info WHERE video_name = ?", (item,)
        ).fetchone()
        rst.append(video)
    return render_template("models/search-result.html", rst=rst)


# -*- coding: UTF-8 -*-
import functools,os

from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash,generate_password_hash
from werkzeug.utils import secure_filename
from blue7accoon.db import get_db
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr,formataddr
import smtplib


bp = Blueprint("auth",__name__,url_prefix="/auth") #创建蓝图，蓝图下的所有路由地址在使用时需加"/auth"前缀


def login_required(view):
    # 编写将未知用户重定向至登录页面的视图装饰器
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


def _format_addr(s):
    name,addr = parseaddr(s)
    return formataddr((Header(name,"utf-8").encode(),addr))


@bp.before_app_request   # 注册蓝图后对全局生效的装饰器
def load_logged_in_user():
    # 如果用户id在会话中，从数据库将用户对象导入
    # 每个请求之前都会运行此函数
    user_id = session.get("user_id")    # 会话跨请求存在

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?",(user_id,)
        ).fetchone()



@bp.route("/register",methods=("GET","POST"))
def register():
    # 注册新用户
    # 确保用户名唯一，存储密码的哈希值
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        rePassword = request.form["rePassword"]
        email = request.form["email"]

        db = get_db()
        error = None

        if not username:
            error = "未输入用户名！"
        elif not password:
            error = "未输入密码！"
        elif not rePassword:
            error = "请确认密码！"
        elif not email:
            error = "请输入电子邮箱地址！"
        elif len(username) < 2:
            error = "用户名不可少于两个字符！"
        elif db.execute(
            "SELECT id FROM user WHERE username = ?",(username,)
        ).fetchone() is not None:
            error = "用户名 {0} 已被注册！".format(username)
        elif password != rePassword:
            error = "两次输入的密码必须一致！"
        elif db.execute(
            "SELECT id FROM user WHERE email = ?",(email,)
        ).fetchone() is not None:
            error = "同一邮箱只可注册一个帐号！"
        if error is None:
            # 将用户名和密码哈希值存储在数据库中并发送验证邮件之后跳转到登录界面
            db.execute(
                "INSERT INTO user (username,password,email) VALUES (?,?,?)",
                (username,generate_password_hash(username + password + "eu72dj"),email)
            )
            db.commit()


            msg = MIMEMultipart()
            msg["From"] = _format_addr("blue7accoon <xxxx@xxx.com>")
            msg["To"] = _format_addr("<%s>" %email)
            msg["Subject"] = Header("欢迎您加入blue7accoon！请验证邮箱地址！", "utf-8").encode()

            # 邮件正文-html
            msg.attach(MIMEText("""<html><body><h3>您好！{0}</h3>
                                <p>欢迎加入blue7accoon！</p>
                                <p>请点击下方链接完成邮箱验证：</p>
                                <p><a href='http://127.0.0.1:5000/auth/login/{1}'>点击此处链接完成邮箱验证<a></p>
                                <p>如果您没有注册blue7accoon帐号，请忽略这封邮件</p>
                                </body></html>""".format(username,generate_password_hash(username + "eu343hds")), "html", "utf-8"))

            server = smtplib.SMTP(smtp_server, 587)
            server.set_debuglevel(1)
            server.login("xxxx@xxx.com", email_password)
            server.sendmail("xxxx@xxx.com", [email], msg.as_string())
            server.quit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("/login",methods=("GET","POST"))
@bp.route("/login/<string:id>",methods=("GET","POST"))
def login(id=None):
    # 将用户id加入会话来进行登录
    if request.method == "POST":
        db = get_db()
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?",(username,)
        ).fetchone()
        if id is not None:
            if check_password_hash(id,username + "eu343hds"):
                db.execute(
                    "UPDATE user SET email_validation = 1"
                    " WHERE username = ?",(username,)
                )
                db.commit()
            else:
                return render_template("404.html")
        if not username:
            error = "请输入用户名！"
        elif not password:
            error = "请输入密码！"
        elif user is None:
            error = "用户名不存在！"
        elif not check_password_hash(user["password"],username + password + "eu72dj"):
            error = "密码错误！"
        elif user["email_validation"] < 1:
            error = "初次登录请先验证邮箱！"
        if error is None:
            # 使用用户id创建会话并返回首页
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("models.index"))

        flash(error)

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    # 清除会话以及其中的用户数据
    session.clear()
    return redirect(url_for("models.index"))


@bp.route("user/profile",methods=("GET","POST"))
@login_required
def profile():
    if request.method == "POST":
        db = get_db()
        username = request.form["username"]
        password = request.form["password"]
        f = request.files["file"]
        icon = secure_filename(f.filename)
        suffix = (".jpg", ".bmp", ".jpeg", ".png", ".gif")
        error = None

        if not username:
            username = g.user["username"]
        if db.execute(
            "SELECT id FROM user WHERE username = ?",(username,)
        ).fetchone() is not None:
            error = "用户名 {0} 已被注册！".format(username)
        if not password:
            password = g.user["password"]
        if not icon:
            icon = g.user["icon"]
        else:
            if not icon.endswith(suffix):
                error = "请上传指定格式的头像文件！"
            else:
                f.save(".\\static\\icon\\" + username + icon)
                icon = username + icon
        if error is None:
            db.execute(
                "INSERT INTO user (username,password,icon)"
                " VALUES (?,?,?)", (username,password,icon)
            )
            db.commit()
        return redirect(url_for("auth.login"))

    return render_template("auth/profile.html")


@bp.route("user/userSpace")
@login_required
def userSpace():
    return render_template("auth/userSpace.html")


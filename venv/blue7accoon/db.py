# -*- coding: UTF-8 -*-
import sqlite3

import click
from flask import current_app,g
from flask.cli import with_appcontext


def get_db():
    # 连接到配置好的数据库，连接对于每次请求都是唯一的，此函数可重复调用
    if "db" not in g:
        g.db = sqlite3.connect(
                            current_app.config["DATABASE"],
                            detect_types=sqlite3.PARSE_DECLTYPES
                            )
        g.db.row_factory = sqlite3.Row      # 返回Row对象，namedtuple类型

    return g.db



def close_db(e=None):
    # 关闭数据库连接
    db = g.pop("db",None)

    if db is not None:
        db.close()


def init_db():
    # 清除原本的数据，创建新的数据表
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    # 初始化数据库
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    # 将数据库函数注册到应用工厂
    app.teardown_appcontext(close_db)   # 无论是否发生异常，都会在返回响应进行清理时调用
    app.cli.add_command(init_db_command) # 添加flask命令行命令

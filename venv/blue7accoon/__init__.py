# -*- coding: UTF-8 -*-
import os
from flask import Flask

def create_app(test_config=None):
    # 创建并配置一个Flask应用的实例
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        # 使用os.urandom(16)生成
        SECRET_KEY="\xad>\xd1S\xc3nw\xc6\xd1Te\x10\xf4\xbe\xfdI",   # 配置实例密钥
        DATABASE=os.path.join(app.instance_path,"blue7accoon.sqlite"),
    )
    app.app_context().push()

    if test_config is None:
        # 非测试模式下载入实例参数
        app.config.from_pyfile("config.py",silent=True)
    else:
        # 载入传入的测试参数
        app.config.update(test_config)

    # 确保存在实例路径
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 注册数据库指令
    from blue7accoon import db
    db.init_app(app)


    # 将蓝图添加到应用工厂函数
    from blue7accoon import auth,models
    app.register_blueprint(auth.bp)
    app.register_blueprint(models.bp)

    # 添加视频信息到数据库
    subdirs = os.listdir(".\\blue7accoon\\static\\video\\")
    video_dirs = tuple([".\\blue7accoon\\static\\video\\" + subdir for subdir in subdirs])
    models.video_update(video_dirs)


    return app
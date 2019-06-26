## blue7accoonWebApp
- 一个视频网站应用,前端主要依赖bootstrap框架实现,后端通过改写Flask官方tutorial完成
- 主要功能：视频播放、注册、登录、邮箱验证、视频评论、视频检索
- 运行所需环境都已配置好
### 使用方法
- 将MP4格式的视频拷贝到venv/blue7accoon/static/video文件夹中，根据分类按照video中的格式创建新的子文件夹，再将视频置于其中
- 对视频进行截图，截图需要重命名为与视频文件名一致，之后放置于venv/blue7accoon/static/images文件夹下
- 如需启用注册、登录、评论等功能，请对以下代码进行修改：
````dwdw```
### 注意事项
- `runServer.bat`设置了当前应用以调试模式启动，如果需要以生产模式启动可以将其中的`set FLASK_ENV=development`去掉
- `runServer.bat`中加入了初始化数据库的命令行语句，每次执行都会清空其中的数据表

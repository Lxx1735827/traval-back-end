# traval-back-end

## 环境配置
- 下载代码到本地
- 下载requirement里面的库
- 安装mysql
- 修改setting.py里面的配置
  主要是这里："default": "mysql://root:2022141461051@localhost:3306/travel"
                                用户名：密码                   端口/数据库名字  （数据库名字需要自己再创建一个数据库）（用户名和端口一般默认是这个，如果自己没有改的话）
- 删除migrations文件和pyproject.toml
- 在traval-back-end/路径下运行aerich init -t src.setting.TORTOISE_ORM
- 在traval-back-end/路径下运行aerich init-db
------------------ 环境配置完成

## 运行
- 直接运行main.py文件
## 其他
- 可以学习fastapi，也可以直接仿照代码
- git拉不下来,找lxx


# 落花项目  [![Build Status](https://travis-ci.org/jnrainerds/luohua.png)](https://travis-ci.org/jnrainerds/luohua) [![Coverage Status](https://coveralls.io/repos/jnrainerds/luohua/badge.png?branch=master)](https://coveralls.io/r/jnrainerds/luohua?branch=master) [![Total views](https://sourcegraph.com/api/repos/github.com/jnrainerds/luohua/counters/views.png)](https://sourcegraph.com/github.com/jnrainerds/luohua) [![Views in the last 24 hours](https://sourcegraph.com/api/repos/github.com/jnrainerds/luohua/counters/views-24h.png?no-count=1)](https://sourcegraph.com/github.com/jnrainerds/luohua)

![luohua logo](/docs/_static/logo-720x240.png)


## 简介

这是江南听雨网的后端项目. 江南听雨网的目的是接替江南听雨 BBS 成为江南大学的下一代大学生社区网站, 同时也肩负着探索高校 BBS 的转型道路 (技术与运营方面) 的历史使命. 这个目标从 2012 年开始酝酿, 经过长久的学习积累和试错, 最终形成了现在的项目.


## 特性

* **分布式**: 数据持久层, 应用服务器, 任务队列服务器均可伸缩
* **实时性**: 基于 `gevent-socketio` 与 Redis PubSub 的实时消息机制
* **保留历史**: 所有安全相关的操作和内容操作都保留完整历史, API 界面不支持任何形式的数据删除.
* **国家政策**: 江南听雨网属于高校学生网站; 按照教育部规定, 实现了基于高校具体情况构建的实名认证


### 关于实名机制

为了借助实名信息而更有针对性地服务用户群体 (主要是在校大学生), 以及控制滥用网站资源, 目前实名机制与帐户系统是耦合的. 但架构上帐号系统可以完全脱离实名机制而独立运作, 如果你没有实名制方面的需要, 请与我们联系.

当前支持的高校列表:

* 江南大学


## 授权

* GPLv3+


## 部署说明

**注意** 这里仅仅描述本项目 (后端) 的部署; 前端环境部署请参见 `jnrainerds/jnrain-web` 项目的说明.

为简化描述, 假定操作者具备基本的 Linux 命令行生存能力, 例如路径, 工作目录, 命令参数, 转义 (escape) 之类的基本概念不再赘述.


### 外部依赖

* 推荐使用 64 位 Linux 环境. 32 位 Linux 的网络性能有限制; 其他操作系统未经测试, 不确保可用性或稳定性.
* Python 2.7.x, virtualenv
* 至少 1 个 Riak 实例, 默认存储后端需要设置为 `leveldb` (以启用 2i).
* 至少 1 个 Redis 实例
* 1 个 SMTP 服务器和域名, 用于发送邮箱验证, 找回密码, 系统通知等邮件
* 1 个 `jnrain-web` 部署. 为防止跨域带来麻烦, 应该将两个项目部署到同一个域名下的不同子域名, 例如 `example.com` (前端) 与 `api.example.com` (后端).


### 部署流程

* 安装 Protobuf Compiler (`riak-pb` 的外部依赖), 具体方法随不同 distro 而变; 请用 root 权限执行.
    - Debian 系 (Debian/Ubuntu/...): `apt-get install protobuf-compiler`
    - Gentoo 系: `emerge protobuf` 注意需要打开 `USE="python"`
* `virtualenv <给你的虚拟环境起个名字>`
* `git clone` 本项目
* 在刚才的虚拟环境里 `pip install -r <本项目的 requirements.txt>`
* 根据 `Rain.d` 中各种 `*.example.yml` 定制你的配置文件. 推荐放在单独的目录, 用 `config.yml` 可以包含你的设置文件
* 设置应用服务器, 实时通道服务器和 Celery worker 进程, 推荐使用 supervisor, 请自行安装.  *TODO: 配置样例*
* 设置 HTTP 前端服务器 (其实不一定, 但为了性能和稳定性一般都加一层), 推荐 nginx.  *TODO: 配置样例*


## 路线图

* 改善 coverage
    - 完善单元测试
    - 撰写集成测试, 测试 HTTP API 界面
* 实现比较完整的 Analytics
    - 仿照 GA 等产品实现统计和前端展示功能
    - 加入高校特色, 例如按学院/专业/年级的统计等等
* OAuth Provider 支持
* ...


## 开发者

### 创始人/领衔开发者

* @xen0n (气体sama)


### 开发团队

暂无, 不过期待你的加入 :-P


<!-- vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8: -->

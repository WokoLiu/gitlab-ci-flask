# gitlab-ci-flask

这是一个简单的 demo 项目，用于展示如何使用 GitLab-CI 为 Flask 应用做单元测试和API测试

项目中会写一个简单的 flask app，为其添加单元测试和 API 测试，并在 CI 里使用预置数据库进行测试

# 需要了解的内容：
* [flask](https://github.com/pallets/flask)
* mysql
* redis
* [pytest](https://docs.pytest.org/en/latest/)
* [gitlab-ci](https://gitlab.com/help/ci/yaml/README)
* [docker](https://www.docker.com/)

# 项目结构

```
.
├── .gitlab-ci.yml      # gitlab ci 配置文件
├── Dockerfile          # 构建镜像所需
├── app.py              # Flask 应用，就这一个文件
├── config              # 根据环境区分配置文件
│   ├── develop.py
│   ├── production.py
│   └── test.py
├── init_db.py          # 用于初始化测试数据库
├── init_db.sql         # 测试数据库的 scheme 和数据
├── mock                # 使用测试数据库进行 API 测试
│   ├── __init__.py
│   └── test_app.py
├── requirements.txt    # 依赖
└── unit                # 单元测试目录
    ├── __init__.py
    └── test_app.py
```

应用代码[app.py] 很简单，一共提供四个接口，其中 `/` 用到了 Redis，其他三个接口用到了 MySQL

配置文件[config] 会根据 `ENV_MODE` 环境变量，选择相应的配置文件，并读取配置

单元测试[unit] 只测了 `hit_count` 一个函数，使用 pytest 来运行

API 测试[mock] 里使用了 [Flask 推荐的测试方式](https://flask.palletsprojects.com/en/1.1.x/testing/)，同样使用 pytest

以上四部分，都是本地可以直接运行的，就算没有 CI 也可以进行测试

但放到 CI 里时，可以定制数据库数据，以保证每次运行测试时，所有的输入输出都是可预期的

对于运行 CI 时的数据库，有两个想法，一是另外单独打一个数据库镜像，每次运行测试时使用那个镜像；另一个是准备一个 .sql 文件，CI 时进行构建

这里为了简单，选择方法二。[init_db.sql] 就是这个数据库文件的内容，可以看到十分简单，就一个表两个字段

至于如何在运行 CI 时将这个文件 load 进数据库，目前我还没找到太好的办法，GitLab-CI 还没支持在初始化 services 前写入配置及初始化数据，因此只好[手动写入](init_db.py)

[.gitlab-ci.yml] 就是具体的 CI 配置文件了，我这里写的多了点，只做测试的话，可以直接看下面的搭建过程

# 搭建过程

### 1. 准备好 gitlab 以及程序代码

1. 查看自己 gitlab 的版本，我目前只测了 11.11 
2. 至少保证 [app.py] 可以成功运行

### 2. 注册 [gitlab-runner](https://docs.gitlab.com/runner/install/)

至少需要一个 runner，用来运行测试，需要使用 docker 作 executor，以将 MySQL 和 redis 运行为 services

对其他的 job 来说，也可以使用其他的 runner

注意，官方文档[这个地方](https://docs.gitlab.com/ee/ci/docker/using_docker_images.html#register-docker-runner)有错误，注册 runner 时添加 service 的参数应该是`--docker-service mysql:latest` 而不是 `--docker-mysql latest`

### 3. 准备数据库文件和测试用例

即 [init_db.sql]，[unit] 和 [mock]

这些可能是最麻烦的部分，当然最初可以简单写，跑通之后再完善

### 4. 配置 [.gitlab-ci.yml]，以及项目环境变量

单纯只看测试的话，可以只配一个 job，也就是 `test` 的部分

```yaml
# .gitlab-ci.yml

test:
  image: python:3.6
  services:
    - mysql:latest
    - redis:latest
  script:
    - pip install -r requirements.txt # 安装依赖
    - python init_db.py               # 初始化数据库
    - pytest unit --cov=app           # 单元测试
    - pytest mock --cov=app           # API测试
  tags:
    - docker-py36                     # 指定自己创建的 runner
```

[.gitlab-ci.yml]里东西要多一些，设置了三个 stages:
* test: 我们的测试就会在这里完成
* build: 使用 docker 的话，可以在这里打包镜像，推送给镜像仓库，其中需要的 registry 和账号密码等内容，可以在[这里](https://gitlab.com/help/ci/variables/README#variables)配置
* deploy: 部署的脚本，根据具体的 CD 方案来写

另外还多配置上了 pip 缓存，可以不用每次都重新下载，相关内容可以参考[这个文章](https://blog.zacharyjia.me/2017/04/06/gitlab-ci-docker-pip-cache/)

### 5. 运行

test job 我们并没有设置触发条件，于是使用默认条件：所有 branch 和 tag 操作都会触发

可以在原有项目库里新开一个分支，将 CI 配置提交上去，观察运行情况

# 优化和完善

整体流程还是依赖于 GitLab-CI 的，在基本的测试完成后，还有以下可完善的点：
* 将 code review 流程放到 CI 里，作为一个 manual 的 job，强制确认
* 将 CD 流程加进来，同样作为 manual job
* 将测试用例的部分，拆出去作为另一个单独的仓库，用 submodule 的方式关联起来，让 QA 补充测试用例
* docker 镜像的打包和推送，可以自动完成

[.gitlab-ci.yml]: .gitlab-ci.yml
[app.py]: app.py
[init_db.sql]: init_db.sql
[mock]: mock
[unit]: unit
[config]: config

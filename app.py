#!/usr/bin/env python
# coding=utf-8

import os
import time

import pymysql
import redis
from flask import Flask, request, g, jsonify, abort, redirect
from pymysql import escape_string

app = Flask(__name__)

# 选择配置文件
app.config.from_pyfile(
    os.path.join('config', os.environ.get('ENV_MODE', 'develop') + '.py'))

# 配置 redis
cache = redis.StrictRedis(host=app.config.get('REDIS_HOST', '127.0.0.1'),
                          port=app.config.get('REDIS_PORT', 6379))


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.before_request
def init_db():
    """初始化数据库连接"""
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PSWD'],
        db='test',
        cursorclass=pymysql.cursors.DictCursor)
    g.db = connection


@app.teardown_request
def close_db(response):
    """关闭数据库连接"""
    if hasattr(g, 'db'):
        g.db.close()
    return response


@app.route('/')
def index():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)


@app.route('/users')
def get_user_list():
    with g.db.cursor() as cursor:
        cursor.execute('select id, username from user')
        users = cursor.fetchall()
    return jsonify(users)


@app.route('/users/<username>')
def get_user(username):
    with g.db.cursor() as cursor:
        cursor.execute('select id, username from user where username = %s',
                       escape_string(username))
        user = cursor.fetchone()
    if user:
        return jsonify(user)
    else:
        abort(404)


@app.route('/users', methods=['POST'])
def add_user():
    username = request.form.get('username')[:40]
    if not username:
        abort(400, 'need username')
    try:
        with g.db.cursor() as cursor:
            cursor.execute('insert into user (username) values (%s)',
                           escape_string(username))
        g.db.commit()
    except pymysql.err.IntegrityError:
        abort(400, 'duplicate username')
    return redirect(f'/users/{username}')

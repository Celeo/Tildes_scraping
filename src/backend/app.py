from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from ..db import Comment, Topic


app = Flask(__name__)
app.config.from_mapping({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///../../data.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
CORS(app)
db = SQLAlchemy(app)


@app.route('/')
def index():
    return jsonify({
        'message': 'Index page'
    })


@app.route('/topics')
def topics():
    limit = request.args.get('limit', 100, type=int)
    after = request.args.get('after', 0, type=int)
    group = request.args.get('group')
    topics = (
        db.session.query(Topic)
        .filter(Topic.id > after)
    )
    if group:
        if group[0] != '~':
            group = '~' + group
        topics = topics.filter_by(group=group)
    topics = topics.limit(limit)
    return jsonify([topic.to_dict() for topic in topics])


@app.route('/topic/<int:topic_id>/comments')
def topic_comments(topic_id):
    limit = request.args.get('limit', 100, type=int)
    after = request.args.get('after', 0, type=int)
    comments = (
        db.session.query(Comment)
        .filter(Comment.topic_id == topic_id, Comment.id > after)
        .limit(limit)
    )
    return jsonify([comment.to_dict() for comment in comments])

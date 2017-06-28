from flask import Flask, abort, jsonify
from flask.ext.restful import Resource, reqparse, fields, marshal, request
from flask.ext.httpauth import HTTPBasicAuth
from app import api

auth = HTTPBasicAuth()

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Mick, Cheese, Pizza, Fruit, Tylenol',
        'done': False
     },

     {
         'id': 2,
         'title': u'Learn Python',
         'description': u'Need find a good Python',
         'done': False

     }
]

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}


@auth.get_password
def get_password(username):
    if username == "ding":
        return 'python'
    return None


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided', location='json')
        self.reqparse.add_argument('description', type=str, default="", location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'tasks': marshal(tasks, task_fields)}, 201

    def post(self):
        task = {
            'id': tasks[-1]['id']+1,
            'title': request.json['title'],
            'description': request.json['description'],
            'done': request.json['done']
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        if id == 0:
            return jsonify({'tasks': marshal(tasks, task_fields)})

        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort('404')
        return {'task[0]': marshal(task[0], task_fields)}, 201

    def put(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}

api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')

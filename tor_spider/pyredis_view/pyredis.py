import redis
from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
import json

app = Flask(__name__)

DB_CONNECTION_PARAMS = dict(
    host='localhost',
    port='6379',
    password='hardpass123',
)

r = redis.Redis(**DB_CONNECTION_PARAMS)


@app.route('/')
def main():
    list_values = [{k.decode(): v.decode() for k, v in r.hgetall(k).items()} for k in r.keys()]
    return render_template('index.html',
            list_values=list_values,
            keys=sorted(list_values[0].keys()),
            rows_count=len(list_values)
            )


@app.route('/export')
def export():
    res = request.args.get('res')
    file_name = 'export.{}'.format(res)
    list_values = [{k.decode(): v.decode() for k, v in r.hgetall(k).items()} for k in r.keys()]
    if res == 'json':
        with open(file_name, 'w') as f:
            json.dump(list_values, f)
        return send_file(file_name)
    elif res == 'csv':
        sorted_keys = sorted(list_values[0].keys())
        with open(file_name, 'w') as f:
            f.write(','.join(sorted_keys))
            for row in list_values:
                f.write(','.join(row[k] for k in sorted_keys))
        return send_file(file_name)
    return ''


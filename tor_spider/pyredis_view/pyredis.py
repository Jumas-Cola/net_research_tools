import redis
from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
import json
import re
import sqlite3
import os

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
    if os.path.isfile(file_name):
        os.remove(file_name)
    list_values = ({k.decode(): v.decode() for k, v in r.hgetall(k).items()} for k in r.keys())
    if res == 'json':
        with open(file_name, 'w') as f:
            json.dump([*list_values], f)
        return send_file(file_name)
    elif res == 'csv':
        sorted_keys = sorted(next(list_values).keys())
        with open(file_name, 'w') as f:
            f.write(','.join(sorted_keys) + '\n')
            for row in list_values:
                f.write(','.join((re.sub('\W', ' ', row[k]) if k in row else '') for k in sorted_keys) + '\n')
        return send_file(file_name)
    elif res == 'db':
        conn = sqlite3.connect(file_name)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE Export(
           id INT PRIMARY KEY,
           {});
        """.format(','.join('{} TEXT'.format(i) for i in next(list_values).keys())))

        for n, row in enumerate(list_values):
            heads, vals = ['id'], ['"{}"'.format(n)]
            for h, v in row.items():
                heads.append(h)
                vals.append('"{}"'.format(re.sub(r'"|\'', '', v)))

            cur.execute('INSERT INTO Export({}) VALUES ({});'.format(','.join(heads), ','.join(vals)))
        conn.commit()
        return send_file(file_name)
    return ''


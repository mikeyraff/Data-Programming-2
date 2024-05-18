# project: p4
# submitter: raffanti
# partner: none
# hours: 10

import pandas as pd
import re
import os
import time
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from flask import Flask, render_template, request, jsonify, Response, make_response

app = Flask(__name__)
df = pd.read_csv("main.csv")
num_subscribed = 0
donation_counts = {"A": 0, "B": 0}
ip_requests = {}
matplotlib.use('Agg')
counter = 0
A = 0
B = 0

@app.route('/')
def home():
    global counter, A, B
    counter += 1
    if counter <= 10:
        if counter % 2 == 0:
            version = 'A'
            with open("index_a.html") as f:
                html = f.read()
            html = html.replace('<a href="donate.html">', '<a href="donate.html?from=A">')
        else:
            version = 'B'
            with open("index_b.html") as f:
                html = f.read()
            html = html.replace('<a href="donate.html">', '<a href="donate.html?from=B">')
    else:
        if A > B:
            version = "A"
            with open("index_a.html") as f:
                html = f.read()
            html = html.replace('<a href="donate.html">', '<a href="donate.html?from=A">')
        else:
            version = "B"
            with open("index_b.html") as f:
                html = f.read()
            html = html.replace('<a href="donate.html">', '<a href="donate.html?from=B">')
    return html

@app.route('/browse.html')
def browse():
    table_html = df.to_html()
    return f"<html><body><h1>Browse Data</h1>{table_html}</body></html>"

@app.route('/donate.html')
@app.route('/donate.html')
def donate():
    from_version = request.args.get("from")
    global A, B
    if from_version == "A":
        A += 1
    elif from_version == "B":
        B += 1
    return "<html><body><h1>Donate</h1><p>Please consider donating to support our project.</p></body></html>"

@app.route('/email', methods=["POST"])
def email():
    global num_subscribed
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,8}$", email)) >= 1:
        with open("emails.txt", "a+") as f:
            f.write(email + "\n")
        num_subscribed += 1
        return jsonify(f"Thanks, your subscriber number is {num_subscribed}!")
    else:
        return jsonify("Invalid email address. Please be more careful.")

@app.route('/browse.json')
def browse_json():
    global ip_requests

    client_ip = request.remote_addr
    current_time = time.time()

    if client_ip in ip_requests and current_time - ip_requests[client_ip] < 60:
        response = make_response(jsonify({"error": "Too many requests. Please wait."}), 429)
        response.headers["Retry-After"] = "60"
        return response

    ip_requests[client_ip] = current_time
    data = df.to_dict(orient= 'records')
    return jsonify(data)

@app.route('/visitors.json')
def visitors_json():
    return jsonify(list(ip_requests.keys()))

@app.route('/dashboard_1.svg')
def dashboard_1():
    bins = int(request.args.get('bins', 50))
    fig, ax = plt.subplots()
    df['Founded'].hist(ax=ax, bins=bins)
    ax.set_xlabel('X-axis label')
    ax.set_ylabel('Y-axis label')
    ax.set_title('Dashboard 1')
    plt.tight_layout()
    output = BytesIO()
    plt.savefig(output, format='svg')
    plt.close(fig)
    output.seek(0)
    return Response(output, content_type='image/svg+xml')

@app.route('/dashboard_2.svg')
def dashboard_2():
    fig, ax = plt.subplots()
    df.plot(x='Founded', y='RevenueUSD billions', kind='scatter', ax=ax)
    ax.set_xlabel('X-axis label')
    ax.set_ylabel('Y-axis label')
    ax.set_title('Dashboard 2')
    plt.tight_layout()
    output = BytesIO()
    plt.savefig(output, format='svg')
    plt.close(fig)
    output.seek(0)
    return Response(output, content_type='image/svg+xml')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False)
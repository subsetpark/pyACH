#! /usr/bin/env python3

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, escape, make_response
import ach, pickle

app = Flask(__name__)
app.config.from_object(__name__)

ach.DEBUG = True

with open('ach_db', 'rb') as f:
    try:
        workspaces = pickle.load(f)
    except EOFError:
        workspaces = {}

def app_state():
    d = {}
    d['sessions'] = session['workspaces']
    d['session'] = session['current']
    d['evidences'] = {sn: {'sn': sn, 'content': e.content, 'credibility': e.cred(), 'relevance': e.rel()} 
                    for sn, e in current().evidences.items()}
    d['hypotheses'] = {sn: {'sn': sn, 'content': h.content} for sn, h in current().hypotheses.items()}
    d['matrix'] = {k: {h: w.consistency for h, w in v.items()} for k, v in current().matrix.items()}
    d['scores'] = {sn: current().get_score(sn) for sn, h in current().hypotheses.items()}
    return d

def current():
    return workspaces[session['current']]

@app.route("/flush")
def flush():
    workspaces.clear()
    session.clear()
    with open('ach_db', 'wb') as f:
        pickle.dump(workspaces, f)
    print(session and "No session")
    print(workspaces and "No workspaces")
    resp = make_response(jsonify(success=True))
    resp.set_cookie('session', expires=0)
    return resp

@app.route("/")
def index():
    if 'workspaces' not in session or session['current'] not in workspaces:
        new_session()
    with open('ach_db', 'wb') as f:
        pickle.dump(workspaces, f)

    return render_template("app.html", session=current().sn, 
                                       es=({'sn': e.sn, 'content': e.content} for e in current().evidences.values()), 
                                       hs=({'sn': h.sn, 'content': h.content} for h in current().hypotheses.values()))

@app.route("/new_session")
def new_session():
    if 'workspaces' not in session:
        session['workspaces'] = []
    workspace = ach.ACH()
    workspaces[workspace.sn] = workspace
    session['workspaces'].append(workspace.sn)
    session['current'] = workspace.sn
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))    

@app.route("/get_state")
def get_state():
    return jsonify(app_state())

@app.route("/hypo_score")
def hypo_score():
    h_score = current().get_score(request.args.get('hypo'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(h_score=h_score)
    return redirect(h_score)

@app.route("/add_hypothesis")
def add_hypo():
    h_sn = current().add_hypothesis()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/name_hypo")
def name_hypo():
    hypo = request.args.get('hypo')
    content = request.args.get('content')
    current().name_hypo(hypo, content)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/add_evidence")
def add_evidence():
    e_sn = current().add_evidence()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/name_evidence")
def name_evidence():
    current().name_evidence(request.args.get('evidence'), request.args.get('content'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/set_cred")
def set_cred():
    cred = request.args.get('cred')
    if cred == "low":
        level = ach.LOW
    elif cred == "medium":
        level = ach.MEDIUM
    elif cred == "high":
        level = ach.HIGH
    else:
        return jsonify(success=False)
    current().set_cred(request.args.get('evidence'), level)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/set_rel")
def set_rel():
    rel = request.args.get('rel')
    if rel == "low":
        level = ach.LOW
    elif rel == "medium":
        level = ach.MEDIUM
    elif rel == "high":
        level = ach.HIGH
    else:
        return jsonify(success=False)
    current().set_rel(request.args.get('evidence'), level)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/set_consistency")
def set_consistency():
    consistency = request.args.get('consistency')
    current().rate(request.args.get('h'), request.args.get('e'), consistency)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(app_state())
    return redirect(url_for('index'))

@app.route("/switch_session")
def switch_session():
    workspace_id = request.args.get('session')
    if workspace_id in session['workspaces']:
        session['current'] = workspace_id
        return jsonify(app_state())
    else:
        return jsonify(success=False)

if __name__ == "__main__":
    app.debug = True
    # import credentials
    app.secret_key = "credentials.key"
    app.run()
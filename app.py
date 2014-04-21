#! /usr/bin/env python3

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, escape
import ach, pickle

app = Flask(__name__)
app.config.from_object(__name__)

ach.DEBUG = True

def current():
    return workspaces[session['current']]

with open('ach_db', 'rb') as f:
    try:
        workspaces = pickle.load(f)
    except EOFError:
        workspaces = {}

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
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/get_hypotheses")
def get_hypotheses():
    if current().hypotheses:
        return jsonify({sn: {'sn': sn, 'content': h.content} for sn, h in current().hypotheses.items()})
    else:
        return jsonify({})

@app.route("/get_evidences")
def get_evidences():
    if current().evidences:
        return jsonify({sn: {'sn': sn, 'content': e.content, 'credibility': e.credibility, 'relevance': e.relevance} 
                    for sn, e in current().evidences.items()})

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
        return jsonify(h_sn=h_sn)
    return redirect(url_for('index'))

@app.route("/name_hypo")
def name_hypo():
    hypo = request.args.get('hypo')
    content = request.args.get('content')
    current().hypotheses[hypo].content = content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/add_evidence")
def add_evidence():
    e_sn = current().add_evidence()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(e_sn=e_sn)
    return redirect(url_for('index'))

@app.route("/name_evidence")
def name_evidence():
    current().name_evidence(request.args.get('evidence'), request.args.get('content'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/set_cred")
def set_cred():
    current().evidences[request.args.get('evidence')].credibility = request.args.get('cred', type=float) 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/set_rel")
def set_rel():
    current().evidences[request.args.get('evidence')].relevance = request.args.get('rel', type=float)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/set_consistency")
def set_consistency():
    current().rate(request.args.get('h'), request.args.get('e'), request.args.get('rating'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    return redirect(url_for('index'))

@app.route("/switch_session")
def switch_session():
    workspace_id = request.args.get('session')
    if workspace_id in session['workspaces']:
        session['current'] = workspaces[workspace_id]
        return jsonify(success=True)
    else:
        return jsonify(success=False)
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.debug = True
    # import credentials
    app.secret_key = "credentials.key"
    app.run()
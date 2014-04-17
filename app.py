from flask import Flask, render_template, request, jsonify, session, redirect, url_for, escape
import ach, pickle

app = Flask(__name__)
app.config.from_object(__name__)

ach.DEBUG = True
workspaces = {}

with open('ach_db', 'rb') as f:
    workspaces = pickle.load(f)

@app.route("/")
def index():
    if 'workspaces' not in session or session['current'] not in workspaces:
        new_session()
    current = workspaces[session['current']]
    with open('ach_db', 'wb') as f:
        pickle.dump(workspaces, f)

    return render_template("app.html", session=current.sn, 
                                       es=({'sn': e.sn, 'content': e.content} for e in current.evidences.values()), 
                                       hs=({'sn': h.sn, 'content': h.content} for h in current.hypotheses.values()))

@app.route("/new_session")
def new_session():
    if 'workspaces' not in session:
        session['workspaces'] = []
    workspace = ach.ACH()
    workspaces[workspace.sn] = workspace
    session['workspaces'].append(workspace.sn)
    session['current'] = workspace.sn
    return jsonify(success=True)

@app.route("/hypo_score")
def hypo_score():
    return jsonify(h_score=workspaces[session['current']].get_score(request.args.get('hypo')))

@app.route("/add_hypothesis")
def add_hypo():
    return jsonify(h_sn=workspaces[session['current']].add_hypothesis())

@app.route("/name_hypo")
def name_hypo():
    hypo = request.args.get('hypo')
    content = request.args.get('content')
    workspaces[session['current']].hypotheses[hypo].content = content
    return jsonify(success=True)

@app.route("/add_evidence")
def add_evidence():
    return jsonify(e_sn=workspaces[session['current']].add_evidence())

@app.route("/name_evidence")
def name_evidence():
    workspaces[session['current']].evidences[request.args.get('evidence')] = request.args.get('content')
    return jsonify(success=True)

@app.route("/set_cred")
def set_cred():
    workspaces[session['current']].evidences[request.args.get('evidence')].credibility = request.args.get('cred', type=float) 
    return jsonify(success=True)

@app.route("/set_rel")
def set_rel():
    workspaces[session['current']].evidences[request.args.get('evidence')].relevance = request.args.get('rel', type=float)
    return jsonify(success=True)

@app.route("/set_consistency")
def set_consistency():
    workspaces[session['current']].rate(request.args.get('h'), request.args.get('e'), request.args.get('rating'))
    return jsonify(success=True)

@app.route("/switch_session")
def switch_session():
    workspace_id = request.args.get('session')
    if workspace_id in session['workspaces']:
        session['current'] = workspaces[workspace_id]
        return jsonify(success=True)
    else:
        return jsonify(success=False)

if __name__ == "__main__":
    app.debug = True
    import credentials
    app.secret_key = credentials.key
    app.run()
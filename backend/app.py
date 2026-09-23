import os, uuid
from datetime import date
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app=Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"]=5*1024*1024
UPLOAD_DIR=os.path.join(os.path.dirname(__file__),"uploads")
os.makedirs(UPLOAD_DIR,exist_ok=True)
try:
    from supabase import create_client
    url,key=os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY")
    supabase=create_client(url,key) if url and key and "YOUR_PROJECT" not in url else None
except Exception:
    supabase=None

# Local fallback keeps the demo usable before DB setup. With Supabase configured, DB is authoritative.
students=[{"id":1,"name":"Vikash Gupta","email":"vikash@example.com","password":"demo1234","roll_no":"26","department":"CSE","cgpa":8.9,"graduation_year":2028,"phone":"","gender":"","skills":["C++","Python","Java","DSA"],"resume_url":"","linkedin_url":"","leetcode_url":"","github_url":"","city":"","bio":""}]
companies=[{"id":1,"name":"TCS","email":"hr@tcs.example","website":"https://www.tcs.com","industry":"IT Services","location":"Mumbai"},{"id":2,"name":"Infosys","email":"hr@infosys.example","website":"https://www.infosys.com","industry":"IT Services","location":"Pune"}]
jobs=[{"id":1,"company_id":1,"title":"Software Developer","description":"Build and maintain software applications.","package":"₹6 LPA","min_cgpa":7.5,"required_skills":["C++","Python"],"location":"Mumbai","deadline":"2026-09-30","openings":10},{"id":2,"company_id":2,"title":"Graduate Engineer","description":"Work on enterprise software projects.","package":"₹5.5 LPA","min_cgpa":7.0,"required_skills":["Python","Java"],"location":"Pune","deadline":"2026-10-05","openings":8}]
applications=[]

def select(table,fallback):
    if not supabase:return fallback
    try:return supabase.table(table).select("*").execute().data
    except Exception:return fallback
def insert(table,payload,fallback):
    if not supabase:
        payload=dict(payload); payload.setdefault("id",len(fallback)+1); fallback.append(payload); return payload
    return supabase.table(table).insert(payload).execute().data[0]
def update(table,field,value,payload,fallback):
    if supabase:
        try:
            d=supabase.table(table).update(payload).eq(field,value).execute().data
            if d:return d[0]
        except Exception:pass
    for x in fallback:
        if int(x["id"])==int(value):x.update(payload);return x
    return None
def find_student(student_id):
    return next((s for s in select("students",students) if int(s["id"])==int(student_id)),None)
def find_company(cid):
    return next((c for c in select("companies",companies) if int(c["id"])==int(cid)),None)
def find_job(jid):
    return next((j for j in select("jobs",jobs) if int(j["id"])==int(jid)),None)

@app.get("/api/health")
def health(): return jsonify({"success":True,"database_connected":supabase is not None})

@app.post("/api/auth/register")
def register():
    d=request.get_json() or {}; email=d.get("email","").strip().lower(); password=d.get("password","")
    if not email or not password or len(password)<6:return jsonify({"message":"Valid email and password (6+ characters) are required."}),400
    if any(s.get("email","").lower()==email for s in select("students",students)):return jsonify({"message":"Email already registered."}),409
    payload={"name":d.get("name","Student").strip(),"email":email,"password":password,"roll_no":d.get("roll_no",""),"department":d.get("department","CSE"),"cgpa":float(d.get("cgpa") or 0),"graduation_year":int(d.get("graduation_year") or 2028),"skills":d.get("skills",[]),"resume_url":"","linkedin_url":"","leetcode_url":"","github_url":"","phone":"","gender":"","city":"","bio":""}
    s=insert("students",payload,students)
    return jsonify({"success":True,"user":{"id":s["id"],"name":s["name"],"email":s["email"],"role":"student"}}),201

@app.post("/api/auth/login")
def login():
    d=request.get_json() or {}; email=d.get("email","").strip().lower(); password=d.get("password",""); role=d.get("role","student")
    if role=="admin" and email=="admin@example.com" and password=="admin1234":
        return jsonify({"success":True,"user":{"id":1,"name":"Placement Admin","email":email,"role":"admin"}})
    s=next((x for x in select("students",students) if x.get("email","").lower()==email and x.get("password")==password),None)
    if s:return jsonify({"success":True,"user":{"id":s["id"],"name":s["name"],"email":s["email"],"role":"student"}})
    return jsonify({"message":"Invalid email or password."}),401

@app.get("/api/jobs")
def get_jobs():
    cs=select("companies",companies); cmap={int(c["id"]):c for c in cs}; out=[]
    for j in select("jobs",jobs):
        x=dict(j); c=cmap.get(int(j["company_id"])); x["company_name"]=c["name"] if c else "Company"; out.append(x)
    return jsonify(out)

@app.get("/api/jobs/<int:job_id>")
def job_detail(job_id):
    j=find_job(job_id)
    if not j:return jsonify({"message":"Job not found"}),404
    x=dict(j); c=find_company(j["company_id"]); x["company_name"]=c["name"] if c else "Company"; return jsonify(x)

@app.post("/api/companies")
def add_company():
    d=request.get_json() or {}
    if not d.get("name"):return jsonify({"message":"Company name is required."}),400
    return jsonify(insert("companies",{"name":d["name"].strip(),"email":d.get("email",""),"website":d.get("website",""),"industry":d.get("industry",""),"location":d.get("location","")},companies)),201
@app.get("/api/companies")
def get_companies():return jsonify(select("companies",companies))

@app.post("/api/jobs")
def add_job():
    d=request.get_json() or {}
    try:
        p={"company_id":int(d["company_id"]),"title":d["title"].strip(),"description":d.get("description",""),"package":d.get("package",""),"min_cgpa":float(d["min_cgpa"]),"required_skills":d.get("required_skills",[]),"location":d.get("location",""),"deadline":d["deadline"],"openings":int(d["openings"])}
    except (KeyError,ValueError):return jsonify({"message":"Invalid job details."}),400
    return jsonify(insert("jobs",p,jobs)),201

@app.get("/api/students/<int:student_id>")
def profile(student_id):
    s=find_student(student_id)
    if not s:return jsonify({"message":"Student not found"}),404
    x=dict(s); x.pop("password",None); return jsonify(x)

@app.put("/api/students/<int:student_id>")
def edit_profile(student_id):
    d=request.get_json() or {}
    allowed=["name","roll_no","department","cgpa","graduation_year","phone","gender","skills","resume_url","linkedin_url","leetcode_url","github_url","city","bio"]
    p={k:d[k] for k in allowed if k in d}
    if "cgpa" in p:p["cgpa"]=float(p["cgpa"])
    if "graduation_year" in p:p["graduation_year"]=int(p["graduation_year"])
    s=update("students","id",student_id,p,students)
    if not s:return jsonify({"message":"Student not found"}),404
    s=dict(s);s.pop("password",None);return jsonify(s)

@app.post("/api/students/<int:student_id>/resume")
def upload_resume(student_id):
    s=find_student(student_id)
    if not s:return jsonify({"message":"Student not found"}),404
    f=request.files.get("resume")
    if not f or not f.filename:return jsonify({"message":"Choose a PDF resume."}),400
    if not f.filename.lower().endswith(".pdf"):return jsonify({"message":"Only PDF resume is allowed."}),400
    name=f"{student_id}_{uuid.uuid4().hex}_{secure_filename(f.filename)}"; path=os.path.join(UPLOAD_DIR,name); f.save(path)
    # Local demo URL; for production, move this upload to a Supabase Storage bucket.
    public=f"http://127.0.0.1:5000/uploads/{name}"
    update("students","id",student_id,{"resume_url":public},students)
    return jsonify({"success":True,"resume_url":public})

@app.get("/uploads/<path:name>")
def uploads(name):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_DIR,name,as_attachment=False)

@app.post("/api/applications")
def apply():
    d=request.get_json() or {}
    try:sid,jid=int(d["student_id"]),int(d["job_id"])
    except: return jsonify({"message":"Invalid student/job."}),400
    s,j=find_student(sid),find_job(jid)
    if not s or not j:return jsonify({"message":"Student or job not found."}),404
    apps=select("applications",applications)
    if any(int(a["student_id"])==sid and int(a["job_id"])==jid for a in apps):return jsonify({"message":"You have already applied for this job."}),409
    if float(s.get("cgpa",0))<float(j.get("min_cgpa",0)):return jsonify({"message":f"Not eligible. Minimum CGPA is {j['min_cgpa']}."}),400
    if str(j["deadline"])<date.today().isoformat():return jsonify({"message":"Application deadline has passed."}),400
    a=insert("applications",{"student_id":sid,"job_id":jid,"status":"Applied"},applications)
    return jsonify({"success":True,"message":"Application submitted successfully.","application":a}),201

@app.get("/api/applications")
def all_applications():
    apps=select("applications",applications); ss={int(s["id"]):s for s in select("students",students)}; js={int(j["id"]):j for j in select("jobs",jobs)}; cs={int(c["id"]):c for c in select("companies",companies)}
    out=[]
    for a in apps:
        j=js.get(int(a["job_id"]),{});s=ss.get(int(a["student_id"]),{});c=cs.get(int(j.get("company_id",0)),{})
        out.append({"id":a["id"],"student_id":a["student_id"],"job_id":a["job_id"],"status":a["status"],"student_name":s.get("name",""),"student_email":s.get("email",""),"student":{k:v for k,v in s.items() if k!="password"},"job_title":j.get("title",""),"company_id":j.get("company_id"),"company_name":c.get("name","")})
    return jsonify(out)

@app.put("/api/applications/<int:application_id>/status")
def status(application_id):
    d=request.get_json() or {}; allowed={"Applied","Shortlisted","Interview","Selected","Rejected"}
    if d.get("status") not in allowed:return jsonify({"message":"Invalid status"}),400
    a=update("applications","id",application_id,{"status":d["status"]},applications)
    if not a:return jsonify({"message":"Application not found"}),404
    return jsonify(a)

@app.get("/api/companies/<int:company_id>/applications")
def company_applications(company_id):
    apps=all_applications().get_json()
    return jsonify([a for a in apps if int(a.get("company_id") or 0)==company_id])

@app.get("/api/dashboard/stats")
def stats():
    a=select("applications",applications);return jsonify({"students":len(select("students",students)),"companies":len(select("companies",companies)),"jobs":len(select("jobs",jobs)),"applications":len(a),"selected":sum(1 for x in a if x.get("status")=="Selected")})
if __name__=="__main__":app.run(debug=True,port=5000)

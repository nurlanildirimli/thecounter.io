from flask import *
import sqlite3

app = Flask(__name__)

app.secret_key = "423"

@app.route("/")
@app.route("/index")
@app.route("/homepage")
def index():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    else:
        return render_template("index.html")

@app.post("/applylogin")
def loginoperation():
    #DB check to see if the user is available
    session["username"] = request.form["username"]
    return redirect(url_for("index"))

@app.route("/login")
def loginScreen():
    return render_template("index.html")

@app.route("/register")
def registrationScreen():
    return render_template("register.html")

@app.post("/applyLogin")
def loginOperation():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("posts.db")
    c = conn.cursor()

    c.execute("SELECT username,password FROM user WHERE username=? AND password=?", (username,password))
    user = c.fetchone()
    conn.close()
    if user == None:
        check = True
        return render_template("index.html",check = check)
    session["username"] = username
    return render_template("index.html",username=username, Message = "Welcome!!!" , title = "Home Page")

@app.post("/applyRegister")
def registerOperation():
    username = request.form["username"]
    password = request.form["password"]
    fullname = request.form["fullname"]
    email = request.form["email"]
    telNo = request.form["telNo"]
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()

    c.execute("SELECT username FROM user WHERE username=?", (username,))
    user = c.fetchone()

    if user != None:
        check = True
        conn.close()
        return render_template("register.html",check = check)

    c.execute("INSERT INTO user(username,password,email,fullname,telno) VALUES(?,?,?,?,?)", (username,password,email,fullname,telNo))
    conn.commit()
    conn.close()
    homelink = "/index"
    return render_template("registersuccesful.html",Message = "Registration Successfully Applied <br><a href=" + homelink + ">Return to the log in screen.</a> ", title = "Confirmation Message")


@app.route("/logout")
def logoutoperation():
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/myProfile")
def myProfileScreen():
    username = session["username"]

    conn = sqlite3.connect("posts.db")
    c = conn.cursor()

    c.execute("SELECT fullname,email,telno,password FROM user WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template("myprofile.html",username=username,password = user[3],fullname = user[0],email = user[1],telNo = user[2])

@app.route("/applyChanges")
def myProfileChange():
    username = session["username"]
    telNo = request.args.get("telNo")
    email = request.args.get("email")
    fullname = request.args.get("fullname")
    password = request.args.get("password")
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()

    c.execute("UPDATE user SET password=? , email=? , fullname=? , telno=? WHERE username=?",
              (password, email, fullname, telNo, username))

    conn.commit()
    conn.close()

    return render_template("index.html",username=username,Message = "Changes Successfully Applied", title = "Confirmation Message")

@app.route("/ads")
def ads():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT advertisement.*, category.cname FROM advertisement LEFT JOIN category ON advertisement.cid = category.cid WHERE advertisement.title IS NOT NULL AND advertisement.username = ?",(session["username"],))
    table = c.fetchall()
    conn.close()

    return render_template("advertisements.html", data=table)

@app.post("/addad")
def addad():
    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT cname FROM category")
    categories=c.fetchall()
    if(category not in categories):
        c.execute("INSERT INTO category(cname) VALUES (?)",(category,))

    c.execute("SELECT cid FROM category WHERE cname=(?)",(category,))
    catid =c.fetchone()
    conn.commit()
    conn.close()
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("INSERT INTO advertisement(title, description, cid, username) VALUES(?,?,?,?)", (title, description, catid[0],session["username"]))
    conn.commit()
    conn.close()
    return redirect(url_for('ads'))

@app.post("/deletead")
def deletead():
    ad_id= request.form["ad_id"]
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT * FROM advertisement WHERE isactive=(?) AND aid=(?)",("deactive",int(ad_id)))
    currentval=c.fetchone()
    conn.close()
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    if(currentval==None):
        c.execute("UPDATE advertisement SET isactive=(?) WHERE aid=(?) ",("deactive",int(ad_id)))
    else:
        c.execute("UPDATE advertisement SET isactive=(?) WHERE aid=(?) ", ("active", int(ad_id)))
    conn.commit()
    conn.close()
    return redirect(url_for('ads'))

@app.get("/getmatches")
def getmatches():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT advertisement.title, advertisement.description, user.fullname, category.cname FROM advertisement LEFT JOIN user ON advertisement.username = user.username LEFT JOIN category ON advertisement.cid=category.cid WHERE advertisement.title IS NOT NULL AND advertisement.isactive != 'deactive'")
    data=c.fetchall()

    conn.close()
    matches = ""
    q = request.args.get("q", None)
    keywords=q.split(" ")
    for q in keywords:
        if q != None:
            for ads in data:
                for i in range(3):
                    if q.lower() in ads[i].lower():
                        if(matches==""):
                            matches +=  ads[0]
                        else:
                            matches += ("," + ads[0])
                        matches+= ("," + ads[1])
                        matches+= ("," + ads[2])
                        matches+= ("," + ads[3])
                        break
    return matches

@app.post("/details")
def details():
    ad_details = request.form["addetails"]
    print("title:",ad_details)
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT user.fullname, user.telno, user.email, advertisement.title, advertisement.description, category.cname FROM user LEFT JOIN advertisement ON advertisement.username=user.username LEFT JOIN category ON advertisement.cid=category.cid WHERE advertisement.title=?",(ad_details,))
    details=c.fetchone()
    return render_template("details.html", data=details)

if __name__ == "__main__":
    app.run(debug=True, port=8001)

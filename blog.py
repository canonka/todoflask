from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

# kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.length(min = 4, max = 25)])
    email = StringField("Email Adresi",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Girin.")])
    username = StringField("Kullanıcı Adı",validators=[validators.length(min = 5, max = 35)])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin."),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

app = Flask(__name__)
app.secret_key = "ybblog"

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

#hakkında kısmını oluşturduk.
@app.route("/about")
def about():
    return render_template("about.html")

#kayıt olma register
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla kayıt oldunuz.","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

#login giriş işlemi
@app.route("/login",methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        #veritabanı sorgusu için
        cursor = mysql.connection.cursor()
        sorgu = "Select * From users where username = %s"
        #result şeklinde username'i kontrol edicez
        result = cursor.execute(sorgu,(username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yaptınız...","success")
                
                session["logged_in"] = True
                session["username"] = username

                
                
                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))
    return render_template("login.html",form=form)

#logout çıkış işlemi
@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız...","success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

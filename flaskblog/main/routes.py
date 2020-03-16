from flask import render_template, request, Blueprint
from flaskblog.models import Post,User


main = Blueprint('main',__name__)

#home route :
#@app.route('/')
#def index():
    # return render_template("home.html")

@main.route('/')
@main.route('/home')
#@login_required
def home():
         page = request.args.get('page',1,type=int)
         posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
         return render_template('home.html',title='Home Page',posts=posts,User=User)
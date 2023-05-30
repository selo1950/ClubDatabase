from myapp import create_app, db
from myapp.models import Base


app = create_app()

if __name__ == '__main__':
    
    db.init_app(app)
    #app.app_context().push()
    #db.create_all()
    app.run(debug=True)
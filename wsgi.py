import click, sys
from models import db, User
from app import app
from sqlalchemy.exc import IntegrityError

#flask init
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  #db.init_app(app)
  db.create_all()
  bob = User('bob', 'bob@mail.com', 'bobpass')
  jane = User('jane', 'jane@mail.com', 'janepass')
  john = User('john', 'john@mail.com', 'johnpass')
  db.session.add(bob)
  db.session.add(jane)
  db.session.add(john)
  db.session.commit()
  print(bob)
  print(jane)
  print(john)
  print('database intialized')

#flask get-user
@app.cli.command("get-user", help="Retrieves a User")
@click.argument('username', default='bob') #if a name is not given the name bob would be searched for
def get_user(username): #getting the user based on their username
  registered_user = User.query.filter_by(username = username).first() #the first instance of the name that matches the name stored in the variable "username" would be stored in the variable "registered_user"
  if not registered_user:
    print(f'{username} not found!') # the name that was being searched for is not in the database
    return
  print(registered_user)# if the person username is in the database their information is returned

#flask get-users
@app.cli.command('get-users')
def get_users():
  # gets all objects of a model
  users = User.query.all()
  print(users)

#flask change-email
@app.cli.command("change-email")
@click.argument('username', default='bob')
@click.argument('new_email', default='bob@mail.com')
def change_email(username, new_email):
  registered_user = User.query.filter_by(username=username).first()
  if not registered_user:
      print(f'{username} not found!')
      return
  registered_user.email = new_email
  db.session.add(registered_user)
  db.session.commit()
  print(registered_user)

#flask create-user
@app.cli.command('create-user')
@click.argument('username', default='rick')
@click.argument('email', default='rick@mail.com')
@click.argument('password', default='rickpass')
def create_user(username, email, password):
  newuser = User(username, email, password)
  try:
    db.session.add(newuser)
    db.session.commit()
  except IntegrityError as e:
    #let's the database undo any previous steps of a transaction
    db.session.rollback()
    # print(e.orig) #optionally print the error raised by the database
    print("Username or email already taken!") #give the user a useful message
  else:
    print(newuser) # print the newly created user
import click, sys
from models import db, User, Todo, Category, TodoCategory
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
  
  #add one task at a time
  bob.todos.append(Todo('wash car'))
  jane.todos.append(Todo('walk the dog'))
  jane.todos.append(Todo('water the plants'))
  john.todos.append(Todo('clean the house'))
  john.todos.append(Todo('cook for the family'))

  db.session.add(bob)
  db.session.add(jane)
  db.session.add(john)

  new_todo = bob.create_todo('walk the cat')
  db.session.add(new_todo)

  db.session.commit()

  print(bob)
  print(jane)
  print(john)
  print(bob, new_todo)

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

#flask delete-user
@app.cli.command('delete-user')
@click.argument('username', default='bob')
def delete_user(username):
  registered_user = User.query.filter_by(username=username).first()
  if not registered_user:
      print(f'{username} not found!')
      return
  db.session.delete(registered_user)
  db.session.commit()
  print(f'{username} deleted')

#flask get-user-todos
@app.cli.command('get-user-todos')
@click.argument('username', default='bob')
def get_user_todos(username):
  registered_user = User.query.filter_by(username = username).first()
  if not registered_user:
      print(f'{username} not found!')
      return
  print(registered_user.todos)

#flask get-all-todos
@app.cli.command('get-all-todos')
def get_all_todos():
  todos = Todo.query.all()
  print(todos)

#flask add-todo e.g. flask add-todo jane "wash the clothes"
@app.cli.command('add-todo')
@click.argument('username', default='bob')
@click.argument('text', default='wash car')
def add_task(username, text):
  registered_user = User.query.filter_by(username=username).first()
  if not registered_user:
      print(f'{username} not found!')
      return
  #new_todo = Todo(text)
  #registered_user.todos.append(new_todo)
  registered_user.create_todo(text)
  db.session.add(registered_user)
  db.session.commit()
  print("Todo added!")

#flask toggle-todo e.g. flask toggle-todo jane 3
@click.argument('todo_id', default=1)
@click.argument('username', default='bob')
@app.cli.command('toggle-todo')
def toggle_todo_command(todo_id, username):
  registered_user = User.query.filter_by(username=username).first()
  if not registered_user:
    print(f'{username} not found!')
    return

  todo = Todo.query.filter_by(id=todo_id, user_id=registered_user.id).first()
  if not todo:
    print(f'{username} has no todo id {todo_id}')

  todo.toggle()
  print(f'{todo.text} is {"completed" if todo.task_completed else "not completed"}!') 

#flask add-category
@click.argument('username', default='bob')
@click.argument('todo_id', default=6)
@click.argument('category', default='chores')
@app.cli.command('add-category', help="Adds a category to a todo")
def add_todo_category_command(username, todo_id, category):
  registered_user = User.query.filter_by(username=username).first()
  if not registered_user:
    print(f'{username} not found!')
    return

  res = registered_user.add_todo_category(todo_id, category)
  if not res:
    print(f'{username} has no todo id {todo_id}')
    return

  #print('Category added!')

# I also want to list the categories
#flask get-categories
@app.cli.command('get-categories')
def get_categories():
  # gets all objects of a model
  categories = Category.query.all()
  print(categories)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import app

db = SQLAlchemy(app)


class User(db.Model):
  __tablename__ ='user'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  #creates a relationship field to get the user's todos
  todos = db.relationship('Todo', backref='user', lazy=True, cascade="all, delete-orphan")
  #categories = db.relationship('Category', backref='user', lazy= 'joined') #to link Category and Todo tables together
  categories = db.relationship('Category', lazy='joined', back_populates='user')


  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.set_password(password)

  def set_password(self, password):
    """Create hashed password."""
    self.password = generate_password_hash(password, method='scrypt')

  def __repr__(self):
    return f'<User {self.id} {self.username} - {self.email}>'
  
  
  #"Research"
  def add_todo_category(self, todo_id, category_name):
        # Find the Todo by ID
        todo = next((todo for todo in self.todos if todo.id == todo_id), None)
        if not todo:
            return False  # No Todo with this ID found for the user

        # Check if the category already exists for this user
        category = Category.query.filter_by(user_id=self.id, text=category_name).first()
        if not category:
            # Create a new category
            category = Category(user_id=self.id, text=category_name)
            db.session.add(category)
            db.session.commit()

        # Check if the category is already associated with the todo
        if category not in todo.categories:
            todo.categories.append(category)
            db.session.commit()

        return True
  
#####################################################################################

class Todo(db.Model):
  __tablename__ ='todo'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #set userid as a foreign key to user.id # 1 to Many relationship from User to Todo.
  text = db.Column(db.String(255), nullable=False)
  task_completed = db.Column(db.Boolean, default=False)
  #categories = db.relationship('Category', secondary='todo_category', back_populates='todos')

  def toggle(self): # changed the status of task_completed from false to true and updates the database
    self.task_completed = not self.task_completed
    db.session.add(self)
    db.session.commit()

  def __init__(self, text):
      self.text = text

  '''
  def __repr__(self):
    return f'<Todo: {self.id} | {self.user.username} | {self.text} | { "Task Completed" if self.task_completed else "Task Not Completed" }>'
  #Note: the id is for the list of todos, not the user
  '''

  def __repr__(self):
    category_names = ', '.join([category.text for category in self.categories])
    return f'<Todo: {self.id} | {self.user.username} | {self.text} | { "completed" if self.task_completed else "not completed" } | categories [{category_names}]>' 
  
#####################################################################################

class TodoCategory(db.Model):
  __tablename__ ='todo_category'
  id = db.Column(db.Integer, primary_key=True)
  todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
  last_modified = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

  def __repr__(self):
    return f'<TodoCategory last modified {self.last_modified.strftime("%Y/%m/%d, %H:%M:%S")}>'
  
#####################################################################################

class Category(db.Model):
  __tablename__ ='category'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  text = db.Column(db.String(255), nullable=False)
  #user = db.relationship('User', backref=db.backref('categories', lazy='joined'))
  user = db.relationship('User', back_populates='categories')
  todos = db.relationship('Todo', secondary='todo_category', backref=db.backref('categories', lazy=True))

  def __init__(self, user_id, text):
    self.user_id = user_id
    self.text = text
  
  def __repr__(self):
    return f'<Category user:{self.user.username} - {self.text}>'
  
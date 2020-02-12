import sqlite3 as db

class Post:
    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

def insert_posts(post, cursor):
    insert_post_string = "insert into Posts(title, body, author) values(:title, :body, :author)"
    cursor.execute(insert_post_string, {'title': post.title, 'body': post.body, 'author': post.author})

def get_posts_by_author(cursor, author):
    posts = cursor.execute("select * from Posts where author=:author", {'author':author})
    return posts

connection = db.connect("my_database.db")
cursor = connection.cursor()

create_posts_table_string = '''
    CREATE TABLE Posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title text,
        body text, 
        author text
    );
'''
title = input("enter post title: ")
body = input("enter post body: ")
author = input("enter post author: ")
post = Post(title, body, author)
insert_posts(post, cursor)
connection.commit()

post = get_posts_by_author(cursor, "me")
print(post.fetchall())

cursor.close()
connection.close()
import sqlite3 as db

class Post:
    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author


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

insert_post_string = "insert into Posts(title, body, author) values(:title, :body, :author)"
cursor.execute(create_posts_table_string)
cursor.execute(insert_post_string, {'title':post.title,'body':post.body,'author':post.author})

connection.commit()
cursor.close()
connection.close()
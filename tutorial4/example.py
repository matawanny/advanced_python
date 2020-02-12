import requests
import sqlite3 as db

def getUserIdWithMostPosts(posts):
    postNumberForUsers = {}
    for post in posts:
        userId = post['userId']
        if (userId in postNumberForUsers):
            postNumberForUsers[userId] += 1
        else:
            postNumberForUsers[userId] = 1

    mostPostUserId = None
    mostPosts = 0
    for userId in postNumberForUsers:
        if(postNumberForUsers[userId] > mostPosts):
            mostPosts = postNumberForUsers[userId]
            mostPostUserId = userId
    return mostPostUserId

def getPostsByUserId(posts, userId):
    result=[]
    for post in posts:
        if(post['userId']==userId):
            result.append(post)
    return result

class Post:
    def __init__(self, title, body, author):
        self.title = title
        self.body = body

def insert_posts(post, cursor):
    insert_post_string = "insert into Posts(title, body) values(:title, :body)"
    cursor.execute(insert_post_string, {'title': post['title'], 'body': post['body']})

create_posts_table_string = '''
    CREATE TABLE Posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title text,
        body text
    );
'''

response = requests.get("https://jsonplaceholder.typicode.com/posts", timeout = 6,  verify=False)
connection = db.connect("my_database_1.db")

cursor = connection.cursor()


create_posts_table_string = '''
    CREATE TABLE Posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title text,
        body text
    );
'''
cursor.execute(create_posts_table_string)
connection.commit()

if(response.ok):
    posts=response.json()
    userId = getUserIdWithMostPosts(posts)
    print(userId)
    posts_for_user = getPostsByUserId(posts, userId)
    for post in posts_for_user:
        insert_posts(post, cursor)
    connection.commit()
    print(posts_for_user)
else:
    print("Error happened with status code ", response.status_code)


cursor.close()
connection.close()
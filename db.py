from pymongo import MongoClient
import pymongo


def connect_to_db():
    cluster = MongoClient(
        "mongodb+srv://moodify_main:Patanahi1$@cluster0.zhax9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
    )

    db = cluster['moodify']

    db['admins'].create_index([("email", pymongo.ASCENDING)], unique=True)

    return db
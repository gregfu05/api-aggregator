from app.db.mongo import get_db

def main():
    db = get_db()
    # cache indexes
    db.cache.create_index("expiresAt", expireAfterSeconds=0)
    db.cache.create_index("key", unique=True)
    # req_logs TTL (7 days)
    db.req_logs.create_index("createdAt", expireAfterSeconds=7*24*3600)
    print("Cache + logs indexes created.")

if __name__ == "__main__":
    main()

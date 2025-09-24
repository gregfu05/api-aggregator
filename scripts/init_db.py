from app.db.mongo import get_db

def main():
    db = get_db()
    db.cache.create_index("expiresAt", expireAfterSeconds=0)  # TTL
    db.cache.create_index("key", unique=True)
    print("Cache indexes created.")

if __name__ == "__main__":
    main()


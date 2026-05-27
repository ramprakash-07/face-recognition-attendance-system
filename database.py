import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Read MongoDB connection URI from environment variable for safety
# Set MONGO_URI in your environment before running, e.g.:
# $env:MONGO_URI = 'mongodb+srv://user:pass@cluster0.../'
# $env:MONGO_URI = ''

# MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI")
MONGO_URI = ''

_client = None
_db = None
_col = None

if MONGO_URI:
	try:
		_client = MongoClient(MONGO_URI)
		_db = _client.get_database("attendance_db")
		_col = _db.get_collection("records")
	except Exception as e:
		# Do not raise on import; surface error when trying to use DB
		print("Warning: could not initialize MongoDB client:", e)
		_client = None

def is_configured() -> bool:
	"""Return True if a MongoDB client was configured via MONGO_URI."""
	return _client is not None and _col is not None

def insert_attendance(name: str, label: int = None, timestamp: str = None, class_name: str = None, extra: dict = None) -> bool:
	"""
	Insert an attendance record into MongoDB.

	Returns True on success, False on failure or if DB not configured.
	"""
	if not is_configured():
		return False

	doc = {
		"name": name,
		"label": int(label) if label is not None else None,
		"class": class_name,
		"timestamp": timestamp,
	}
	if extra:
		doc.update(extra)

	try:
		_col.insert_one(doc)
		return True
	except PyMongoError as e:
		print("Error inserting attendance to MongoDB:", e)
		return False

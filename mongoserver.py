
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.fastmcp import FastMCP
from bson import ObjectId
import json
import os

# Initialize FastMCP server
mcp = FastMCP("mongodb")

# MongoDB connection - using environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://hemeshintern:root@cluster0.ru2tebj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client."""
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGODB_URI)
    return client


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format."""
    if doc is None:
        return None
    
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result


@mcp.tool()
async def list_databases() -> str:
    """List all databases in MongoDB instance."""
    try:
        client = get_client()
        databases = await client.list_database_names()
        return json.dumps({"databases": databases}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_collections(database: str) -> str:
    """List all collections in a database.
    
    Args:
        database: Name of the database
    """
    try:
        client = get_client()
        db = client[database]
        collections = await db.list_collection_names()
        return json.dumps({"collections": collections}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def find_documents(database: str, collection: str, limit: int = 10) -> str:
    """Find documents in a collection.
    
    Args:
        database: Name of the database
        collection: Name of the collection
        limit: Maximum number of documents to return (default: 10)
    """
    try:
        client = get_client()
        db = client[database]
        coll = db[collection]
        
        cursor = coll.find().limit(limit)
        documents = await cursor.to_list(length=limit)
        
        serialized_docs = [serialize_doc(doc) for doc in documents]
        
        return json.dumps({"documents": serialized_docs}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def insert_document(database: str, collection: str, document: str) -> str:
    """Insert a single document into a collection.
    
    Args:
        database: Name of the database
        collection: Name of the collection
        document: Document to insert as JSON string
    """
    try:
        client = get_client()
        db = client[database]
        coll = db[collection]
        
        doc_dict = json.loads(document)
        result = await coll.insert_one(doc_dict)
        
        return json.dumps({
            "inserted_id": str(result.inserted_id),
            "success": True
        }, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def update_document(database: str, collection: str, doc_id: str, update: str) -> str:
    """Update a document by ID.
    
    Args:
        database: Name of the database
        collection: Name of the collection
        doc_id: Document ID as string
        update: Fields to update as JSON string (e.g., {"name": "John", "age": 30})
    """
    try:
        client = get_client()
        db = client[database]
        coll = db[collection]
        
        update_dict = json.loads(update)
        result = await coll.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": update_dict}
        )
        
        return json.dumps({
            "modified_count": result.modified_count,
            "success": True
        }, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def delete_document(database: str, collection: str, doc_id: str) -> str:
    """Delete a document by ID.
    
    Args:
        database: Name of the database
        collection: Name of the collection
        doc_id: Document ID as string
    """
    try:
        client = get_client()
        db = client[database]
        coll = db[collection]
        
        result = await coll.delete_one({"_id": ObjectId(doc_id)})
        
        return json.dumps({
            "deleted_count": result.deleted_count,
            "success": True
        }, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"
if __name__ == "__main__":
    mcp.run()
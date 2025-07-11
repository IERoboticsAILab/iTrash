"""
Database module for iTrash system.
Handles MongoDB operations and data storage.
"""

import os
from datetime import datetime
from pymongo import MongoClient
from config.settings import MONGO_CONNECTION_STRING, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class DatabaseManager:
    """MongoDB database manager for iTrash system"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            if not MONGO_CONNECTION_STRING:
                print("Error: MongoDB connection string not found in environment variables")
                return False
            
            self.client = MongoClient(MONGO_CONNECTION_STRING)
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            self.is_connected = True
            print("Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            print("Disconnected from MongoDB")
    
    def get_acc_value(self):
        """Get current accumulator value from database"""
        if not self.is_connected:
            print("Not connected to database")
            return None
        
        try:
            cursor = self.collection.find({})
            if cursor.count() > 0:
                return cursor[0].get("acc", 0)
            else:
                # Initialize if no document exists
                self.collection.insert_one({"acc": 0})
                return 0
        except Exception as e:
            print(f"Error getting accumulator value: {e}")
            return None
    
    def update_acc(self, value):
        """Update accumulator value in database"""
        if not self.is_connected:
            print("Not connected to database")
            return False
        
        try:
            self.collection.update_one({}, {"$set": {"acc": value}}, upsert=True)
            print(f"Accumulator updated to: {value}")
            return True
        except Exception as e:
            print(f"Error updating accumulator: {e}")
            return False
    
    def increment_acc(self, increment=1):
        """Increment accumulator value"""
        if not self.is_connected:
            print("Not connected to database")
            return False
        
        try:
            self.collection.update_one({}, {"$inc": {"acc": increment}}, upsert=True)
            print(f"Accumulator incremented by: {increment}")
            return True
        except Exception as e:
            print(f"Error incrementing accumulator: {e}")
            return False
    
    def insert_image_data(self, image_base64, date, time, predicted_class, real_class="", person_thrown=True):
        """Insert image data with metadata"""
        if not self.is_connected:
            print("Not connected to database")
            return False
        
        try:
            # Create image collection if it doesn't exist
            image_collection = self.db["images"]
            
            document = {
                "image": image_base64,
                "date": date,
                "time": time,
                "predicted_class": predicted_class,
                "real_class": real_class,
                "person_thrown": person_thrown,
                "timestamp": datetime.now(),
                "classification_method": "hybrid"  # Could be "yolo", "gpt", or "hybrid"
            }
            
            result = image_collection.insert_one(document)
            print(f"Image data inserted with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting image data: {e}")
            return False
    
    def get_image_data(self, limit=100, date_filter=None):
        """Get image data from database"""
        if not self.is_connected:
            print("Not connected to database")
            return []
        
        try:
            image_collection = self.db["images"]
            
            # Build query
            query = {}
            if date_filter:
                query["date"] = date_filter
            
            # Get documents
            cursor = image_collection.find(query).sort("timestamp", -1).limit(limit)
            return list(cursor)
            
        except Exception as e:
            print(f"Error getting image data: {e}")
            return []
    
    def get_classification_stats(self, date_filter=None):
        """Get classification statistics"""
        if not self.is_connected:
            print("Not connected to database")
            return {}
        
        try:
            image_collection = self.db["images"]
            
            # Build query
            query = {}
            if date_filter:
                query["date"] = date_filter
            
            # Aggregate statistics
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$predicted_class",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = list(image_collection.aggregate(pipeline))
            
            # Convert to dictionary
            stats = {}
            for result in results:
                stats[result["_id"]] = result["count"]
            
            return stats
            
        except Exception as e:
            print(f"Error getting classification stats: {e}")
            return {}
    
    def get_daily_stats(self, days=7):
        """Get daily statistics for the last N days"""
        if not self.is_connected:
            print("Not connected to database")
            return []
        
        try:
            image_collection = self.db["images"]
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                            "class": "$predicted_class"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.date",
                        "classes": {
                            "$push": {
                                "class": "$_id.class",
                                "count": "$count"
                            }
                        },
                        "total": {"$sum": "$count"}
                    }
                },
                {"$sort": {"_id": -1}}
            ]
            
            results = list(image_collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old image data"""
        if not self.is_connected:
            print("Not connected to database")
            return False
        
        try:
            image_collection = self.db["images"]
            
            # Calculate cutoff date
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            # Delete old documents
            result = image_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            print(f"Cleaned up {result.deleted_count} old documents")
            return True
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return False
    
    def export_to_csv(self, filename, date_filter=None):
        """Export image data to CSV file"""
        if not self.is_connected:
            print("Not connected to database")
            return False
        
        try:
            import pandas as pd
            
            # Get image data
            data = self.get_image_data(limit=10000, date_filter=date_filter)
            
            if not data:
                print("No data to export")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Remove image data for CSV export (too large)
            if "image" in df.columns:
                df = df.drop("image", axis=1)
            
            # Export to CSV
            df.to_csv(filename, index=False)
            print(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False


# Global database instance
db_manager = DatabaseManager()

# Utility functions for backward compatibility
def update_acc(value):
    """Legacy function to update accumulator"""
    return db_manager.update_acc(value)

def insert_image(image, date, time, predicted, real="", person_thrown=True):
    """Legacy function to insert image data"""
    return db_manager.insert_image_data(image, date, time, predicted, real, person_thrown) 
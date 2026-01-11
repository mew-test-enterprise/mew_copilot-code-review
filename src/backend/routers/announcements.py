"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to JSON-serializable format"""
    if announcement and "_id" in announcement:
        announcement["id"] = str(announcement["_id"])
        del announcement["_id"]
    return announcement


@router.get("")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get all active announcements (within date range)"""
    current_time = datetime.utcnow().isoformat()
    
    # Find announcements where:
    # - No start_date OR start_date <= current_time
    # - expiration_date > current_time
    query = {
        "$and": [
            {
                "$or": [
                    {"start_date": {"$exists": False}},
                    {"start_date": None},
                    {"start_date": {"$lte": current_time}}
                ]
            },
            {"expiration_date": {"$gt": current_time}}
        ]
    }
    
    announcements = list(announcements_collection.find(query).sort("created_at", -1))
    return [serialize_announcement(a) for a in announcements]


@router.get("/all")
def get_all_announcements(username: str) -> List[Dict[str, Any]]:
    """Get all announcements for management (requires authentication)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    announcements = list(announcements_collection.find().sort("created_at", -1))
    return [serialize_announcement(a) for a in announcements]


@router.post("")
def create_announcement(
    message: str,
    expiration_date: str,
    username: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new announcement (requires authentication)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate expiration_date is required
    if not expiration_date:
        raise HTTPException(status_code=400, detail="Expiration date is required")
    
    # Validate dates format
    try:
        datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
        if start_date:
            datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    announcement = {
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date,
        "created_by": username,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = announcements_collection.insert_one(announcement)
    announcement["id"] = str(result.inserted_id)
    if "_id" in announcement:
        del announcement["_id"]
    
    return announcement


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    message: str,
    expiration_date: str,
    username: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing announcement (requires authentication)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate expiration_date is required
    if not expiration_date:
        raise HTTPException(status_code=400, detail="Expiration date is required")
    
    # Validate dates format
    try:
        datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
        if start_date:
            datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Find and update the announcement
    try:
        result = announcements_collection.update_one(
            {"_id": ObjectId(announcement_id)},
            {"$set": {
                "message": message,
                "start_date": start_date,
                "expiration_date": expiration_date,
                "updated_by": username,
                "updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        # Fetch and return the updated announcement
        announcement = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
        return serialize_announcement(announcement)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid announcement ID: {str(e)}")


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, username: str) -> Dict[str, str]:
    """Delete an announcement (requires authentication)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Delete the announcement
    try:
        result = announcements_collection.delete_one({"_id": ObjectId(announcement_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        return {"message": "Announcement deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid announcement ID: {str(e)}")

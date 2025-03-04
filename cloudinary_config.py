import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_photo(file, folder="horizon_afrika"):
    """
    Upload a photo to Cloudinary
    
    Args:
        file: File object to upload
        folder: Cloudinary folder to store the image (default: "horizon_afrika")
    
    Returns:
        dict: Dictionary containing the upload result including the URL
    """
    try:
        upload_result = cloudinary.config.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        return {
            "success": True,
            "url": upload_result.get('secure_url'),
            "public_id": upload_result.get('public_id')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def delete_photo(public_id):
    """
    Delete a photo from Cloudinary
    
    Args:
        public_id: The public ID of the image to delete
    
    Returns:
        dict: Dictionary containing the deletion result
    """
    try:
        result = cloudinary.config.uploader.destroy(public_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
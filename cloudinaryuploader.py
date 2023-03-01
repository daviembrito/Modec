import cloudinary
import cloudinary.uploader

class CloudinaryUploader():
    def __init__(self, cloud_name, key, secret):
        self.cloud_name = cloud_name
        self.key = key
        self.secret = secret
        self.__config()

    def __config(self):
        cloudinary.config(
            cloud_name = self.cloud_name,
            api_key = self.key,
            api_secret = self.secret
        )

    def upload(self, image_path, title="title"):
        return cloudinary.uploader.upload(image_path, public_id=title)["secure_url"]
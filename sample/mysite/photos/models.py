from django.db import models
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

class Photo(models.Model):
    photo = models.ImageField(upload_to='uploads/%Y/%m/%d/')

    photo_thumbnail = ImageSpecField(source='photo',
                            processors=[ResizeToFill(260,260)],
                            format='JPEG',
                            options={'quality': 85}
                            )

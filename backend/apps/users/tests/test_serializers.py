import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TestCase
from django.test.utils import override_settings
from PIL import Image
from users.models import User
from users.api.serializers import (
    AvatarSerializer,
    CreateUserSerializer,
    UserPasswordSerializer,
    UserDetailsSerializer,
    UserSerializer,
)


def generate_image_file() -> SimpleUploadedFile:
    image = BytesIO()
    Image.new('RGB', (200, 200)).save(image, 'png')
    image.seek(0)
    return SimpleUploadedFile('test_avatar.png',
                              image.getvalue(),
                              content_type='image/png')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestSerializers(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', 
        )
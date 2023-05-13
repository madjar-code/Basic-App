import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TestCase
from django.test.utils import override_settings
from PIL import Image

from users.models import User
from posts.models import Tag
from posts.api.serializers import (
    PostSerializer,
    TagSerializer,
)


def generate_image_file():
    image = BytesIO()
    Image.new('RGB', (200, 200)).save(image, 'png')
    image.seek(0)
    return SimpleUploadedFile('test_thumbnail.png',
                              image.getvalue(),
                              content_type='image/png')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestSerializers(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@test.com', password='test')
        self.tags = [Tag.objects.create(name=name)\
                     for name in ('Test1', 'Test2', 'Test3')]

        self.thumbnail = generate_image_file()
        self.post_serializer = PostSerializer(
            data={
                'title': 'Test post',
                'slug': 'test-post',
                'author': self.user,
                'thumbnail': self.thumbnail,
                'body': 'Test Body',
                'read_time': 5,
                'tags': self.tags,
            }
        )
        self.tag_serializer = TagSerializer(data={'name': 'Test Tag'})

    def test_post_serializer(self):
        """
        Post Serializer
        """
        serializer: PostSerializer = self.post_serializer
        self.assertTrue(serializer.is_valid())

        data = serializer.data

        self.assertCountEqual(
            data.keys(),
            ['title',
             'slug',
             'thumbnail',
             'body',
             'read_time'])
        self.assertEqual(data['title'], 'Test post')
        self.assertEqual(data['slug'], 'test-post')
        self.assertEqual(data['body'], 'Test Body')
        self.assertEqual(data['read_time'], 5)

    def test_tag_serializer(self):
        """
        Tag Serializer
        """
        serializer = self.tag_serializer

        self.assertTrue(serializer.is_valid())

        data = serializer.data

        self.assertCountEqual(data.keys(), ['name'])
        self.assertEqual(data['name'], 'Test Tag')
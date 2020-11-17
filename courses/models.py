from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class Subject(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	class Meta:
		ordering = ['title']

	def __str__(self):
		return self.title


class Course(models.Model):
	owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	overview = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ['-created']

	def __str__(self):
		return self.title


class Module(models.Model):
	course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.title


class Content(models.Model):
	"""
	Content model that represents the
	modules' contents, and define a generic relation to associate any kind of content

	Remember that you need three different fields to set up a generic relation. In your
	Content model, these are:
		• content_type: A ForeignKey field to the ContentType model
		• object_id: A PositiveIntegerField to store the primary key of the related object
		• item: A GenericForeignKey field to the related object combining the two previous fields
	"""
	module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in':(
																											'text',
																											'video',
																											'image',
																											'file')})
	object_id = models.PositiveIntegerField()
	item = GenericForeignKey('content_type', 'object_id')


class ItemBase(models.Model):
	"""
	An abstract model is a base class in which you define fields you want to include
	in all child models. Django doesn't create any database tables for abstract models.
	A database table is created for each child model, including the fields inherited from
	the abstract class and the ones defined in the child model.
	"""
	owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
	title = models.CharField(max_length=250)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.title


class Text(ItemBase):
	content = models.TextField()


class File(ItemBase):
	file = models.FileField(upload_to='files')


class Image(ItemBase):
	file = models.FileField(upload_to='images')


class Video(ItemBase):
	url = models.URLField()
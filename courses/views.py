from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Course

# Create your views here.

"""
This is the ManageCourseListView view. It inherits from Django's generic ListView.
You override the get_queryset() method of the view to retrieve only courses
created by the current user. To prevent users from editing, updating, or deleting
courses they didn't create, you will also need to override the get_queryset()
method in the create, update, and delete views. When you need to provide a specific
behavior for several class-based views, it is recommended that you use mixins.
"""


class ManageCourseListView(ListView):
	model = Course
	template_name = 'courses/manage/course/list.html'

	def get_queryset(self):
		qs = super().get_queryset()
		return qs.filter(owner=self.request.user)
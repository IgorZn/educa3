from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
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


class OwnerMixin(object):
	"""
	OwnerMixin implements the get_queryset() method,
	which is used by the views to get the base QuerySet. Your mixin will override this
	method to filter objects by the owner attribute to retrieve objects that belong to the
	current user (request.user).
	"""
	def get_queryset(self):
		qs = super().get_queryset()
		return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
	"""
	OwnerEditMixin implements the form_valid() method, which is used by views
	that use Django's ModelFormMixin mixin, that is, views with forms or model
	forms such as CreateView and UpdateView. form_valid() is executed when
	the submitted form is valid.
	"""
	def form_valid(self, form):
		form.instance.owner = self.request.user
		return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin):
	model = Course
	fields = ['subject', 'title', 'slug', 'overview']
	success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
	template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
	"""
	ManageCourseListView: Lists the courses created by the user. It inherits
	from OwnerCourseMixin and ListView. It defines a specific template_name
	attribute for a template to list courses.
	"""
	template_name = 'courses/manage/course/list.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
	"""
	CourseCreateView: Uses a model form to create a new Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses CreateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	pass


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
	"""
	CourseUpdateView: Allows the editing of an existing Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses UpdateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	pass


class CourseDeleteView(OwnerCourseMixin, DeleteView):
	"""
	CourseUpdateView: Allows the editing of an existing Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses UpdateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	template_name = 'courses/manage/course/delete.html'
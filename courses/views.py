from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Course

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

# Create your views here.

"""
This is the ManageCourseListView view. It inherits from Django's generic ListView.
You override the get_queryset() method of the view to retrieve only courses
created by the current user. To prevent users from editing, updating, or deleting
courses they didn't create, you will also need to override the get_queryset()
method in the create, update, and delete views. When you need to provide a specific
behavior for several class-based views, it is recommended that you use mixins.
"""

"""
following two mixins provided by django.contrib.auth to limit access to views:
	
	• 	LoginRequiredMixin: Replicates the login_required decorator's
		functionality.
	
	• 	PermissionRequiredMixin: Grants access to the view to users with
		a specific permission. Remember that superusers automatically have
		all permissions.
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


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
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
	permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
	"""
	CourseCreateView: Uses a model form to create a new Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses CreateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
	"""
	CourseUpdateView: Allows the editing of an existing Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses UpdateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
	"""
	CourseUpdateView: Allows the editing of an existing Course object.
	It uses the fields defined in OwnerCourseMixin to build a model
	form and also subclasses UpdateView. It uses the template defined
	in OwnerCourseEditMixin.
	"""
	template_name = 'courses/manage/course/delete.html'
	permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
	"""
	In this view:

	• get_formset(): You define this method to avoid repeating the code to build
	the formset. You create a ModuleFormSet object for the given Course object
	with optional data.

	• dispatch(): This method is provided by the View class. It takes an HTTP
	request and its parameters and attempts to delegate to a lowercase method
	that matches the HTTP method used. A GET request is delegated to the get()
	method and a POST request to post(), respectively. In this method, you use
	the get_object_or_404() shortcut function to get the Course object for the
	given id parameter that belongs to the current user. You include this code in
	the dispatch() method because you need to retrieve the course for both GET
	and POST requests. You save it into the course attribute of the view to make
	it accessible to other methods.

	• get(): Executed for GET requests. You build an empty ModuleFormSet
	formset and render it to the template together with the current
	Course object using the render_to_response() method provided by
	TemplateResponseMixin.

	• post(): Executed for POST requests.
		In this method, you perform the following actions:
			1. You build a ModuleFormSet instance using the submitted data.
			2. You execute the is_valid() method of the formset to validate all of
			its forms.
			3. If the formset is valid, you save it by calling the save() method. At
			this point, any changes made, such as adding, updating, or marking
			modules for deletion, are applied to the database. Then, you redirect
			users to the manage_course_list URL. If the formset is not valid,
			you render the template to display any errors instead.
	"""
	template_name = 'courses/manage/module/formset.html'
	course = None

	def get_formset(self, data=None):
		return ModuleFormSet(instance=self.course, data=data)

	def dispatch(self, request, pk):
		self.course = get_object_or_404(Course, id=pk, owner=request.user)
		return super().dispatch(request, pk)

	def get(self, request, *args, **kwargs):
		formset = self.get_formset()
		return self.render_to_response({'course': self.course, 'formset': formset})

	def post(self, request, *args, **kwargs):
		formset = self.get_formset(data=request.POST)
		if formset.is_valid():
			formset.save()
			return redirect('manage_course_list')
		return self.render_to_response({'course': self.course, 'formset': formset})
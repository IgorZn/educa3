from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Course

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content

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


class ContentCreateUpdateView(TemplateResponseMixin, View):
	"""
	This is the first part of ContentCreateUpdateView. It will allow you to create
	and update different models' contents. This view defines the following methods:

		• get_model(): Here, you check that the given model name is one of the four
		content models: Text, Video, Image, or File. Then, you use Django's apps
		module to obtain the actual class for the given model name. If the given
		model name is not one of the valid ones, you return None.

		• get_form(): You build a dynamic form using the modelform_factory()
		function of the form's framework. Since you are going to build a form for
		the Text, Video, Image, and File models, you use the exclude parameter
		to specify the common fields to exclude from the form and let all other
		attributes be included automatically. By doing so, you don't have to know
		which fields to include depending on the model.

		• dispatch(): It receives the following URL parameters and stores the
		corresponding module, model, and content object as class attributes:
			° module_id: The ID for the module that the content is/will be
			associated with.
			° model_name: The model name of the content to create/update.
			° id: The ID of the object that is being updated. It's None to create new
			objects.

		• get(): Executed when a GET request is received. You build the model
		form for the Text, Video, Image, or File instance that is being updated.
		Otherwise, you pass no instance to create a new object, since self.obj
		is None if no ID is provided.

		• post(): Executed when a POST request is received. You build the model
		form, passing any submitted data and files to it. Then, you validate it. If the
		form is valid, you create a new object and assign request.user as its owner
		before saving it to the database. You check for the id parameter. If no ID is
		provided, you know the user is creating a new object instead of updating an
		existing one. If this is a new object, you create a Content object for the given
		module and associate the new content with it.
	"""

	module = None
	model = None
	obj = None
	template_name = 'courses/manage/content/form.html'

	def get_model(self, model_name):
		if model_name in ['text', 'video', 'image', 'file']:
			return apps.get_model(app_label='courses', model_name=model_name)
		return None

	def get_form(self, model, *args, **kwargs):
		Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
		return Form(*args, **kwargs)

	def dispatch(self, request, module_id, model_name, id=None):
		self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
		self.model = self.get_model(model_name)

		if id:
			self.obj = get_object_or_404(self.model, id=id, owner=request.user)
		return super().dispatch(request, module_id, model_name, id)

	def get(self, request, module_id, model_name, id=None):
		form = self.get_form(self.model, instance=self.obj)
		return self.render_to_response({'form': form, 'object': self.obj})

	def post(self, request, module_id, model_name, id=None):
		form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

		if form.is_valid():
			obj = form.save(commit=False)
			obj.owner = request.user
			obj.save()
			if not id:
				# new content
				Content.objects.create(module=self.module, item=obj)
				return redirect('module_content_list', self.module.id)

		return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
	def post(self, request, id):
		content = get_object_or_404(Content, id=id, module__course__owner=request.user)
		module = content.module
		content.item.delete()
		content.delete()
		return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
	template_name = 'courses/manage/module/content_list.html'

	def get(self, request, module_id):
		module = get_object_or_404(Module, id=module_id, course__owner=request.user)
		return self.render_to_response({'module': module})
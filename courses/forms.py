from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

"""
You use the following parameters to build the formset:

	• 	fields: The fields that will be included in each form of the formset.
	
	• 	extra: Allows you to set the number of empty extra forms to display
		in the formset.
		
	• 	can_delete: If you set this to True, Django will include a Boolean field for
		each form that will be rendered as a checkbox input. It allows you to mark
		
the objects that you want to delete.
"""

ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description'], extra=2, can_delete=True)
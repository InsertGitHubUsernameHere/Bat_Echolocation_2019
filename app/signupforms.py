from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email

class SignUPForm(UserCreationForm):
	email = forms.EmailField(required=True)
	class Meta:
		model = User
		fields = (
			'username',
			'first_name',
			'last_name',
		 	'email',
		#	'organization',
			'password1',
			'password2',
		)

	def clean_username(self):
		user = self.cleaned_data['username']
		try:
			match = User.objects.get(username = user)
		except:
			return self.cleaned_data['username']
		raise forms.ValidationError("Username already exist, try different username")

	def clean_email(self):		
		email = self.cleaned_data['email']
		if User.objects.filter(email = email).exists():
			raise forms.ValidationError("Email already exist, try another email")
		return email
		
	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']
		if password1 and password2:
		 if password1 != password2:
				raise forms.ValidationError("password not match")
				

	def save(self, commit=True):
		user = super(SignUPForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']
		user.organization = self.cleaned_data['organization']

		if commit:
			user.save()

		return user	
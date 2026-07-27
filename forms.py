from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm


class UserCustForm(UserCreationForm):
    class Meta:
        model = UserCustModel
        fields = ['username','email','display_name','user_type','password1','password2']
        
class AuthForm(AuthenticationForm):
    class Meta:
        model = UserCustModel
        fields = ['username','password1']
        
class SkillForm(forms.ModelForm):
    class Meta:
        model = SkillModel
        fields = '__all__'
    
        
class RecuiterForm(forms.ModelForm):
    class Meta:
        model = RecuiterModel
        fields = '__all__'
        exclude = ['user']
        
        
class JobSeekerForm(forms.ModelForm):
    class Meta:
        model = JobSeekerModel
        fields = '__all__'
        exclude = ['user']
        
class JobpostForm(forms.ModelForm):
    class Meta:
        model = JobPostModel
        fields = '__all__'
        exclude = ['user']

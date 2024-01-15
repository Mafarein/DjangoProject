from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import Post, User

class MyUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm password'

        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': ''
        }

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password1')
        password = self.cleaned_data.get('password2')
        email_check = User.objects.filter(email=email)
        if email_check.exists():
            raise forms.ValidationError('This Email already exists')
        if len(password) < 5:
            raise forms.ValidationError('Your password should have more than 5 characters')
        return super(MyUserCreationForm, self).clean(*args, **kwargs)
        
        

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['created_by']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','username', 'email', 'bio']

class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']
        

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)


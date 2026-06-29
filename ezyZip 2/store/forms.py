from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Store, Product, Order, Message


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    store_name = forms.CharField(max_length=200, required=True)
    store_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Store.objects.create(
                owner=user,
                name=self.cleaned_data['store_name'],
                description=self.cleaned_data.get('store_description', '')
            )
        return user


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('name', 'description')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'price', 'stock', 'category', 'sku', 'image_url', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status', 'notes')


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your message...',
            }),
        }

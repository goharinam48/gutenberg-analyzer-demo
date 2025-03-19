from django import forms

class BookIDForm(forms.Form):
    book_id = forms.CharField(label='Book ID', max_length=20)
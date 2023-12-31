from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    sender_delim = forms.CharField()
    timestamp_delim = forms.CharField()
    custom_delim = forms.CharField()

    def clean_sender_delim(self):
        cleaned_data = self.cleaned_data
        delim = cleaned_data.get('sender_delim')
        if delim.strip().isalnum():
            raise form.ValidationError('Alphanumerical character can not be a delimiter.')
        return delim
    
    def clean_timestamp_delim(self):
        cleaned_data = self.cleaned_data
        delim = cleaned_data.get('timestamp_delim')
        if delim.strip().isalnum():
            raise form.ValidationError('Alphanumerical character can not be a delimiter.')
        return delim

from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    # sender_delim = forms.CharField()
    # timestamp_delim = forms.CharField()
    # custom_delim = forms.CharField()
    
    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     sender = cleaned_data.get('sender_delim')
    #     timestamp = cleaned_data.get('timestamp_delim')
    #     custom = cleaned_data.get('custom_delim')
    #     if sender.strip().isalnum():
    #         self.add_error('sender_delim', 'Alphanumerical character can not be a delimiter.')
    #     return cleaned_data
    
class DelimeterForm(forms.Form):
    sender_delim = forms.CharField()
    timestamp_delim = forms.CharField()
    custom_delim = forms.CharField()
    
    def clean(self):
        cleaned_data = self.cleaned_data
        sender = cleaned_data.get('sender_delim')
        timestamp = cleaned_data.get('timestamp_delim')
        custom = cleaned_data.get('custom_delim')
        if sender.strip().isalnum():
            self.add_error('sender_delim', 'Alphanumerical character can not be a delimiter.')
        return cleaned_data
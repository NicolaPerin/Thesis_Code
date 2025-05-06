from django import forms

class NexusFileUploadForm(forms.Form):
    metadata = forms.FileField(label="Select metadata (.hdr)")
    image = forms.FileField(label="Select image (.png)")


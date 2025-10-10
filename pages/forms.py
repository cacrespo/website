from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5})
    )
    validator = forms.CharField(
        max_length=50,
        label='¿Qué aderezo director técnico creó el "Paso a Paso"?',
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_validator(self):
        answer = self.cleaned_data.get("validator")
        if answer.lower() != "mostaza":
            raise forms.ValidationError("Respuesta incorrecta. ¡Inténtalo de nuevo!")
        return answer

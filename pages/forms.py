from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "your@email.com",
                "required": True,
                "type": "email",
            }
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5})
    )
    validator = forms.CharField(
        max_length=50,
        label='¿Qué aderezo director técnico creó el "Paso a Paso"?',
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if len(message) < 10:
            raise forms.ValidationError(
                "The message is too short! Ponele ganas maestro."
            )
        return message

    def clean_validator(self):
        answer = self.cleaned_data.get("validator")
        if answer.lower() != "mostaza":
            raise forms.ValidationError("Respuesta incorrecta my friend!")
        return answer

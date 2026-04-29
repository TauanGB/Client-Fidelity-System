from django import forms


class StyledClearableFileInput(forms.ClearableFileInput):
    template_name = "widgets/clearable_image_input.html"
    initial_text = "Arquivo atual"
    input_text = "Trocar arquivo"
    clear_checkbox_label = "Remover arquivo"

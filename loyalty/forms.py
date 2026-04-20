from django import forms

from core.image_specs import IMAGE_REQUIREMENTS, validate_image_requirements

from .models import LoyaltyCampaign, RewardRedemption


class LoyaltyCampaignForm(forms.ModelForm):
    reward_image = forms.FileField(
        required=False,
        help_text=IMAGE_REQUIREMENTS["reward_image"].help_text,
        widget=forms.ClearableFileInput(attrs={"accept": ".png,.jpg,.jpeg,.webp"}),
    )

    class Meta:
        model = LoyaltyCampaign
        fields = [
            "name",
            "description",
            "required_purchases",
            "reward_name",
            "reward_description",
            "reward_image",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "reward_description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_reward_image(self):
        return validate_image_requirements(self.cleaned_data.get("reward_image"), "reward_image")


class RewardRedemptionForm(forms.ModelForm):
    class Meta:
        model = RewardRedemption
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Observações do resgate"}),
        }

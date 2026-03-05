from django import forms
from .models import MenuCategory, MenuItem


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'
        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        
        # Determine restaurant from instance if not provided
        if not restaurant and self.instance and self.instance.pk:
            restaurant = self.instance.restaurant
        
        if restaurant:
            # Filter categories to only show those for this restaurant
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=restaurant)


from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'postal_code', 'city', 'shipping_zone', 'payment_method', 
                  'bkash_number', 'transaction_id']
        widgets = {
            'payment_method': forms.RadioSelect,
            'phone': forms.TextInput(attrs={'maxlength': '11', 'pattern': '[0-9]{11}', 'placeholder': '01XXXXXXXXX'}),
            'bkash_number': forms.TextInput(attrs={'maxlength': '11', 'pattern': '[0-9]{11}', 'placeholder': '01XXXXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['bkash_number'].required = False
        self.fields['transaction_id'].required = False
        
        # Make these fields required (they should already be, but explicit is better)
        self.fields['first_name'].required = True
        self.fields['phone'].required = True
        self.fields['address'].required = True
        self.fields['postal_code'].required = True
        self.fields['city'].required = True

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone) != 11:
                raise forms.ValidationError("Phone number must be exactly 11 digits.")
        return phone

    def clean_bkash_number(self):
        bkash_number = self.cleaned_data.get('bkash_number')
        if bkash_number:
            if not bkash_number.isdigit():
                raise forms.ValidationError("bKash/Nagad number must contain only digits.")
            if len(bkash_number) != 11:
                raise forms.ValidationError("bKash/Nagad number must be exactly 11 digits.")
        return bkash_number

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        bkash_number = cleaned_data.get('bkash_number')
        transaction_id = cleaned_data.get('transaction_id')

        # If payment method is bKash or Nagad, require bkash_number and transaction_id
        if payment_method in ['bkash', 'nagad']:
            if not bkash_number:
                self.add_error('bkash_number', 'This field is required for bKash/Nagad payment.')
            if not transaction_id:
                self.add_error('transaction_id', 'Transaction ID is required for bKash/Nagad payment.')

        return cleaned_data


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Article, Order

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "nama@email.com"}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"placeholder": "Nama lengkap"}))

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Buat username",
            "password1": "Minimal 8 karakter",
            "password2": "Ulangi password",
        }
        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs.update({"placeholder": placeholder})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "description", "price", "stock", "image", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nama produk"}),
            "description": forms.Textarea(attrs={"placeholder": "Deskripsi produk...", "rows": 5}),
            "price": forms.NumberInput(attrs={"placeholder": "Harga dalam Rupiah"}),
            "stock": forms.NumberInput(attrs={"placeholder": "Jumlah stok"}),
        }
        labels = {
            "name": "Nama Produk",
            "category": "Kategori",
            "description": "Deskripsi",
            "price": "Harga (Rp)",
            "stock": "Stok",
            "image": "Foto Produk",
            "is_active": "Tampilkan di marketplace",
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "excerpt", "content", "thumbnail", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Judul artikel"}),
            "excerpt": forms.Textarea(attrs={"placeholder": "Ringkasan singkat artikel...", "rows": 3}),
            "content": forms.Textarea(attrs={"placeholder": "Isi artikel...", "rows": 15}),
        }
        labels = {
            "title": "Judul Artikel",
            "excerpt": "Ringkasan",
            "content": "Konten Artikel",
            "thumbnail": "Gambar Thumbnail",
            "is_published": "Publikasikan artikel",
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "shipping_address", "payment_method"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Nama lengkap penerima"}),
            "phone": forms.TextInput(attrs={"placeholder": "Nomor WhatsApp / Telepon aktif"}),
            "shipping_address": forms.Textarea(attrs={"placeholder": "Alamat lengkap pengiriman...", "rows": 4}),
            "payment_method": forms.RadioSelect(attrs={"class": "payment-radio"}),
        }
        labels = {
            "full_name": "Nama Penerima",
            "phone": "Nomor Telepon / WhatsApp",
            "shipping_address": "Alamat Pengiriman",
            "payment_method": "Metode Pembayaran",
        }


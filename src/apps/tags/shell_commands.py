(ecommerce) PS D:\ProjectsPyCharm\ecommerce\src> python manage.py shell
Python 3.6.2 (v3.6.2:5fd33b5, Jul  8 2017, 04:14:34) [MSC v.1900 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from apps.tags.models import Tag
>>> Tag.objects.all()
<QuerySet [<Tag: T shirt>, <Tag: TShirt>, <Tag: T-shirt>, <Tag: red>, <Tag: black>]>
>>> Tag.objects.last()
<Tag: black>
>>> black = Tag.objects.last()
>>> black.title
'black'
>>> black.slug
'black'
>>> black.active
True
>>> black.products
<django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x047F52D0>
>>> black.products.all()
<ProductQuerySet [<Product: T-Shirt>, <Product: Hat>, <Product: T-Shirt>]>
>>> black.products.all().first
<bound method QuerySet.first of <ProductQuerySet [<Product: T-Shirt>, <Product: Hat>, <Product: T-Shirt>]>>
>>> black.products.all().first()
<Product: T-Shirt>
>>> exit()
(ecommerce) PS D:\ProjectsPyCharm\ecommerce\src> python manage.py shell
Python 3.6.2 (v3.6.2:5fd33b5, Jul  8 2017, 04:14:34) [MSC v.1900 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from products.models import Product
>>> qs = Product.objects.all()
>>> qs
<ProductQuerySet [<Product: T-Shirt>, <Product: Hat>, <Product: Supercomputer>, <Product: T-Shirt>, <Product: Lorem ipsum>]>
>>> tshirt = qs.first(
... )
>>> tshirt
<Product: T-Shirt>
>>> tshirt.title
'T-Shirt'
>>> tshirt.description
'This is an awesome shirt. Buy it :)'
>>> tshirt.tag
Traceback (most recent call last):
  File "<console>", line 1, in <module>
AttributeError: 'Product' object has no attribute 'tag'
>>> tshirt.tag_set
<django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x045285B0>
>>> tshirt.tag_set.all()
<QuerySet [<Tag: T shirt>, <Tag: TShirt>, <Tag: T-shirt>, <Tag: red>, <Tag: black>]>
>>> tshirt.tag_set.filter(title__iexact='Black')
<QuerySet [<Tag: black>]>
>>>
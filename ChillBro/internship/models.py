from django.db import models

# Create your models here.

class Transport(models.Model):
    Streams = (
        (1, 'Business Client'),
        (2, 'Individual'),
    )
    kind_of_stream=models.IntegerField(max_length=100,choices=Streams,default=1)
    travels_name=models.CharField(max_length=100)
    contact_person_name=models.CharField(max_length=100)
    contact_no=models.CharField(max_length=10)
    alternate_no=models.CharField(max_length=10)
    office_no=models.CharField(max_length=10)
    website_url=models.CharField(max_length=100)
    address_1=models.TextField(max_length=1000)
    address_2=models.TextField(max_length=1000)
    pin_code=models.CharField(max_length=6)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    addresses=(
        (1,"Home"),
        (2,"Office"),
        (3,"Others")
    )
    type_of_address=models.IntegerField(max_length=100,choices=addresses,default=1)
    send_to=models.IntegerField(max_length=100,choices=((1,"All"),(2,"individual")))
    employee_name=models.CharField(max_length=100)
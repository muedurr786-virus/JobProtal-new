from django.db import models
from django.contrib.auth.models import AbstractUser


class UserCustModel(AbstractUser):
    User =[
        ('Recuiter','Recuiter'),
        ('JobSeeker','JobSeeker')
    ]
    
    
    display_name = models.CharField(null=True, max_length=50)
    user_type = models.CharField(choices=User, max_length=50)

class SkillModel(models.Model):
    name = models.CharField(null=True, max_length=50, unique=True)


class RecuiterModel(models.Model):
    user = models.OneToOneField(UserCustModel, on_delete=models.CASCADE)
    company = models.CharField(null=True, max_length=50)
    address = models.TextField(null=True)
    phone = models.CharField(null=True, max_length=50)
    skill = models.CharField(null=True, max_length=50)
    image = models.ImageField(null=True, upload_to='media/image')


class JobSeekerModel(models.Model):
    user = models.OneToOneField(UserCustModel, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=50)
    address = models.TextField(null=True)
    phone = models.CharField(null=True, max_length=50)
    skill = models.CharField(null=True, max_length=50)
    image = models.ImageField(null=True, upload_to='media/image')
    resume = models.FileField(null=True, upload_to='media/resume')

class JobPostModel(models.Model):
    Category =[
        ('Full Time','Full Time'),
        ('Half Time','Half Time'),
        ('Remote Job','Remote Job')
    ]
    
    user = models.ForeignKey(UserCustModel, on_delete=models.CASCADE)
    titel = models.CharField(null=True, max_length=50)
    number_opening = models.IntegerField(null=True)
    category = models.CharField(null=True, max_length=50,choices=Category)
    skill_set = models.ManyToManyField(SkillModel)

class AppliedModel(models.Model):
    
    Status=[
        ('Pending','Pending'),
        ('Shor List','Shor List'),
        ('Reject','Reject'),
    ]
    
    job_post = models.ForeignKey(JobSeekerModel, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPostModel, on_delete=models.CASCADE)
    status =models.CharField(choices=Status, max_length=50)


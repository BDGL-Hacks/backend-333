from django.db import models
from django.contrib.auth.models import User


# Additional information about users that is not needed at registration
class User_Profile(models.Model):
    # Should be set to "M" or "F"
    gender = models.CharField(max_length=1, null=True)

    # Need to figure this out
    profile_picture = None


class Person(models.Model):
    # Built-in Django user
    # See https://docs.djangoproject.com/en/1.7/ref/contrib/auth/
    # for information about models.User
    user = models.OneToOneField(User)

    # Additional information about the user that is not needed at registration
    profile = models.ForeignKey(User_Profile)

    def __str__(self):
        return self.user.username


'''
We need to make a decision about whether to use the built-in django groups or
whether we should write our own.
'''
# # See https://docs.djangoproject.com/en/1.7/ref/contrib/auth/
# # for information about models.User
# class Group(models.Model):
#     # People in the group
#     group_members = models.ManyToMany(Person)

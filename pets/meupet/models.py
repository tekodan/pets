from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from users.models import OwnerProfile
from easy_thumbnails.files import get_thumbnailer

from . import functions


class PetManager(models.Manager):
    def get_lost_or_found(self, kind_id):
        return self.filter(kind__id=kind_id, status__in=[Pet.MISSING, Pet.FOUND])

    def get_for_adoption_adopted(self, kind_id):
        return self.filter(kind__id=kind_id, status__in=[Pet.FOR_ADOPTION, Pet.ADOPTED])


class Kind(models.Model):
    kind = models.TextField(max_length=100)

    def __str__(self):
        return self.kind


class Pet(models.Model):
    MISSING = 'MI'
    FOR_ADOPTION = 'FA'
    ADOPTED = 'AD'
    FOUND = 'FO'
    PET_STATUS = (
        (MISSING, 'Missing'),
        (FOR_ADOPTION, 'For Adoption'),
        (ADOPTED, 'Adopted'),
        (FOUND, 'Found'),
    )
    owner = models.ForeignKey(OwnerProfile)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500)
    kind = models.ForeignKey(Kind, null=True)
    status = models.CharField(max_length=2,
                              choices=PET_STATUS,
                              default=MISSING)
    profile_picture = models.ImageField(upload_to='pet_profiles')

    objects = PetManager()

    def get_absolute_url(self):
        return reverse('meupet:detail', kwargs={'id': self.id})

    def found_or_adopted(self):
        return self.status == self.ADOPTED or self.status == self.FOUND

    def change_status(self):
        self.status = self.FOUND if self.status == self.MISSING else self.ADOPTED
        thumb_path = get_thumbnailer(self.profile_picture)['pet_thumb'].file
        functions.update_image(thumb_path.name, self.get_status_display(), settings.STATICFILES_DIRS[0])
        self.save()

    def __str__(self):
        return self.name


class Photo(models.Model):
    pet = models.ForeignKey(Pet)
    image = models.ImageField(upload_to='pet_photos')
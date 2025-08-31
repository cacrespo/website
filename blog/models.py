from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.postgres import search

STATUS = ((0, "Draft"), (1, "Publish"))


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    text = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)
    categories = models.ManyToManyField("Category", related_name="posts")
    published_at = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    vector = models.GeneratedField(
        db_persist=True,
        expression=search.SearchVector("text", config="english"),
        output_field=search.SearchVectorField(),
    )


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    comment = models.TextField()
    link = models.URLField()

    def __str__(self):
        return self.title


class Activity(TimeStampedModel):
    details = models.TextField()
    link = models.URLField()
    link_hpv = models.TextField()

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return self.details

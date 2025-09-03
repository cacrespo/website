from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from pgvector.django import VectorField, CosineDistance
from sentence_transformers import SentenceTransformer
import numpy as np

STATUS = ((0, "Draft"), (1, "Publish"))

T = SentenceTransformer("distiluse-base-multilingual-cased-v2")


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
    embedding = VectorField(dimensions=512, editable=False)

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        title_vec = T.encode(self.title)
        text_vec = T.encode(self.text)
        # Normalize embeddings
        title_vec /= np.linalg.norm(title_vec)
        text_vec /= np.linalg.norm(text_vec)
        # Weighted average
        self.embedding = 0.7 * title_vec + 0.3 * text_vec
        self.embedding /= np.linalg.norm(self.embedding)
        super().save(*args, **kwargs)

    @classmethod
    def search(cls, q, dmax=0.5):
        literal_qs = cls.objects.filter(Q(title__icontains=q) | Q(text__icontains=q))
        semantic_qs = (
            cls.objects.alias(distance=CosineDistance("embedding", T.encode(q)))
            .filter(distance__lt=dmax)
            .order_by("distance")
        )
        return literal_qs.union(semantic_qs)


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
    embedding = VectorField(dimensions=512, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        title_vec = T.encode(self.title)
        comment_vec = T.encode(self.comment)
        # Normalize embeddings
        title_vec /= np.linalg.norm(title_vec)
        comment_vec /= np.linalg.norm(comment_vec)
        # Weighted average
        self.embedding = 0.7 * title_vec + 0.3 * comment_vec
        self.embedding /= np.linalg.norm(self.embedding)
        super().save(*args, **kwargs)

    @classmethod
    def search(cls, q, dmax=0.5):
        literal_qs = cls.objects.filter(Q(title__icontains=q) | Q(comment__icontains=q))
        semantic_qs = (
            cls.objects.alias(distance=CosineDistance("embedding", T.encode(q)))
            .filter(distance__lt=dmax)
            .order_by("distance")
        )
        return literal_qs.union(semantic_qs)


class Activity(TimeStampedModel):
    details = models.TextField()
    link = models.URLField()
    link_hpv = models.TextField()

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return self.details

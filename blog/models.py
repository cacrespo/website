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


class EmbeddableManager(models.Manager):
    def search(self, q, dmax=0.5):
        if not self.model._content_field:
            raise NotImplementedError(
                "Subclasses of Embeddable must define '_content_field'."
            )

        filter_query = Q(title__icontains=q) | Q(
            **{f"{self.model._content_field}__icontains": q}
        )
        literal_qs = self.get_queryset().filter(filter_query)
        semantic_qs = (
            self.get_queryset()
            .alias(distance=CosineDistance("embedding", T.encode(q)))
            .filter(distance__lt=dmax)
            .order_by("distance")
        )
        return literal_qs.union(semantic_qs)


class Embeddable(TimeStampedModel):
    embedding = VectorField(dimensions=512, editable=False, null=True)
    _content_field = None  # To be defined in subclasses

    objects = EmbeddableManager()

    class Meta:
        abstract = True

    def prepare_vector_information(self):
        if not self._content_field:
            raise NotImplementedError(
                "Subclasses of Embeddable must define '_content_field'."
            )
        content = getattr(self, self._content_field)
        title_vec = T.encode(self.title)
        content_vec = T.encode(content)
        # Normalize embeddings
        title_vec /= np.linalg.norm(title_vec)
        content_vec /= np.linalg.norm(content_vec)
        # Weighted average
        embedding = 0.7 * title_vec + 0.3 * content_vec
        embedding /= np.linalg.norm(embedding)
        return embedding

    def save(self, *args, **kwargs):
        self.embedding = self.prepare_vector_information()
        super().save(*args, **kwargs)


class Post(Embeddable):
    _content_field = "text"
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


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Article(Embeddable):
    _content_field = "comment"
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

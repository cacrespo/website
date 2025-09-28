from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from pgvector.django import VectorField, CosineDistance
import torch
from transformers import AutoTokenizer, AutoModel

# --- Transformer Setup ---
# Load tokenizer and model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
model = AutoModel.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
model.eval() # Set model to evaluation mode

# --- Pooling and Embedding Function ---
def mean_pooling(model_output, attention_mask):
    """Mean Pooling - Take attention mask into account for correct averaging."""
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def get_embedding_tensor(text: str) -> torch.Tensor:
    """Generates a sentence embedding tensor for a given text."""
    # Tokenize sentences
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
    # Perform pooling and return tensor
    return mean_pooling(model_output, encoded_input['attention_mask'])

# --- Model Definitions ---

STATUS = ((0, "Draft"), (1, "Publish"))

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

        # Get query embedding as a numpy array for pgvector
        q_embedding = get_embedding_tensor(q).squeeze().numpy()

        semantic_qs = (
            self.get_queryset()
            .alias(distance=CosineDistance("embedding", q_embedding))
            .filter(distance__lt=dmax)
            .order_by("distance")
        )
        return literal_qs.union(semantic_qs)


class Embeddable(TimeStampedModel):
    embedding = VectorField(dimensions=384, editable=False, null=True)
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

        # Get embeddings as tensors
        title_vec = get_embedding_tensor(self.title)
        content_vec = get_embedding_tensor(content)

        # Normalize embeddings
        title_vec = torch.nn.functional.normalize(title_vec, p=2, dim=1)
        content_vec = torch.nn.functional.normalize(content_vec, p=2, dim=1)

        # Weighted average
        embedding = 0.7 * title_vec + 0.3 * content_vec
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)

        return embedding.squeeze().numpy()

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
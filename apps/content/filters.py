from django_filters import rest_framework as filters
from .models import Article


class ArticleFilter(filters.FilterSet):
    """Filter for articles."""
    
    category = filters.CharFilter(field_name='category__slug')
    tag = filters.CharFilter(field_name='tags__name')
    content_type = filters.ChoiceFilter(choices=Article.CONTENT_TYPE_CHOICES)
    status = filters.ChoiceFilter(choices=Article.STATUS_CHOICES)
    confidence_rating = filters.ChoiceFilter(choices=Article.CONFIDENCE_RATING_CHOICES)
    is_editor_pick = filters.BooleanFilter()
    is_paywalled = filters.BooleanFilter()
    
    class Meta:
        model = Article
        fields = ['category', 'tag', 'content_type', 'status', 'confidence_rating', 'is_editor_pick', 'is_paywalled']

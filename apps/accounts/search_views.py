from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.forum.models import Post
from apps.marketplace.models import Listing
from apps.farms.models import Farm

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return Response({'results': [], 'query': q})

    results = []

    # forum posts
    for post in Post.objects.filter(title__icontains=q)[:5]:
        results.append({'type': 'post', 'id': post.id, 'title': post.title,
                        'subtitle': post.body[:80], 'url': '/dashboard/forum/'})

    # marketplace listings
    for listing in Listing.objects.filter(crop__icontains=q, status='active')[:5]:
        results.append({'type': 'listing', 'id': listing.id, 'title': f'{listing.crop} — grade {listing.grade}',
                        'subtitle': f'ksh {listing.price_per_kg}/kg', 'url': '/dashboard/marketplace/'})

    # farms
    for farm in Farm.objects.filter(owner=request.user, name__icontains=q)[:3]:
        results.append({'type': 'farm', 'id': farm.id, 'title': farm.name,
                        'subtitle': farm.location_name, 'url': '/dashboard/farms/'})

    return Response({'results': results, 'query': q})

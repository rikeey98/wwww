from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Subscriber
from .serializers import SubscriberSerializer

class SubscriberViewSet(viewsets.ViewSet):
    """
    Subscriber Management - Simple ReadOnly ViewSet
    Custom ViewSet to handle table without primary key
    """
    
    def get_queryset(self):
        """Get base queryset"""
        return Subscriber.objects.all()
    
    def list(self, request):
        """List all subscribers with filtering"""
        queryset = self.get_queryset()
        
        # Filter by service_id
        service_id = request.query_params.get('service_id')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        
        # Filter by email
        email = request.query_params.get('email')
        if email:
            queryset = queryset.filter(email=email)
            
        # Filter by domain
        domain = request.query_params.get('domain')
        if domain:
            queryset = queryset.filter(email__icontains=f'@{domain}')
        
        # Search functionality
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(service_id__icontains=search) | Q(email__icontains=search)
            )
        
        # Ordering
        ordering = request.query_params.get('ordering', 'service_id,email')
        if ordering:
            order_fields = [field.strip() for field in ordering.split(',')]
            queryset = queryset.order_by(*order_fields)
        
        # Simple pagination
        page = request.query_params.get('page', 1)
        page_size = int(request.query_params.get('page_size', 20))
        
        try:
            page = int(page)
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = queryset.count()
            paginated_queryset = queryset[start:end]
            
            serializer = SubscriberSerializer(paginated_queryset, many=True)
            
            return Response({
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'results': serializer.data
            })
        except (ValueError, TypeError):
            serializer = SubscriberSerializer(queryset, many=True)
            return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Individual retrieve not supported without primary key"""
        return Response(
            {
                'error': 'Individual subscriber retrieval is not supported.',
                'message': 'Please use filtering with service_id and email parameters.',
                'example': '/api/subscribers/?service_id=SERVICE001&email=user@example.com'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def by_service(self, request):
        """Get subscribers by service"""
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({'error': 'service_id parameter required'})
        
        subscribers = self.get_queryset().filter(service_id=service_id)
        serializer = self.get_serializer(subscribers, many=True)
        
        return Response({
            'service_id': service_id,
            'count': subscribers.count(),
            'subscribers': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """Get subscribed services by email"""
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'email parameter required'})
        
        subscribers = self.get_queryset().filter(email=email)
        serializer = self.get_serializer(subscribers, many=True)
        
        return Response({
            'email': email,
            'count': subscribers.count(),
            'services': [s.service_id for s in subscribers],
            'subscriptions': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Check subscription status"""
        service_id = request.query_params.get('service_id')
        email = request.query_params.get('email')
        
        if not service_id or not email:
            return Response({'error': 'service_id and email parameters required'})
        
        exists = self.get_queryset().filter(service_id=service_id, email=email).exists()
        return Response({
            'service_id': service_id,
            'email': email,
            'subscribed': exists
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Simple statistics"""
        queryset = self.get_queryset()
        
        return Response({
            'total_subscriptions': queryset.count(),
            'unique_emails': queryset.values('email').distinct().count(),
            'unique_services': queryset.values('service_id').distinct().count(),
            'services': list(queryset.values('service_id').annotate(
                count=Count('email')
            ).order_by('-count'))
        })
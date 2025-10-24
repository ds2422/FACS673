from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Summary
from .serializers import SummarySerializer, SummaryCreateSerializer, SummaryUpdateSerializer

class SummaryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        summaries = Summary.objects.filter(user=request.user)
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SummaryCreateSerializer(data=request.data)
        if serializer.is_valid():
            summary = serializer.save(user=request.user)
            return Response(SummarySerializer(summary).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SummaryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        return get_object_or_404(Summary, pk=pk, user=user)
    
    def get(self, request, pk):
        summary = self.get_object(pk, request.user)
        serializer = SummarySerializer(summary)
        return Response(serializer.data)
    
    def put(self, request, pk):
        summary = self.get_object(pk, request.user)
        serializer = SummaryUpdateSerializer(summary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        summary = self.get_object(pk, request.user)
        summary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PublicSummaryListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        summaries = Summary.objects.filter(is_public=True)
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)

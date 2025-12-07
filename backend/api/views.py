from rest_framework.views import APIView
from rest_framework.response import Response
from .authentication import FirebaseAuthentication
from .utils import process_inputs
from django.conf import settings
import google.generativeai as genai
from firebase_admin import firestore # Import firestore directly here
import datetime

# Configure API Key from settings
genai.configure(api_key=settings.GEMINI_API_KEY)

class SummarizeView(APIView):
    authentication_classes = [FirebaseAuthentication]

    def post(self, request):
        user_inputs = request.data.get('inputs', [])
        
        # 1. Process Inputs
        try:
            combined_text = process_inputs(user_inputs)
        except Exception as e:
            return Response({'error': f"Processing failed: {str(e)}"}, status=500)
        
        # 2. Use the Model found in your logs
        # Your logs showed 'gemini-2.0-flash' is available for you
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"Summarize the following content into a coherent summary:\n\n{combined_text}"
        
        try:
            # 3. Generate Content
            response = model.generate_content(prompt)
            
            if not response.text:
                return Response({'error': "Gemini returned empty response"}, status=500)

            summary_text = response.text
            
            # 4. Save to Firebase
            user_uid = request.user 
            if user_uid:
                # Initialize DB Connection here instead of settings
                db = firestore.client() 
                
                doc_ref = db.collection('users').document(str(user_uid)).collection('history').document()
                doc_ref.set({
                    'inputs': user_inputs,
                    'summary': summary_text,
                    'timestamp': datetime.datetime.now()
                })
            
            return Response({'summary': summary_text})
            
        except Exception as e:
            return Response({'error': f"AI Generation Failed: {str(e)}"}, status=500)

class HistoryView(APIView):
    authentication_classes = [FirebaseAuthentication]

    def get(self, request):
        try:
            user_uid = request.user
            # Initialize DB Connection here
            db = firestore.client()
            
            history_ref = db.collection('users').document(str(user_uid)).collection('history')
            
            # Order by timestamp descending (newest first)
            # Note: You might need to create a composite index in Firebase Console if this errors,
            # but for now let's just get the list.
            docs = history_ref.stream()
            
            history_data = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                history_data.append(data)
                
            return Response(history_data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
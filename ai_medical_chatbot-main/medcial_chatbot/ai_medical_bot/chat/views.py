from django.shortcuts import render
from datetime import timedelta
from .models import Patient, Conversation
from .ai_handler import AIHandler
from django.conf import settings

from django.shortcuts import render

def opening_view(request):
    # Your view logic here
    return render(request, 'template_name.html')


def chat_view(request):
    patient = Patient.objects.first()
    if not patient:
        patient = Patient.objects.create(
            first_name="Jessy",
            last_name="Mary",
            date_of_birth="1999-10-08",
            phone_number="8870699909",
            email="jessy.mary@vit.edu",
            medical_condition="Hypertension. The patient is on Lisinopril for blood pressure management.",
            medication_regimen="Lisinopril",
            last_appointment="2024-09-10 09:00",
            next_appointment="2024-09-25 10:00",
            doctor_name="Dr. Chittibabu"
        )

    # Get selected model
    selected_model = request.POST.get('model', 'google')  # Default to 'google'

    if selected_model == 'openai':
        api_key = settings.OPENAI_API_KEY
    else:
        api_key = settings.GEMINI_API_KEY

    ai_handler = AIHandler(api_key=api_key, model_choice=selected_model)

    if settings.LANGCHAIN_TRACING_V2:
        ai_handler.initialize_tracing(
            endpoint=settings.LANGCHAIN_ENDPOINT,
            project=settings.LANGCHAIN_PROJECT,
            langsmith_api_key=settings.LANGCHAIN_API_KEY
        )

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = ai_handler.generate_response(user_input=user_input, patient=patient)

        Conversation.objects.create(patient=patient, message=user_input, response=bot_response)

    conversation_history = Conversation.objects.filter(patient=patient).order_by('-timestamp')

    return render(request, 'chat/chat.html', {
        'patient': patient,
        'conversation_history': conversation_history
    })

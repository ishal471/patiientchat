import openai
import google.generativeai as genai
import markdown2
import re
from datetime import timedelta
import langsmith
from langchain.prompts import PromptTemplate
from langsmith import traceable
class AIHandler:
    def __init__(self, api_key, model_choice='google'):
        self.api_key = api_key
        self.model_choice = model_choice
        
        if self.model_choice == 'google':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        elif self.model_choice == 'openai':
            openai.api_key = self.api_key

    def generate_response(self, user_input, patient, conversation_summary):
        user_input_lower = user_input.lower()

        responses = []

        if "appointment" in user_input_lower and ("when" in user_input_lower or "date" in user_input_lower):
            responses.append(f"Your next appointment is on {patient.next_appointment.strftime('%B %d, %Y at %I:%M %p')}.")

        reschedule_match = re.search(r"reschedule.*by (\d+) days", user_input_lower)
        if reschedule_match:
            days_to_reschedule = int(reschedule_match.group(1))
            new_appointment_date = patient.next_appointment + timedelta(days=days_to_reschedule)
            patient.next_appointment = new_appointment_date
            patient.save()  
            responses.append(f"Your appointment has been rescheduled to {new_appointment_date.strftime('%B %d, %Y at %I:%M %p')}.")

        if "medical condition" in user_input_lower or "condition" in user_input_lower:
            responses.append(f"Here is information about your condition: {patient.medical_condition}")

        if responses:
            return " ".join(responses)

        # Use conversation summary instead of full history for LLM call
        prompt_template = PromptTemplate(
            input_variables=["user_input", "doctor_name", "conversation_summary"],
            template="""
                AI Role:
                You are a health assistant designed to interact with patients regarding their health and care plan. Your primary goal is to respond to health-related inquiries, assist with treatment and medication-related requests, and facilitate communication between the patient and their doctor.

                Conversation Summary:
                {conversation_summary}

                Patient message: "{user_input}"
                Doctor's Name: "{doctor_name}"
            """
        )
        
        rendered_prompt = prompt_template.format(
            user_input=user_input,
            doctor_name=patient.doctor_name,
            conversation_summary=conversation_summary
        )
        if self.model_choice == 'google':
            response = self.model.generate_content(rendered_prompt)
            return response.text
        elif self.model_choice == 'openai':
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": rendered_prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content

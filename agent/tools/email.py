from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import os
from agent.tools.evaluate import _evaluate

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']

def _gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body, thread_id=None):
    message = MIMEMultipart() #creates an empty email container
    message['to'] = to #sets the recipient and subject line
    message['subject'] = subject #adds the body text to the email
    message.attach(MIMEText(body, 'plain'))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode() #converts the whole email to a base64 string because Gmail API only accepts emails in that format
    service = _gmail_service() #gets your authenticated Gmail connection
    body = {'raw': raw}
    if thread_id:
        body['threadId'] = thread_id
    service.users().messages().send(userId='me', body=body).execute() # actually sends it through Gmail


def draft_cold_email(recipient, relevant_experiences, candidate_background, job_description, build_opportunities=None, tone=None):
    prompt = f"""
    Draft a cold email from Lakshita to {recipient} for a job opportunity.
    
    Write in this exact style — warm, specific, genuine, not salesy:
    "Dear Andrew, I hope you are doing well! I have been reading up on AssemblyAI's work, 
    and it is really interesting to see your team's work on cutting-edge speech models. 
    I'd love to contribute to audio intelligence systems in any way possible!"
    
    The email must:
    - Open with something specific about their company or work
    - Introduce Lakshita naturally (NYU MS CS, UCLA Cognitive Science + Economics background)
    - Reference these specific experiences: {relevant_experiences}
    - Mention what she could build or contribute: {build_opportunities}
    - End with a soft ask to connect, not a hard sell
    - Be 3-4 short paragraphs, conversational, not corporate
    
    Job Context: {job_description}
    Candidate Background: {candidate_background}
    Tone: {tone or "warm and genuine"}
    
    Return JSON with:
    - subject: email subject line
    - body: full email text
    """
    return _evaluate(prompt)

def draft_rejection_email(recipient, company_name , tone=None):
    prompt = f"""
    Draft a cold email from Lakshita to {recipient} for a job opportunity at {company_name}.
    
    Write in this exact style — warm, specific, genuine, not salesy:
    "Dear Arely, Thank you for letting me know, and thank you for the opportunity! While this was not the news I was hoping for, as I genuinely thought the interviews went quite well, I hope you keep me in mind for future opportunities! Sincerely,
    Lakshita "
    

    Tone: {tone or "warm and genuine"}
    
    Return JSON with:
    - subject: email subject line
    - body: full email text
    """
    return _evaluate(prompt)

def draft_offer_response(recipient, company_name, offer_details, tone=None):
    prompt = f"""
    Draft an offer acceptance email from Lakshita to {recipient} at {company_name}.
    
    Write in this exact style — warm, genuine, enthusiastic but professional:
    "Dear Arely, Thank you for letting me know, and thank you for the opportunity!"
    
    The email must include:
    - Genuine excitement and gratitude for the offer
    - Warmth toward the team she'll be joining
    - What she hopes to accomplish in her first month, 3 months, 6 months, and year
    - Close with enthusiasm for what's ahead
    
    Offer Details: {offer_details}
    Tone: {tone or "warm, grateful, excited"}
    
    Return JSON with:
    - subject: email subject line
    - body: full email text
    """
    return _evaluate(prompt)

def draft_schedule_call_email(recipient, company_name, purpose, availability=None, tone=None):
    prompt = f"""
    Draft an email from Lakshita to {recipient} at {company_name}.
    
    Write in this exact style — warm, genuine, not salesy:
    "Dear Arely, Thank you for letting me know, and thank you for the opportunity!"
    
    The email must include:
    - Genuine thank you for their response, mention it was helpful
    - Express interest in scheduling a quick call to learn more about {purpose}
    - Mention availability if provided: {availability or "suggest they reply with a time that works"}
    
    Tone: {tone or "warm and genuine"}
    
    Return JSON with:
    - subject: email subject line
    - body: full email text
    """
    return _evaluate(prompt)

def draft_referral_email(recipient, company_name, role, relationship_context, tone=None):
    prompt = f"""
    Draft a referral request email from Lakshita to {recipient} at {company_name}.
    
    Write in this exact style — warm, genuine, not pushy:
    "Dear Arely, Thank you for letting me know, and thank you for the opportunity!"
    
    The email must include:
    - Genuine thank you for their time and relationship: {relationship_context}
    - Specific role she is applying for: {role}
    - Soft, non-pushy ask for a referral
    
    Tone: {tone or "warm, grateful, not pushy"}
    
    Return JSON with:
    - subject: email subject line
    - body: full email text
    """
    return _evaluate(prompt)

def track_email_status(thread_id ):
    service = _gmail_service()
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    messages = thread['messages']
    if len(messages)>1:
        return {"status": "replied", "message_count": len(messages)}
    else:
        return {"status": "no response", "message_count": len(messages)}
    
def parse_email_response(email_content, thread_context=None):
    prompt = f"""
    Read the email  {email_content} and include any {thread_context}.
    
    
    Your role is as follows:
    - Tell what the sentiment is , whether positive, neutral, negative
    - What is their intent : interested, scheduling, rejecting, ghosting
    - what you recommend as next action: send followup, schedule call, move on
    
    Return JSON with:
    - sentiment: positive, neutral, or negative
    - intent: interested, scheduling, rejecting, or ghosting
    - next_action: send_followup, schedule_call, or move_on
    - reasoning: one sentence explanation
    """
    return _evaluate(prompt)

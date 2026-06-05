from agent.tools.evaluate import _evaluate

def login_to_portal(portal_url, portal_type=None):
    return {"status": "mock", "message": f"Would login to {portal_type or 'portal'} at {portal_url}"}

def fill_basic_fields(resume, portal_type=None):
    return {"status": "mock", "message": f"Would fill name, education, experience into {portal_type or 'portal'}"}

def generate_cover_letter(job_description, relevant_experiences, build_opportunities=None, company_name=None):
    prompt = f"""Write a cover letter for {company_name} using these experiences: {relevant_experiences} and this job description: {job_description}. Build opportunities: {build_opportunities}"""
    return _evaluate(prompt)

def answer_short_questions(questions, resume, company_context=None):
    prompt = f"""Answer these application questions: {questions}. Use this background: {resume}. Company context: {company_context}"""
    return _evaluate(prompt)

def attach_portfolio(role, available_links=None):
    return {"status": "mock", "message": f"Would attach portfolio links for {role}", "links": available_links or []}

def fill_demographic_fields(demographic_preferences=None):
    return {"status": "mock", "message": "Would fill demographic fields"}

def fill_salary_expectation(negotiation_position=None, salary_data=None):
    return {"status": "mock", "message": "Would fill salary expectation based on market data"}

def fill_availability(start_date, availability_notes=None):
    return {"status": "mock", "message": f"Would fill start date as {start_date}"}

def submit_application(portal_type, application_data):
    return {"status": "mock", "message": f"Would submit application to {portal_type}"}

def parse_confirmation(confirmation_page):
    return {"status": "mock", "message": "Would parse confirmation number and next steps", "confirmation": "MOCK-12345"}

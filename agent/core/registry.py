"""
Tool Registry for Job Application Agent
55 tools across 5 namespaces: search, evaluate, email, apply, document
"""

TOOL_REGISTRY = [

    # ─────────────────────────────────────────
    # NAMESPACE: search (14 tools)
    # ─────────────────────────────────────────
    {
        "name": "search_jobs",
        "namespace": "search",
        "description": "Search for jobs across LinkedIn, Indeed, Wellfound, YC and other job boards",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "job title or keywords"},
                "location": {"type": "string", "description": "city or remote"},
                "focus_area": {"type": "string", "description": "domain like healthtech or neurotech"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_key_people",
        "namespace": "search",
        "description": "Find recruiters, CEO, CTO, and relevant employees at a company for outreach",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "roles": {"type": "array", "items": {"type": "string"}, "description": "roles to find e.g. recruiter, CTO"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_company_pain_points",
        "namespace": "search",
        "description": "Research what problems the company is solving and what gaps they are hiring for",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "specific role being hired for"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_visa_sponsorship",
        "namespace": "search",
        "description": "Check if the company sponsors H1B or other work visas",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_funding",
        "namespace": "search",
        "description": "Find funding information and investors for a company",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_fundraising_stage",
        "namespace": "search",
        "description": "Find the current fundraising stage of a company (seed, series A, etc)",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_glassdoor_reviews",
        "namespace": "search",
        "description": "Fetch Glassdoor reviews, ratings, and employee sentiment for a company",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_press_coverage",
        "namespace": "search",
        "description": "Find recent press coverage and assess prestige and reputation of a company",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_salary_range",
        "namespace": "search",
        "description": "Find salary range for a role at a company from Levels.fyi, Glassdoor, or similar",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "job title"}
            },
            "required": ["company_name", "role"]
        }
    },
    {
        "name": "fetch_job_description",
        "namespace": "search",
        "description": "Fetch the full job description from a job posting URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "direct URL to the job posting"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_similar_roles",
        "namespace": "search",
        "description": "Find similar roles at other companies to understand the broader market",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "job title to search for"},
                "industry": {"type": "string", "description": "industry to focus on"}
            },
            "required": ["job_title"]
        }
    },
    {
        "name": "fetch_my_resume",
        "namespace": "search",
        "description": "Fetch the candidate's current resume and full background information",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_interview_process",
        "namespace": "search",
        "description": "Find what the interview loop looks like at a company from Glassdoor, Blind, or similar",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "job title"}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "search_career_trajectory",
        "namespace": "search",
        "description": "Research what career paths and opportunities open up after this role at this company",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "job title"}
            },
            "required": ["company_name", "role"]
        }
    },

    # ─────────────────────────────────────────
    # NAMESPACE: evaluate (14 tools)
    # ─────────────────────────────────────────
    {
        "name": "evaluate_career_trajectory",
        "namespace": "evaluate",
        "description": "Reason over fetched career trajectory data and assess long-term value of this role given candidate background",
        "input_schema": {
            "type": "object",
            "properties": {
                "trajectory_data": {"type": "object", "description": "output from search_career_trajectory"},
                "candidate_background": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["trajectory_data", "candidate_background"]
        }
    },
   {
    "name": "emotional_comfort",
    "namespace": "evaluate",
    "description": "Analyse the candidate's resume and provide emotional comfort — what makes them strong, what's marketable, what are the gaps, and what opportunities they can realistically pursue",
    "input_schema": {
        "type": "object",
        "properties": {
            "resume": {"type": "object", "description": "output from fetch_my_resume"}
        },
        "required": ["resume"]
    }
},
    {
        "name": "evaluate_resume_fit",
        "namespace": "evaluate",
        "description": "Score how well the candidate's resume matches the job description and identify gaps",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["job_description", "resume"]
        }
    },
    {
        "name": "evaluate_relevant_experiences",
        "namespace": "evaluate",
        "description": "Identify which specific experiences from the candidate's background to highlight for this role",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["job_description", "resume"]
        }
    },
    {
        "name": "suggest_build_opportunities",
        "namespace": "evaluate",
        "description": "SPAWNS SUBAGENT. Synthesize company pain points and candidate background to suggest what the candidate could build or contribute that would stand out",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "job title"},
                "pain_points": {"type": "object", "description": "output from search_company_pain_points"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["company_name", "role", "pain_points", "resume"]
        }
    },
    {
        "name": "evaluate_opportunity_stack_rank",
        "namespace": "evaluate",
        "description": "Compare this opportunity against other roles in the pipeline and previous roles held",
        "input_schema": {
            "type": "object",
            "properties": {
                "current_opportunity": {"type": "object", "description": "structured data about this role"},
                "pipeline": {"type": "array", "items": {"type": "object"}, "description": "list of other opportunities in tracker"}
            },
            "required": ["current_opportunity"]
        }
    },
    {
        "name": "evaluate_enjoyment_fit",
        "namespace": "evaluate",
        "description": "Assess whether this role aligns with the candidate's stated interests, values, and working style",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "glassdoor_data": {"type": "object", "description": "output from search_glassdoor_reviews"},
                "candidate_preferences": {"type": "object", "description": "candidate's known preferences and values"}
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "evaluate_first_year_plan",
        "namespace": "evaluate",
        "description": "Synthesize JD and company goals into a structured 1/3/6/12 month plan for this role",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "company_data": {"type": "object", "description": "aggregated company research"}
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "evaluate_interview_prep",
        "namespace": "evaluate",
        "description": "Generate targeted interview preparation steps based on the role, company, and candidate background",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "interview_process": {"type": "object", "description": "output from search_interview_process"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["job_description", "resume"]
        }
    },
    {
        "name": "evaluate_skill_gaps",
        "namespace": "evaluate",
        "description": "Identify what skills the candidate truly has vs what they need to build for this role",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["job_description", "resume"]
        }
    },
    {
        "name": "evaluate_skill_building_plan",
        "namespace": "evaluate",
        "description": "Generate a concrete plan to build the skills needed to thrive in the interview and role",
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_gaps": {"type": "object", "description": "output from evaluate_skill_gaps"},
                "timeline": {"type": "string", "description": "how much time before interview or start date"}
            },
            "required": ["skill_gaps"]
        }
    },
    {
        "name": "evaluate_red_flags",
        "namespace": "evaluate",
        "description": "Identify red flags in the JD, company data, or Glassdoor reviews worth flagging before investing time",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "glassdoor_data": {"type": "object", "description": "output from search_glassdoor_reviews"},
                "company_data": {"type": "object", "description": "aggregated company research"}
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "evaluate_negotiation_position",
        "namespace": "evaluate",
        "description": "Assess whether this is a reach, match, or safe bet, and what the candidate's negotiation leverage is",
        "input_schema": {
            "type": "object",
            "properties": {
                "resume_fit_score": {"type": "object", "description": "output from evaluate_resume_fit"},
                "salary_data": {"type": "object", "description": "output from search_salary_range"},
                "funding_stage": {"type": "object", "description": "output from search_fundraising_stage"}
            },
            "required": ["resume_fit_score"]
        }
    },
    {
        "name": "evaluate_team_quality",
        "namespace": "evaluate",
        "description": "Assess quality of peers, mentorship potential, and team caliber based on key people data",
        "input_schema": {
            "type": "object",
            "properties": {
                "key_people": {"type": "object", "description": "output from search_key_people"},
                "press_coverage": {"type": "object", "description": "output from search_press_coverage"}
            },
            "required": ["key_people"]
        }
    },
    {
        "name": "evaluate_work_life_balance",
        "namespace": "evaluate",
        "description": "Assess work life balance at the company based on Glassdoor, stage, and role signals",
        "input_schema": {
            "type": "object",
            "properties": {
                "glassdoor_data": {"type": "object", "description": "output from search_glassdoor_reviews"},
                "fundraising_stage": {"type": "object", "description": "output from search_fundraising_stage"},
                "job_description": {"type": "object", "description": "output from fetch_job_description"}
            },
            "required": ["glassdoor_data"]
        }
    },

    # ─────────────────────────────────────────
    # NAMESPACE: email (9 tools)
    # ─────────────────────────────────────────
    {
        "name": "draft_cold_email",
        "namespace": "email",
        "description": "Draft a personalized cold email to a specific person at a company referencing candidate's relevant experiences and the company's pain points",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "object", "description": "person to email from search_key_people"},
                "build_opportunities": {"type": "object", "description": "output from suggest_build_opportunities"},
                "relevant_experiences": {"type": "object", "description": "output from evaluate_relevant_experiences"},
                "tone": {"type": "string", "description": "e.g. warm, direct, formal"}
            },
            "required": ["recipient", "relevant_experiences"]
        }
    },
    {
        "name": "send_email",
        "namespace": "email",
        "description": "Send a drafted email via Gmail",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "recipient email address"},
                "subject": {"type": "string", "description": "email subject line"},
                "body": {"type": "string", "description": "email body"},
                "thread_id": {"type": "string", "description": "optional thread ID for replies"}
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "send_followup_email",
        "namespace": "email",
        "description": "Send a follow up email on a thread that has not received a response",
        "input_schema": {
            "type": "object",
            "properties": {
                "thread_id": {"type": "string", "description": "original email thread ID"},
                "days_since_last": {"type": "integer", "description": "days since last email sent"},
                "context": {"type": "object", "description": "original outreach context"}
            },
            "required": ["thread_id", "days_since_last"]
        }
    },
    {
        "name": "draft_schedule_call_email",
        "namespace": "email",
        "description": "Draft an email to schedule a call or coffee chat with a contact",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "object", "description": "contact to schedule with"},
                "purpose": {"type": "string", "description": "reason for the call e.g. informational, interview"},
                "availability": {"type": "string", "description": "candidate availability windows"}
            },
            "required": ["recipient", "purpose"]
        }
    },
    {
        "name": "draft_rejection_response",
        "namespace": "email",
        "description": "Draft a gracious thank you response to a rejection email",
        "input_schema": {
            "type": "object",
            "properties": {
                "rejection_email": {"type": "string", "description": "content of the rejection received"},
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["rejection_email", "company_name"]
        }
    },
    {
        "name": "draft_offer_response",
        "namespace": "email",
        "description": "Draft a thank you and acknowledgment email upon receiving an offer",
        "input_schema": {
            "type": "object",
            "properties": {
                "offer_details": {"type": "object", "description": "offer details received"},
                "company_name": {"type": "string", "description": "name of the company"},
                "intent": {"type": "string", "description": "accept, negotiate, or decline"}
            },
            "required": ["offer_details", "company_name"]
        }
    },
    {
        "name": "draft_referral_email",
        "namespace": "email",
        "description": "Draft an email requesting a referral from a contact at the company",
        "input_schema": {
            "type": "object",
            "properties": {
                "referrer": {"type": "object", "description": "contact who can refer"},
                "role": {"type": "string", "description": "role being applied for"},
                "relationship_context": {"type": "string", "description": "how candidate knows this person"}
            },
            "required": ["referrer", "role"]
        }
    },
    {
        "name": "track_email_status",
        "namespace": "email",
        "description": "Check if an email was opened, replied to, or ignored via tracking",
        "input_schema": {
            "type": "object",
            "properties": {
                "thread_id": {"type": "string", "description": "email thread ID to check"},
                "sent_at": {"type": "string", "description": "ISO timestamp of when email was sent"}
            },
            "required": ["thread_id"]
        }
    },
    {
        "name": "parse_email_response",
        "namespace": "email",
        "description": "Read an incoming email reply and extract sentiment, intent, and recommended next action",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_content": {"type": "string", "description": "raw text of the reply received"},
                "thread_context": {"type": "object", "description": "context of the original outreach"}
            },
            "required": ["email_content"]
        }
    },

    # ─────────────────────────────────────────
    # NAMESPACE: apply (10 tools)
    # ─────────────────────────────────────────
    {
        "name": "login_to_portal",
        "namespace": "apply",
        "description": "Authenticate into a job application portal like Greenhouse or Workday",
        "input_schema": {
            "type": "object",
            "properties": {
                "portal_url": {"type": "string", "description": "URL of the application portal"},
                "portal_type": {"type": "string", "description": "e.g. greenhouse, workday, lever"}
            },
            "required": ["portal_url"]
        }
    },
    {
        "name": "fill_basic_fields",
        "namespace": "apply",
        "description": "Fill in name, education, and work experience fields from resume data",
        "input_schema": {
            "type": "object",
            "properties": {
                "resume": {"type": "object", "description": "output from fetch_my_resume"},
                "portal_type": {"type": "string", "description": "e.g. greenhouse, workday, lever"}
            },
            "required": ["resume"]
        }
    },
    {
        "name": "generate_cover_letter",
        "namespace": "apply",
        "description": "Generate a tailored cover letter using job description, relevant experiences, and build opportunities",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_description": {"type": "object", "description": "output from fetch_job_description"},
                "relevant_experiences": {"type": "object", "description": "output from evaluate_relevant_experiences"},
                "build_opportunities": {"type": "object", "description": "output from suggest_build_opportunities"},
                "company_name": {"type": "string", "description": "name of the company"}
            },
            "required": ["job_description", "relevant_experiences"]
        }
    },
    {
        "name": "answer_short_questions",
        "namespace": "apply",
        "description": "Generate answers to short answer questions like 'why this company' or 'describe a challenge'",
        "input_schema": {
            "type": "object",
            "properties": {
                "questions": {"type": "array", "items": {"type": "string"}, "description": "list of short answer questions from the application"},
                "company_context": {"type": "object", "description": "aggregated company research"},
                "resume": {"type": "object", "description": "output from fetch_my_resume"}
            },
            "required": ["questions", "resume"]
        }
    },
    {
        "name": "attach_portfolio",
        "namespace": "apply",
        "description": "Attach relevant portfolio links such as GitHub, Neuroscan360, or OP project based on role",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "job title to determine which portfolio items are relevant"},
                "available_links": {"type": "array", "items": {"type": "string"}, "description": "list of portfolio URLs"}
            },
            "required": ["role"]
        }
    },
    {
        "name": "fill_demographic_fields",
        "namespace": "apply",
        "description": "Fill in EEO and demographic fields in the application",
        "input_schema": {
            "type": "object",
            "properties": {
                "demographic_preferences": {"type": "object", "description": "candidate's demographic response preferences"}
            },
            "required": []
        }
    },
    {
        "name": "fill_salary_expectation",
        "namespace": "apply",
        "description": "Fill in salary expectation field using negotiation position and market data",
        "input_schema": {
            "type": "object",
            "properties": {
                "negotiation_position": {"type": "object", "description": "output from evaluate_negotiation_position"},
                "salary_data": {"type": "object", "description": "output from search_salary_range"}
            },
            "required": []
        }
    },
    {
        "name": "fill_availability",
        "namespace": "apply",
        "description": "Fill in start date and availability fields",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "earliest available start date"},
                "availability_notes": {"type": "string", "description": "any caveats like visa processing time"}
            },
            "required": ["start_date"]
        }
    },
    {
        "name": "submit_application",
        "namespace": "apply",
        "description": "Submit the completed application on the portal",
        "input_schema": {
            "type": "object",
            "properties": {
                "portal_type": {"type": "string", "description": "e.g. greenhouse, workday, lever"},
                "application_data": {"type": "object", "description": "all filled fields ready for submission"}
            },
            "required": ["portal_type", "application_data"]
        }
    },
    {
        "name": "parse_confirmation",
        "namespace": "apply",
        "description": "Extract confirmation number, next steps, and timeline from the application submission receipt",
        "input_schema": {
            "type": "object",
            "properties": {
                "confirmation_page": {"type": "string", "description": "raw text or HTML of the confirmation page"}
            },
            "required": ["confirmation_page"]
        }
    },

    # ─────────────────────────────────────────
    # NAMESPACE: document (8 tools)
    # ─────────────────────────────────────────
    {
        "name": "create_application_record",
        "namespace": "document",
        "description": "Create initial Notion record for a new application with company, role, status, and key contacts",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "name of the company"},
                "role": {"type": "string", "description": "job title"},
                "confirmation_data": {"type": "object", "description": "output from parse_confirmation"},
                "key_contacts": {"type": "object", "description": "output from search_key_people"}
            },
            "required": ["company_name", "role"]
        }
    },
    {
        "name": "update_application_status",
        "namespace": "document",
        "description": "Update the status field of an application record: applied, interviewing, offer, rejected",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "status": {"type": "string", "description": "new status value"},
                "notes": {"type": "string", "description": "optional context for this status change"}
            },
            "required": ["record_id", "status"]
        }
    },
    {
        "name": "log_outreach",
        "namespace": "document",
        "description": "Log a sent email in the application record: who was contacted, when, and what was sent",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "recipient": {"type": "object", "description": "person contacted"},
                "email_summary": {"type": "string", "description": "brief summary of what was sent"},
                "sent_at": {"type": "string", "description": "ISO timestamp"}
            },
            "required": ["record_id", "recipient", "sent_at"]
        }
    },
    {
        "name": "update_contact_response",
        "namespace": "document",
        "description": "Update the response status for a contact: replied, ghosted, bounced, scheduled call",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "contact_name": {"type": "string", "description": "name of the contact"},
                "response_status": {"type": "string", "description": "replied, ghosted, bounced, scheduled"},
                "response_summary": {"type": "string", "description": "brief summary of the response if any"}
            },
            "required": ["record_id", "contact_name", "response_status"]
        }
    },
    {
        "name": "log_followup",
        "namespace": "document",
        "description": "Log a follow up email sent in the application record",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "followup_number": {"type": "integer", "description": "which follow up this is e.g. 1, 2, 3"},
                "sent_at": {"type": "string", "description": "ISO timestamp"},
                "summary": {"type": "string", "description": "brief summary of the follow up"}
            },
            "required": ["record_id", "followup_number", "sent_at"]
        }
    },
    {
        "name": "schedule_next_step",
        "namespace": "document",
        "description": "Add a scheduled next step to the application record such as a call or interview",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "step_type": {"type": "string", "description": "coffee chat, phone screen, technical interview, etc"},
                "scheduled_at": {"type": "string", "description": "ISO timestamp of scheduled event"},
                "with_person": {"type": "string", "description": "name of person for the meeting"}
            },
            "required": ["record_id", "step_type", "scheduled_at"]
        }
    },
    {
        "name": "add_notes",
        "namespace": "document",
        "description": "Add freeform notes to an application record",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "notes": {"type": "string", "description": "freeform notes to append"}
            },
            "required": ["record_id", "notes"]
        }
    },
    {
        "name": "fetch_application_record",
        "namespace": "document",
        "description": "Read the current state of an application record before deciding the next action",
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Notion record ID"},
                "company_name": {"type": "string", "description": "company name as alternative lookup"}
            },
            "required": []
        }
    },
]


# Helper: get tools formatted for Anthropic API
def get_tools_for_api(namespace: str = None) -> list:
    """
    Returns tools formatted for the Anthropic API.
    If namespace is provided, returns only tools from that namespace.
    """
    tools = TOOL_REGISTRY if not namespace else [t for t in TOOL_REGISTRY if t["namespace"] == namespace]
    return [
        {
            "name": f"{t['namespace']}__{t['name']}",
            "description": t["description"],
            "input_schema": t["input_schema"]
        }
        for t in tools
    ]


# Helper: look up a tool by namespace and name
def get_tool(namespace: str, name: str) -> dict:
    for tool in TOOL_REGISTRY:
        if tool["namespace"] == namespace and tool["name"] == name:
            return tool
    raise ValueError(f"Tool not found: {namespace}.{name}")


if __name__ == "__main__":
    print(f"Total tools: {len(TOOL_REGISTRY)}")
    namespaces = {}
    for t in TOOL_REGISTRY:
        namespaces[t["namespace"]] = namespaces.get(t["namespace"], 0) + 1
    for ns, count in namespaces.items():
        print(f"  {ns}: {count} tools")
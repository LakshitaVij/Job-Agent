from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
from agent.core.executor import execute_tool
import anthropic
import json
import requests
from bs4 import BeautifulSoup
import os
import http.client
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def _evaluate(prompt):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]
    
    response = client.messages.create(
    model ="claude-haiku-4-5-20251001",
    max_tokens = 4096,
    messages = messages
    )
    return next(block for block in response.content if block.type == "text").text


def evaluate_resume_fit(job_description, resume):
    prompt = f"""
    You are a hiring expert. Given this job description and candidate resume, score the fit from 0-100 and explain why.
    
    Job Description: {job_description}
    
    Resume: {resume}
    
    Return a JSON with:
    - score: number 0-100
    - strengths: list of matching strengths
    - gaps: list of missing requirements
    - summary: one paragraph explanation
    """
    return _evaluate(prompt)

def evaluate_relevant_experiences(job_description, resume):
    prompt = f"""
    You are a career coach. Given this job description and resume, identify the 3-5 most relevant experiences to highlight.
    
    Job Description: {job_description}
    Resume: {resume}
    
    Return JSON with:
    - experiences: list of specific experiences to highlight
    - reasoning: why each experience is relevant
    - suggested_order: which to lead with
    """
    return _evaluate(prompt)

def evaluate_red_flags(job_description, glassdoor_data, company_data):
    prompt = f"""
    You are a career advisor. Analyze this company and role for red flags a candidate should know before applying.
    
    Job Description: {job_description}
    Glassdoor Data: {glassdoor_data}
    Company Data: {company_data}
    
    Return JSON with:
    - red_flags: list of concerns with severity (high/medium/low)
    - green_flags: positive signals
    - verdict: overall recommendation
    """
    return _evaluate(prompt)

def evaluate_negotiation_position(resume_fit_score, salary_data, funding_stage):
    prompt = f"""
    You are a salary negotiation expert. Based on this data, assess the candidate's negotiation position.
    
    Resume Fit Score: {resume_fit_score}
    Salary Data: {salary_data}
    Funding Stage: {funding_stage}
    
    Return JSON with:
    - position: reach / match / safe_bet
    - leverage: list of negotiation strengths
    - suggested_range: salary range to target
    - strategy: one paragraph negotiation advice
    """
    return _evaluate(prompt)
def evaluate_career_trajectory(trajectory_data, candidate_background):
    prompt = f"""
    You are a career strategist. Analyze how this role fits into the candidate's long-term career trajectory.
    
    Career Trajectory Data: {trajectory_data}
    Candidate Background: {candidate_background}
    
    Return JSON with:
    - next_roles: list of roles this opens up in 2-3 years
    - skills_gained: key skills this role builds
    - ceiling: how far this role can take the candidate
    - verdict: is this a stepping stone or a destination
    """
    return _evaluate(prompt)

def evaluate_opportunity_stack_rank(current_opportunity, pipeline):
    prompt = f"""
    You are a career advisor. Compare this opportunity against others in the candidate's pipeline.
    
    Current Opportunity: {current_opportunity}
    Other Opportunities: {pipeline}
    
    Return JSON with:
    - rank: where this opportunity ranks
    - reasoning: why it ranks here
    - trade_offs: what you gain and lose vs other options
    - recommendation: pursue aggressively / keep as backup / deprioritize
    """
    return _evaluate(prompt)

def evaluate_enjoyment_fit(job_description, glassdoor_data, candidate_preferences):
    prompt = f"""
    You are a career coach. Assess whether this role aligns with the candidate's interests and working style.
    
    Job Description: {job_description}
    Glassdoor Data: {glassdoor_data}
    Candidate Preferences: {candidate_preferences}
    
    Return JSON with:
    - alignment_score: 0-100
    - what_youll_love: list of aspects that match preferences
    - what_might_drain_you: list of potential mismatches
    - verdict: one paragraph honest assessment
    """
    return _evaluate(prompt)

def evaluate_first_year_plan(job_description, company_data):
    prompt = f"""
    You are an executive coach. Based on this role and company, draft a realistic first year plan.
    
    Job Description: {job_description}
    Company Data: {company_data}
    
    Return JSON with:
    - month_1: list of goals and priorities
    - month_3: list of goals and priorities  
    - month_6: list of goals and priorities
    - month_12: list of goals and priorities
    - key_relationships: who to build relationships with early
    - quick_wins: what to accomplish in first 30 days
    """
    return _evaluate(prompt)

def evaluate_interview_prep(job_description, interview_process, resume):
    prompt = f"""
    You are an interview coach. Generate a targeted preparation plan for this role.
    
    Job Description: {job_description}
    Interview Process: {interview_process}
    Resume: {resume}
    
    Return JSON with:
    - topics_to_study: list of technical topics to prepare
    - stories_to_prepare: list of behavioral stories from resume to polish
    - questions_to_expect: likely interview questions
    - questions_to_ask: smart questions to ask the interviewer
    """
    return _evaluate(prompt)

def evaluate_skill_gaps(job_description, resume):
    prompt = f"""
    You are a technical recruiter. Identify the gap between what this role needs and what the candidate has.
    
    Job Description: {job_description}
    Resume: {resume}
    
    Return JSON with:
    - strong_skills: skills candidate has that match
    - partial_skills: skills candidate has but needs to deepen
    - missing_skills: skills candidate needs to build
    - dealbreakers: any gaps that could disqualify the candidate
    """
    return _evaluate(prompt)

def evaluate_skill_building_plan(skill_gaps, timeline):
    prompt = f"""
    You are a learning coach. Create a concrete plan to close these skill gaps before the interview.
    
    Skill Gaps: {skill_gaps}
    Timeline: {timeline}
    
    Return JSON with:
    - priority_skills: which gaps to close first
    - resources: specific courses, projects, or readings for each skill
    - weekly_plan: concrete weekly breakdown
    - quick_demonstrations: how to show progress in an interview even if not fully learned
    """
    return _evaluate(prompt)

def evaluate_team_quality(key_people, press_coverage):
    prompt = f"""
    You are a talent advisor. Assess the quality of the team and mentorship potential at this company.
    
    Key People: {key_people}
    Press Coverage: {press_coverage}
    
    Return JSON with:
    - team_caliber: assessment of seniority and background of key people
    - mentorship_potential: who could be a strong mentor and why
    - team_red_flags: any concerns about the team composition
    - verdict: strong team / average team / weak team
    """
    return _evaluate(prompt)

def evaluate_work_life_balance(glassdoor_data, fundraising_stage, job_description):
    prompt = f"""
    You are a career advisor. Assess the likely work life balance at this company based on available signals.
    
    Glassdoor Data: {glassdoor_data}
    Fundraising Stage: {fundraising_stage}
    Job Description: {job_description}
    
    Return JSON with:
    - balance_score: 0-100 where 100 is perfect balance
    - signals: what data points suggest about culture
    - expectations: realistic weekly hour expectations
    - verdict: one honest paragraph
    """
    return _evaluate(prompt)

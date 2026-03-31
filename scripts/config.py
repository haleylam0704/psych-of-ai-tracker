"""
Configuration for the Psychology of AI paper tracker.

Fetching strategy:
  1. Primary: OpenAlex topic IDs + psychology concept filter (broad, systematic)
  2. Safety net: keyword queries for cross-disciplinary papers that get
     mis-tagged by OpenAlex's topic system

Classification: Haiku classifies each paper's relevance and subtopic.
"""

# Email for OpenAlex polite pool (faster rate limits, no key needed)
OPENALEX_EMAIL = "haleylam0704@gmail.com"

# Only fetch papers from this date onward
PUBLICATION_DATE_FROM = "2020-01-01"

# OpenAlex topic IDs for primary fetch
OPENALEX_TOPIC_IDS = [
    "T10883",  # Ethics and Social Impacts of AI
    "T12128",  # AI in Service Interactions
    "T10709",  # Social Robot Interaction and HRI
]

# Require at least one psychology-related concept to filter out
# pure CS/policy papers from the topic results.
OPENALEX_PSYCH_CONCEPT_IDS = [
    "C15744967",   # Psychology
    "C77805123",   # Social psychology
    "C180747234",  # Cognitive psychology
]

# Safety net keyword queries for important papers that OpenAlex mis-topics.
# These should target known blind spots, not replicate the topic sweep.
SAFETY_NET_QUERIES = [
    "theory of mind large language models",
    "AI moral psychology",
    "AI labor market impact",
    "ChatGPT critical thinking",
    "generative AI critical thinking",
    "AI cognitive offloading",
    "suicidality language model",
    "AI PTSD treatment",
    "algorithm aversion",
]

# Subtopics for classifying papers (used by Haiku classification).
SUBTOPICS = {
    "trust_reliance": {
        "name": "Trust & Reliance on AI",
        "description": "How trust in AI is formed, calibrated, and maintained; appropriate vs. inappropriate reliance on AI recommendations.",
    },
    "anthropomorphism": {
        "name": "Anthropomorphism & Mind Perception",
        "description": "Attributing humanlike qualities, intentions, and consciousness to AI; mind perception; warmth and competence perception.",
    },
    "emotional_attachment": {
        "name": "Emotional Bonding & AI Relationships",
        "description": "Emotional attachments to AI chatbots, companionship, perceived empathy, parasocial relationships with AI, AI romance.",
    },
    "cognitive_effects": {
        "name": "Cognitive Effects of AI Use",
        "description": "Impact on critical thinking, memory, learning, cognitive offloading, skill erosion, cognitive dependency from AI use.",
    },
    "mental_health": {
        "name": "AI & Mental Health",
        "description": "Psychological well-being effects of AI use; AI for mental health interventions; chatbot therapy; risks for vulnerable users.",
    },
    "bias_fairness": {
        "name": "AI Bias & Fairness Perceptions",
        "description": "Perceived fairness of AI decisions; algorithmic bias; discrimination in AI systems and human reactions.",
    },
    "decision_making": {
        "name": "AI & Human Decision-Making",
        "description": "How AI advice/nudges affect choices, autonomy, moral judgment, dishonesty, and sense of control; algorithm aversion.",
    },
    "social_norms": {
        "name": "AI & Social Perception",
        "description": "How AI shapes social norms, attitudes, persuasion; AI-generated content effects on beliefs; politeness to AI.",
    },
    "suspicion_stigma": {
        "name": "AI Suspicion & Stigma",
        "description": "Who is suspected of using AI; social consequences of AI use detection; authenticity concerns.",
    },
    "individual_differences": {
        "name": "Individual Differences in AI Interaction",
        "description": "How personality, age, culture, digital literacy, and attitudes shape human-AI interaction.",
    },
    "ai_therapy": {
        "name": "AI in Clinical & Therapeutic Contexts",
        "description": "AI chatbots for therapy, counseling, crisis intervention; therapeutic alliance with AI; clinical AI applications.",
    },
    "ai_psych_methods": {
        "name": "AI as Psychology Research Tool",
        "description": "Using LLMs/AI for psychological research: simulating participants, text analysis, scale development.",
    },
}

# Classification prompt template for Haiku
CLASSIFICATION_PROMPT = """You are classifying psychology research papers about AI/LLMs.

Given a paper's title and abstract, determine:
1. Is this paper actually about the PSYCHOLOGICAL aspects of AI (human reactions to, perceptions of, or behavioral effects of AI)? Not purely technical AI papers.
2. Which subtopic(s) does it best fit?

Subtopics:
{subtopic_list}

Respond in JSON:
{{"relevant": true/false, "primary_topic": "topic_key", "secondary_topic": "topic_key_or_null", "confidence": 0.0-1.0}}

Title: {title}
Abstract: {abstract}
"""

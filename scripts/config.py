"""
Configuration for the Psychology of AI paper tracker.
Defines subtopics, their search queries, and classification prompts.
"""

# Email for OpenAlex polite pool (faster rate limits, no key needed)
OPENALEX_EMAIL = "haleylam@example.com"  # TODO: replace with your real email

# How many results to fetch per subtopic per run
MAX_RESULTS_PER_TOPIC = 200

# Subtopics and their OpenAlex search queries
# Each topic has: display name, description, search queries (OR'd together)
SUBTOPICS = {
    "trust_reliance": {
        "name": "Trust & Reliance on AI",
        "description": "How trust in AI is formed, calibrated, and maintained; appropriate vs. inappropriate reliance on AI recommendations.",
        "queries": [
            "trust artificial intelligence",
            "reliance AI recommendations",
            "trust large language models",
            "AI trust calibration",
        ],
    },
    "anthropomorphism": {
        "name": "Anthropomorphism & Mind Perception",
        "description": "Attributing humanlike qualities, intentions, and consciousness to AI; mind perception of AI systems.",
        "queries": [
            "anthropomorphism AI",
            "mind perception artificial intelligence",
            "AI consciousness attribution",
            "humanlike AI perception",
        ],
    },
    "emotional_attachment": {
        "name": "Emotional Bonding & AI Relationships",
        "description": "Emotional attachments to AI chatbots, companionship, perceived empathy, parasocial relationships with AI.",
        "queries": [
            "emotional attachment AI chatbot",
            "AI companionship loneliness",
            "parasocial relationship AI",
            "AI emotional bond",
            "AI friendship relationship",
        ],
    },
    "cognitive_effects": {
        "name": "Cognitive Effects of AI Use",
        "description": "Impact on critical thinking, memory, learning, cognitive offloading, skill erosion from AI use.",
        "queries": [
            "cognitive effects AI use",
            "AI cognitive offloading",
            "critical thinking artificial intelligence",
            "AI impact learning memory",
            "LLM cognitive dependency",
        ],
    },
    "mental_health": {
        "name": "AI & Mental Health",
        "description": "Psychological well-being effects of AI use; AI for mental health interventions; risks for vulnerable users.",
        "queries": [
            "AI mental health wellbeing",
            "chatbot therapy mental health",
            "AI psychological wellbeing",
            "LLM mental health effects",
            "AI anxiety depression",
        ],
    },
    "bias_fairness": {
        "name": "AI Bias & Fairness Perceptions",
        "description": "Perceived fairness of AI decisions; algorithmic bias; discrimination in AI systems and human reactions.",
        "queries": [
            "AI bias fairness perception",
            "algorithmic discrimination psychology",
            "AI stereotypes prejudice",
            "perceived fairness AI decisions",
        ],
    },
    "decision_making": {
        "name": "AI & Human Decision-Making",
        "description": "How AI advice/nudges affect choices, autonomy, moral judgment, and sense of control.",
        "queries": [
            "AI advice decision making",
            "AI autonomy human choice",
            "AI moral judgment",
            "algorithmic decision aversion",
            "AI nudge behavior",
        ],
    },
    "social_norms": {
        "name": "AI & Social Perception",
        "description": "How AI shapes social norms, attitudes, persuasion; AI-generated content effects on beliefs.",
        "queries": [
            "AI social norms perception",
            "AI persuasion attitudes",
            "AI generated content beliefs",
            "LLM influence opinion",
        ],
    },
    "suspicion_stigma": {
        "name": "AI Suspicion & Stigma",
        "description": "Who is suspected of using AI; social consequences of AI use detection; authenticity concerns.",
        "queries": [
            "AI detection suspicion",
            "AI use stigma",
            "AI authenticity perception",
            "AI generated text detection social",
        ],
    },
    "individual_differences": {
        "name": "Individual Differences in AI Interaction",
        "description": "How personality, age, culture, digital literacy, and attitudes shape human-AI interaction.",
        "queries": [
            "personality AI interaction",
            "individual differences AI use",
            "AI attitudes personality traits",
            "cultural differences AI perception",
        ],
    },
    "ai_therapy": {
        "name": "AI in Clinical & Therapeutic Contexts",
        "description": "AI chatbots for therapy, counseling, crisis intervention; therapeutic alliance with AI.",
        "queries": [
            "AI chatbot therapy counseling",
            "therapeutic alliance AI",
            "AI crisis intervention",
            "conversational AI clinical psychology",
        ],
    },
    "ai_psych_methods": {
        "name": "AI as Psychology Research Tool",
        "description": "Using LLMs/AI for psychological research: simulating participants, text analysis, scale development.",
        "queries": [
            "large language model psychological research",
            "AI simulated participants psychology",
            "LLM text analysis psychology",
            "GPT psychology research method",
        ],
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

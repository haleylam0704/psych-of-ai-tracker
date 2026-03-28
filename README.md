# Psychology of AI — Paper Tracker

Auto-updating literature tracker for the psychological study of human-AI interaction.

## How it works

1. **Every 3 days**, a GitHub Action fetches new papers from [OpenAlex](https://openalex.org/) (free, no API key)
2. **Claude Haiku** classifies abstracts by relevance and subtopic (~$0.03/month)
3. A static site is built and deployed to **GitHub Pages** (free)

## Subtopics tracked

- Trust & Reliance on AI
- Anthropomorphism & Mind Perception
- Emotional Bonding & AI Relationships
- Cognitive Effects of AI Use
- AI & Mental Health
- AI Bias & Fairness Perceptions
- AI & Human Decision-Making
- AI & Social Perception
- AI Suspicion & Stigma
- Individual Differences in AI Interaction
- AI in Clinical & Therapeutic Contexts
- AI as Psychology Research Tool

## Setup

1. Create a GitHub repo and push this project
2. Add your Anthropic API key as a repository secret: `ANTHROPIC_API_KEY`
3. Update `scripts/config.py` with your email (for OpenAlex polite pool)
4. Enable GitHub Pages (source: main branch, `/site` folder)
5. Run the workflow manually once, or wait for the first scheduled run

## Local development

```bash
cd scripts
python fetch_papers.py      # fetch from OpenAlex
python classify_papers.py   # classify with Haiku (needs ANTHROPIC_API_KEY)
python build_site.py        # build site/data.json
# Open site/index.html in browser
```

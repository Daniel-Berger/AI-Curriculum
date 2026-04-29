# Module 05: Solutions Engineer Interview Preparation

## Introduction

Solutions Engineering (SE) sits at the intersection of technical depth and customer empathy.
At AI companies like Anthropic, OpenAI, Google DeepMind, and Cohere, SEs are the bridge
between cutting-edge models and real-world customer outcomes. You are not just answering
support tickets -- you are designing architectures, debugging production systems, delivering
workshops, and influencing product roadmaps based on what you see in the field.

If you are coming from iOS/Swift development, you already have strong instincts here.
You have shipped products to real users. You have debugged production crashes at 2 AM.
You have explained technical constraints to product managers and designers. The SE role
channels all of those skills into a customer-facing technical role with enormous impact.

This module covers every stage of the SE interview process, what each stage evaluates,
and how to prepare with concrete strategies and practice frameworks.

---

## The SE Interview Process

Most AI companies follow a multi-stage interview loop for SE roles. While the exact
number of rounds varies, the stages below are representative of what you will encounter
at Anthropic, OpenAI, Google, Cohere, and similar companies.

### Stage 1: Recruiter Screen (30 min)

**What it evaluates**: Fit, motivation, communication basics, compensation alignment.

**What to expect**:
- "Walk me through your background."
- "Why solutions engineering? Why this company?"
- "What's your experience with AI/ML?"
- "What are your compensation expectations?"

**How to prepare**:
- Have a 90-second career narrative ready (see Phase 8 Module 04 for the STAR framework).
- Research the company's products, pricing, and recent announcements.
- Know their API documentation well enough to reference specific features.
- Have a compensation range ready (see Compensation Guide below).

**Common mistake**: Treating this as a formality. Recruiters are evaluating your
communication skills from the first interaction. Be concise, enthusiastic, and specific.

---

### Stage 2: Technical Screen (45-60 min)

**What it evaluates**: Technical depth, coding ability, understanding of AI concepts.

**What to expect**:
- Live coding (Python, API integrations, data processing)
- Conceptual questions about LLMs, embeddings, RAG, fine-tuning
- "How would you explain [technical concept] to a non-technical customer?"
- Debugging a broken code snippet

**How to prepare**:
- Review Phases 1-7 of this curriculum, especially Phase 6 (LLM Applications)
- Practice explaining technical concepts at multiple levels of abstraction
- Be comfortable writing Python code that calls AI APIs
- Know the differences between major AI providers (pricing, models, capabilities)

**Swift developer advantage**: Your experience with strongly-typed APIs (URLSession,
Codable, Result types) means you understand API contract design deeply. Mention how
you approach error handling, retry logic, and response parsing.

---

### Stage 3: Live Debugging Interview (45-60 min)

**What it evaluates**: Debugging methodology, communication under pressure, systematic
thinking, ability to explain findings to a customer.

**What to expect**:
- A broken code sample or integration that you must diagnose and fix
- The interviewer may role-play as a customer describing their problem
- You may need to read logs, identify error patterns, and propose solutions
- Time pressure -- you will not finish everything, and that is intentional

**How to prepare**:
- See the "Live Debugging Interviews" section below for detailed strategies
- Practice debugging API integrations with common failure modes
- Build a personal debugging checklist you can use under pressure
- Practice narrating your thought process out loud

---

### Stage 4: Demo Presentation (45-60 min)

**What it evaluates**: Presentation skills, technical depth, ability to handle live
failures, audience engagement, Q&A handling.

**What to expect**:
- Build and present a demo using the company's product/API
- The demo should solve a realistic customer problem
- Interviewers will ask tough questions and may introduce curveballs
- You may need to handle a live failure gracefully

**How to prepare**:
- See the "Demo Presentation Skills" section below
- Build 2-3 demo applications using the target company's API
- Practice presenting each demo in under 15 minutes
- Prepare for common failure scenarios and have backup plans

---

### Stage 5: System Design (45-60 min)

**What it evaluates**: Architecture thinking, understanding of AI system components,
ability to design for customer requirements.

**What to expect**:
- Design an AI-powered system for a specific customer use case
- SE system design emphasizes customer constraints (budget, compliance, existing stack)
- More focus on integration architecture than pure infrastructure scaling
- You may need to draw architecture diagrams and discuss tradeoffs

**How to prepare**:
- Review Phase 8 Module 01 (System Design) thoroughly
- Focus on the SE-specific system design problems added to that module
- Practice designing systems that integrate AI APIs into existing enterprise stacks
- Know common patterns: RAG, agentic workflows, fine-tuning pipelines, evaluation frameworks

---

### Stage 6: Behavioral / Values Interview (45-60 min)

**What it evaluates**: Customer empathy, cross-functional collaboration, conflict
resolution, alignment with company values.

**What to expect**:
- STAR-format behavioral questions with SE-specific focus
- "Tell me about a time you handled a difficult customer situation"
- "How do you balance customer needs with product limitations?"
- Values-based questions specific to the company

**How to prepare**:
- Review Phase 8 Module 04 (Behavioral Prep)
- Prepare SE-specific STAR stories (see SE-Specific Behavioral Questions below)
- Research the company's stated values and prepare examples that align
- Practice the customer scenario role-plays below

---

### Stage 7: Team Match / Cross-Functional (30-45 min)

**What it evaluates**: Culture fit, working style, how you collaborate with engineering,
product, and sales teams.

**What to expect**:
- Informal conversation with potential teammates
- "How do you work with sales teams?"
- "How do you prioritize when multiple customers need help?"
- "What does your ideal day look like?"

**How to prepare**:
- Be authentic -- this is about mutual fit
- Have specific examples of cross-functional collaboration
- Show curiosity about how the team operates
- Ask thoughtful questions about team dynamics and workflows

---

## Live Debugging Interviews

Live debugging is the most SE-specific interview stage. It tests whether you can
systematically diagnose problems while communicating clearly -- exactly what you do
every day as an SE.

### The Debugging Framework

Use this structured approach every time:

```
1. REPRODUCE          (2-3 min)
   - Confirm the exact error/symptom
   - Identify what "working" looks like
   - Establish the environment (Python version, OS, API version)

2. ISOLATE            (3-5 min)
   - Binary search: which component is failing?
   - Test each layer independently (network, auth, payload, response parsing)
   - Check the simplest thing first (API key, endpoint URL, HTTP method)

3. DIAGNOSE           (5-10 min)
   - Read error messages carefully (full stack trace, not just the last line)
   - Check API documentation for the specific error code
   - Look for recent changes (API version, library update, config change)

4. FIX                (5-10 min)
   - Implement the fix
   - Verify it resolves the original issue
   - Check for side effects

5. COMMUNICATE        (throughout)
   - Narrate your thought process
   - Explain what you are checking and why
   - Summarize findings in customer-friendly language
```

### Common Debugging Patterns

#### Pattern 1: Authentication Failures

```python
# Customer reports: "I keep getting 401 errors"
# Common causes:
# 1. API key not set or set incorrectly
# 2. API key in wrong header format
# 3. API key expired or revoked
# 4. Using test key against production endpoint
# 5. Organization/project ID mismatch

# Debugging checklist:
import os

def debug_auth(api_key: str, base_url: str) -> dict:
    """Systematic auth debugging."""
    issues = []

    # Check 1: Key exists and is non-empty
    if not api_key:
        issues.append("API key is empty or None")
    elif api_key.startswith(" ") or api_key.endswith(" "):
        issues.append("API key has leading/trailing whitespace")

    # Check 2: Key format matches expected pattern
    if api_key and not api_key.startswith("sk-"):
        issues.append(f"Key starts with '{api_key[:3]}', expected 'sk-'")

    # Check 3: Environment variable vs hardcoded
    env_key = os.environ.get("API_KEY", "")
    if env_key and env_key != api_key:
        issues.append("Hardcoded key differs from environment variable")

    # Check 4: Base URL is correct
    if "v1" not in base_url and "v2" not in base_url:
        issues.append(f"Base URL '{base_url}' missing API version")

    return {"issues": issues, "key_length": len(api_key) if api_key else 0}
```

#### Pattern 2: Rate Limiting

```python
# Customer reports: "Requests work sometimes but fail randomly"
# Common causes:
# 1. Hitting rate limits (requests per minute or tokens per minute)
# 2. No retry logic with exponential backoff
# 3. Concurrent requests exceeding limits
# 4. Burst traffic patterns

import time
import random

def exponential_backoff_request(func, max_retries=5):
    """Robust retry with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Waiting {wait_time:.1f}s (attempt {attempt + 1})")
            time.sleep(wait_time)
        except APIError as e:
            if e.status_code >= 500:
                # Server error -- retry
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                # Client error -- don't retry
                raise
```

#### Pattern 3: Response Parsing Failures

```python
# Customer reports: "The API returns data but my code crashes"
# Common causes:
# 1. Assuming response structure without checking
# 2. Not handling streaming vs non-streaming responses
# 3. Missing error handling for edge cases (empty response, null fields)
# 4. JSON parsing without validation

def safe_parse_response(response) -> dict:
    """Parse API response with comprehensive error handling."""
    # Check HTTP status first
    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}",
            "body": response.text[:500],
            "headers": dict(response.headers),
        }

    # Try to parse JSON
    try:
        data = response.json()
    except ValueError as e:
        return {
            "error": "Invalid JSON in response",
            "raw_text": response.text[:500],
            "content_type": response.headers.get("content-type"),
        }

    # Validate expected structure
    if "choices" not in data:
        return {
            "error": "Missing 'choices' key in response",
            "keys_present": list(data.keys()),
            "data_preview": str(data)[:500],
        }

    if not data["choices"]:
        return {
            "error": "Empty 'choices' array",
            "finish_reason": data.get("usage", {}).get("completion_tokens", "unknown"),
        }

    return {"success": True, "data": data}
```

### Talking Through Your Process

The most important skill in a live debugging interview is narration. Here is what
good narration sounds like:

**Bad**: *silently reads code for 3 minutes, then says "I found the bug"*

**Good**: "I'm going to start by looking at the error message. It says 401 Unauthorized,
so this is an authentication issue. Let me check how the API key is being passed...
I see it's being set in the headers, but the format looks wrong. The API expects
'Authorization: Bearer sk-xxx' but this code is sending 'x-api-key: sk-xxx'.
Let me check the documentation to confirm... Yes, this API uses Bearer token auth.
That's our first issue. Let me also check if there are other problems before I
declare victory."

### Practice Debugging Scenarios

Work through the exercises in `exercises.py` for 15 debugging and SE scenarios.
Each one is designed to test a different skill:

1. **Finding multiple bugs** -- Real customer code rarely has just one issue
2. **Prioritizing fixes** -- Which bug is the root cause vs. a symptom?
3. **Communicating findings** -- Can you explain the issue in non-technical terms?
4. **Proposing preventive measures** -- How do you stop this from happening again?

---

## Demo Presentation Skills

The demo presentation is where SEs shine or stumble. You are not just showing code --
you are telling a story about how technology solves a real problem.

### The Demo Structure

```
1. CONTEXT SETTING     (2-3 min)
   - Customer persona: who are they, what do they do?
   - Pain point: what problem are they trying to solve?
   - Why now: what makes this urgent or important?

2. SOLUTION OVERVIEW   (2-3 min)
   - High-level architecture (one slide or diagram)
   - Key components and how they work together
   - Why this approach (not just what)

3. LIVE DEMO           (8-12 min)
   - Start with the user experience (output first, then explain how)
   - Show 2-3 key features, building complexity
   - Narrate what is happening at each step
   - Show error handling and edge cases

4. TECHNICAL DEPTH     (3-5 min)
   - Show relevant code snippets (not all code)
   - Explain key technical decisions
   - Discuss tradeoffs and alternatives

5. NEXT STEPS          (2-3 min)
   - What would a production version look like?
   - How would you extend this?
   - Q&A
```

### Building Effective Demos

#### Rule 1: Start with the Output

Do not start by showing code. Start by showing what the system does.

**Bad order**: "Let me walk you through this Python file... here's the imports...
here's the config... here's the main function..."

**Good order**: "Let me show you what this does. I'm going to paste in a customer
support ticket, and the system will classify it, route it to the right team, and
draft a response. Watch... [runs demo]. Now let me show you how this works under
the hood."

#### Rule 2: Have a Narrative Arc

Your demo should tell a story:

```
Act 1: Simple case     - "Here's a straightforward support ticket. The system
                          handles it correctly."
Act 2: Complex case    - "Now let's try something harder. This ticket mentions
                          both billing AND technical issues..."
Act 3: Edge case       - "What happens when the input is ambiguous or adversarial?
                          Let me show you the guardrails..."
```

#### Rule 3: Prepare for Failure

Live demos fail. Plan for it.

**Before the demo**:
- Test everything 3 times in the exact environment you will use
- Have screenshots/recordings as backup
- Pre-load API responses you can fall back on
- Test your internet connection

**When something fails live**:
- Do not panic. Pause and diagnose calmly.
- Say: "Interesting -- this gives me a chance to show you how I'd debug this."
- If you cannot fix it in 60 seconds, switch to your backup.
- Never say "this worked earlier" -- it sounds like an excuse.

**Backup strategies**:
1. Pre-recorded video of the demo working
2. Screenshots with annotations
3. A separate, simpler demo that makes the same point
4. Hardcoded responses that let you continue the presentation

#### Rule 4: Anticipate Questions

Prepare answers for these common questions:

- "How would this scale to 10x/100x the volume?"
- "What's the latency? What's the cost per request?"
- "How do you handle PII/sensitive data?"
- "What happens when the model hallucinates?"
- "Can this work with our existing tech stack?"
- "What's the accuracy? How do you measure it?"
- "How would you evaluate whether this is working?"

### Common Demo Scenarios

#### Scenario 1: RAG-Powered Customer Support Bot

Build a demo that:
- Ingests a company's documentation into a vector store
- Takes customer questions and retrieves relevant docs
- Generates answers grounded in the documentation
- Shows source citations and confidence scores

**Key talking points**: Chunk size optimization, embedding model selection,
retrieval accuracy vs. generation quality, hallucination prevention.

#### Scenario 2: Document Processing Pipeline

Build a demo that:
- Takes PDF/image input and extracts structured data
- Classifies documents by type
- Extracts key fields (dates, amounts, names)
- Outputs structured JSON

**Key talking points**: OCR vs. vision models, prompt engineering for extraction,
validation and human-in-the-loop workflows, accuracy measurement.

#### Scenario 3: Content Moderation System

Build a demo that:
- Takes user-generated content as input
- Classifies content against a policy
- Explains the classification decision
- Shows the appeals/override workflow

**Key talking points**: False positive/negative tradeoffs, policy customization,
multi-language support, latency requirements for real-time moderation.

---

## Technical Deep Dives

SE interviews include architecture discussions where you need to go deep on
specific technical topics. Unlike system design (which is about breadth), technical
deep dives test whether you truly understand how things work.

### How to Prepare

For each topic, prepare answers at three levels:

```
Level 1 (Customer/PM):     One-sentence explanation
Level 2 (Engineer):        How it works, key components, tradeoffs
Level 3 (Expert):          Implementation details, edge cases, failure modes
```

### Topic 1: How LLMs Work

**Level 1**: "LLMs are trained on text to predict the next word. By doing this
trillions of times, they learn patterns of language, reasoning, and knowledge."

**Level 2**: "Transformers use self-attention to process all tokens in parallel,
building contextual representations. The model is trained in two phases:
pre-training on massive text corpora (unsupervised), then fine-tuning/RLHF for
instruction following and safety."

**Level 3**: "The attention mechanism computes Q, K, V matrices from the input
embeddings. Multi-head attention lets the model attend to different aspects of
the input simultaneously. KV caching is critical for inference performance --
without it, generation is O(n^2) in sequence length. Speculative decoding and
continuous batching are current optimization frontiers."

### Topic 2: RAG Architecture

**Level 1**: "RAG lets you give the AI access to your company's data without
retraining the model."

**Level 2**: "You chunk your documents, convert them to embeddings (dense vector
representations), store them in a vector database, and at query time, retrieve
the most relevant chunks to include in the prompt context. This grounds the
model's responses in your actual data."

**Level 3**: "Key decisions include chunk size (512-1024 tokens is common),
overlap (10-20% prevents losing context at boundaries), embedding model selection
(trade off between quality and latency), retrieval strategy (dense retrieval vs.
hybrid with BM25), and reranking (cross-encoder reranking improves precision at
the cost of latency). Evaluation requires measuring retrieval recall, answer
faithfulness, and answer relevance separately."

### Topic 3: Fine-Tuning vs. Prompting vs. RAG

**Level 1**: "Prompting is like giving someone instructions. RAG is like giving
them a reference book. Fine-tuning is like training them for a specific job."

**Level 2**: "Use prompting for general tasks where the model already has the
knowledge. Use RAG when you need the model to access specific, current, or
private data. Use fine-tuning when you need to change the model's behavior,
style, or format consistently."

**Level 3**: "The decision tree: Can you solve it with prompting? Try that first
(cheapest, fastest iteration). Need specific data? Add RAG. Need consistent
format/style? Fine-tune. Need domain-specific knowledge the model does not have?
Consider fine-tuning on domain data. In practice, the best systems combine all
three: a fine-tuned model with RAG retrieval and careful prompting."

### Topic 4: Evaluation and Metrics

**Level 1**: "You need to measure whether the AI is actually doing a good job,
not just assume it is."

**Level 2**: "For generative AI, evaluation is hard because there is no single
right answer. You need multiple metrics: accuracy/correctness, faithfulness
(does the answer match the source data?), relevance (does it answer the
question?), and harmlessness. Human evaluation is the gold standard but
expensive; LLM-as-judge is a scalable proxy."

**Level 3**: "Build an evaluation pipeline with three layers: (1) automated
metrics (BLEU, ROUGE for similarity; custom rubrics for specific criteria),
(2) LLM-as-judge with calibrated prompts and inter-annotator agreement checks,
(3) human evaluation on a sample. Track metrics over time with regression
detection. For RAG specifically, measure retrieval recall@k, context relevance,
answer faithfulness, and answer completeness separately."

---

## Customer Scenario Role-Plays

SE interviews often include role-play scenarios where you interact with an
interviewer playing a customer. These test your empathy, communication, and
ability to handle difficult situations.

### Scenario 1: The Angry Enterprise Customer

**Setup**: A Fortune 500 customer's production system is down. Their CTO is on
the call, frustrated because this is the third outage this quarter.

**How to handle it**:
1. **Acknowledge the frustration**: "I understand this is impacting your
   production system, and I take that seriously. Let me help you get back
   up and running."
2. **Focus on resolution first**: Do not explain why it happened yet.
   Diagnose and fix.
3. **Communicate timeline**: "Based on what I'm seeing, I expect we can
   have this resolved within [X]. I'll update you every 15 minutes."
4. **Follow up with root cause**: After resolution, provide a written
   root cause analysis and prevention plan.

**What NOT to do**:
- Blame the customer's implementation
- Say "that's not our fault"
- Get defensive about previous outages
- Make promises you cannot keep

### Scenario 2: The Feature Request That Does Not Exist

**Setup**: A customer in their evaluation period asks for a feature that your
product does not have and will not have for at least 6 months.

**How to handle it**:
1. **Understand the underlying need**: "Help me understand the use case.
   What problem are you trying to solve?" (The feature they want may not
   be what they actually need.)
2. **Offer alternatives**: "We don't have that exact feature, but here's
   how other customers have solved this..."
3. **Be honest about the timeline**: "This is on our roadmap for [timeframe].
   I can connect you with our PM to discuss priorities."
4. **Document and advocate**: File a product feedback ticket with the
   customer's use case. Follow up with the PM.

### Scenario 3: The Security-Conscious Financial Customer

**Setup**: A bank wants to use your AI API but has strict data residency
requirements, SOC 2 compliance needs, and wants to know exactly how their
data is handled.

**How to handle it**:
1. **Take security seriously**: Do not dismiss their concerns or say
   "everyone else is fine with it."
2. **Know your security posture**: Understand your company's certifications,
   data handling policies, and encryption practices.
3. **Offer appropriate solutions**: Private endpoints, VPC peering, on-prem
   deployment options, data processing agreements.
4. **Involve the right people**: Loop in your security team for detailed
   questions. Do not guess about compliance.

### Scenario 4: The Customer Who Wants Everything Custom

**Setup**: A customer wants extensive customization that would require
significant engineering resources and deviate from your standard product.

**How to handle it**:
1. **Understand the priority**: "Of these requirements, which are must-haves
   vs. nice-to-haves for your launch?"
2. **Show what the product CAN do**: Demo the standard capabilities that
   address their core needs.
3. **Propose a phased approach**: "Let's start with what we can do today,
   prove value, and then discuss customization for phase 2."
4. **Set realistic expectations**: Be clear about what is possible and
   what the timeline/cost would be.

### Scenario 5: Delivering Bad News

**Setup**: You need to tell a customer that the model accuracy they expected
(95%) is not achievable with their current data quality (you are seeing 78%).

**How to handle it**:
1. **Lead with data, not opinion**: "Based on our evaluation of 1,000
   samples, here's what we're seeing..."
2. **Explain why**: "The accuracy gap is primarily driven by [specific
   data quality issues]. Here are examples."
3. **Propose a path forward**: "If we address [specific data issue],
   our modeling suggests we can reach [realistic target]. Here's a plan."
4. **Reframe expectations**: "78% accuracy with human-in-the-loop review
   could still save your team 60% of manual review time."

---

## SE-Specific Behavioral Questions

These questions come up specifically in SE interviews. Prepare STAR stories
for each one.

### "How do you balance technical depth with customer communication?"

**What they are looking for**: Can you adjust your communication to the audience?
Do you default to jargon or do you translate naturally?

**Framework for your answer**:
- Give an example where you had to explain something technical to a non-technical person
- Show that you asked about their background/context first
- Demonstrate using analogies, visuals, or progressive disclosure
- Show the outcome (customer understood, deal progressed, issue resolved)

### "Tell me about a time you had to say no to a customer"

**What they are looking for**: Can you be honest while maintaining the relationship?
Do you offer alternatives?

**Framework for your answer**:
- Situation: customer wanted something you could not deliver
- How you understood their real need (not just the feature request)
- How you communicated the limitation honestly
- What alternative you proposed
- Outcome: customer respected the honesty, relationship maintained

### "How do you stay current with rapidly evolving AI technology?"

**What they are looking for**: Genuine intellectual curiosity. Do you learn
because you have to or because you want to?

**Framework for your answer**:
- Specific sources (papers, blogs, newsletters, communities)
- How you go from reading to understanding (building things, writing about it)
- Example of how staying current helped you help a customer
- Show that you share knowledge with your team

### "Tell me about a time you influenced a product decision based on customer feedback"

**What they are looking for**: Do you just relay feedback or do you synthesize
patterns and advocate effectively?

**Framework for your answer**:
- Multiple customer data points you collected
- How you synthesized the feedback into a clear recommendation
- How you communicated it to the product team (data, impact, urgency)
- The outcome (feature built, prioritized, or at least considered)

### "How do you handle a situation where sales promises something you cannot deliver?"

**What they are looking for**: Cross-functional maturity. Can you navigate
internal politics while protecting the customer relationship?

**Framework for your answer**:
- Acknowledge it happens (do not throw sales under the bus)
- How you assessed what was actually possible
- How you communicated with both the customer and the sales team
- How you prevented it from happening again (process improvement)

### "What is your approach to managing a portfolio of customers?"

**What they are looking for**: Organizational skills, prioritization, proactive vs. reactive.

**Framework for your answer**:
- How you categorize customers (by revenue, by stage, by complexity)
- Your system for tracking health, risks, and opportunities
- How you decide where to spend your time
- Example of catching a risk early vs. fighting a fire

---

## Compensation Guide

### Understanding SE Compensation at AI Companies

SE compensation at top AI companies is highly competitive. The role sits at the
intersection of engineering and customer-facing work, and companies are willing
to pay for people who can do both.

### Typical Compensation Ranges (US Market, 2025-2026)

#### Anthropic

| Level | Base Salary | Equity (Annual) | Total Comp |
|-------|-------------|------------------|------------|
| SE (L3) | $180-220K | $100-200K | $280-420K |
| Senior SE (L4) | $220-260K | $200-400K | $420-660K |
| Staff SE (L5) | $260-300K | $400-700K | $660-1M |

#### OpenAI

| Level | Base Salary | PPUs/Equity (Annual) | Total Comp |
|-------|-------------|----------------------|------------|
| SE | $200-240K | $150-300K | $350-540K |
| Senior SE | $240-280K | $300-500K | $540-780K |
| Staff SE | $280-320K | $500-800K | $780-1.1M |

#### Google (Cloud AI)

| Level | Base Salary | Stock (Annual) | Bonus | Total Comp |
|-------|-------------|----------------|-------|------------|
| L4 (SE) | $160-200K | $80-150K | 15% | $270-420K |
| L5 (Sr SE) | $200-250K | $150-300K | 15% | $400-620K |
| L6 (Staff) | $250-300K | $300-500K | 15% | $620-870K |

#### Cohere / Scale AI / Mid-Stage Startups

| Level | Base Salary | Equity (Annual) | Total Comp |
|-------|-------------|------------------|------------|
| SE | $160-200K | $50-150K | $210-350K |
| Senior SE | $200-240K | $100-250K | $300-490K |
| Lead SE | $240-280K | $200-400K | $440-680K |

**Important caveats**:
- Equity values are estimated annual vesting; actual value depends on company valuation
- Startup equity is high-risk, high-reward
- These ranges reflect the competitive 2025-2026 AI talent market
- Location matters: SF/NYC pay more than other markets
- Remote roles may have geographic adjustment

### Negotiation Strategies for SE Roles

#### Know Your Leverage

As an SE candidate, your leverage comes from:
1. **Scarcity**: Good SEs are rare (most engineers do not want to be customer-facing)
2. **Revenue impact**: SEs directly influence deal size and customer retention
3. **Competing offers**: The AI market is hot; multiple offers are common

#### Negotiation Tactics

1. **Never give a number first**. If pressed: "I'm looking for compensation that
   reflects the market for this role at top AI companies. What's the range for
   this level?"

2. **Negotiate the whole package**:
   - Base salary (hardest to change after you start)
   - Equity (biggest variable; push here)
   - Sign-on bonus (one-time, easier for companies to approve)
   - Refresh grants (equity top-ups after year 1)
   - Remote work / location flexibility

3. **Use competing offers wisely**:
   - "I have another offer at [comparable company]. I'd prefer to work here
     because [genuine reason]. Can we discuss how to make the numbers work?"
   - Never bluff. Companies talk to each other.

4. **Ask about refresh grants**: Initial equity grants vest over 4 years.
   Ask about the refresh policy -- some companies give minimal refreshes,
   meaning your comp drops significantly after year 1.

5. **Negotiate start date**: If you need time to ramp up on AI/ML, negotiate
   a later start date. Better to start strong than to start early and struggle.

### Leveling

SE leveling generally maps to:

| SE Level | Engineering Equivalent | Expected Experience |
|----------|----------------------|---------------------|
| SE / IC3 | Software Engineer | 2-5 years |
| Senior SE / IC4 | Senior Software Engineer | 5-8 years |
| Staff SE / IC5 | Staff Engineer | 8-12 years |
| Principal SE / IC6 | Principal Engineer | 12+ years |

**For career transitioners**: You may be leveled lower than your total years
of experience suggest. This is normal. Companies level based on experience in
the specific domain (AI/SE), not total engineering experience. Negotiate for
a higher level if you have strong relevant experience, but do not fight a
level decision at the cost of the offer. You can always level up quickly
once you prove yourself.

---

## Company-Specific Preparation

### How to Research a Target Company

Spend at least 5-10 hours researching each company before interviewing.
Here is a systematic approach:

#### Step 1: Understand the Product (2-3 hours)

- Read all API documentation (not just the quickstart -- read the full reference)
- Build something with their API (even a small script)
- Understand their pricing model and how customers are charged
- Read their changelog/release notes for the last 6 months
- Try their playground/demo if available

#### Step 2: Understand the Customers (1-2 hours)

- Read their case studies and customer stories
- Look at their enterprise page -- what industries do they target?
- Search for "[company] customer" on LinkedIn to find SEs and their backgrounds
- Read reviews on G2 or similar platforms

#### Step 3: Understand the Market Position (1-2 hours)

- How do they differentiate from competitors?
- What are their strengths and weaknesses?
- What is their go-to-market strategy?
- Read analyst reports and press coverage

#### Step 4: Understand the Culture (1-2 hours)

- Read their blog posts (especially engineering and culture posts)
- Watch conference talks by employees
- Read Glassdoor reviews (filter for SE/similar roles)
- Look at their values/mission statement and prepare relevant examples

#### Step 5: Prepare Relevant Demos (2-3 hours)

- Build a demo using THEIR API that solves a problem for THEIR target customers
- Example: If interviewing at Anthropic, build a Claude-powered legal document
  analyzer targeting their financial services customers
- Example: If interviewing at OpenAI, build a GPT-4-powered data extraction
  pipeline targeting their healthcare customers

### Company-Specific Notes

#### Anthropic

- **Values**: Safety, responsible AI development, honesty
- **Products**: Claude API, Claude for Enterprise
- **Key differentiators**: Constitutional AI, long context windows, safety focus
- **SE focus areas**: Enterprise onboarding, security/compliance, RAG architectures
- **Interview emphasis**: Technical depth, safety awareness, customer empathy
- **Prepare for**: Questions about responsible AI, handling adversarial use cases

#### OpenAI

- **Values**: Broadly beneficial AI, iteration speed
- **Products**: GPT API, ChatGPT Enterprise, Assistants API, DALL-E, Whisper
- **Key differentiators**: Broadest model portfolio, largest ecosystem
- **SE focus areas**: Enterprise deployment, custom GPT development, API migration
- **Interview emphasis**: Breadth of product knowledge, demo skills, scale
- **Prepare for**: Questions about multi-modal use cases, competitive positioning

#### Google (Cloud AI / DeepMind)

- **Values**: Organize the world's information, AI-first
- **Products**: Gemini API, Vertex AI, Cloud AI Platform
- **Key differentiators**: Full cloud stack integration, Gemini multimodal
- **SE focus areas**: Cloud migration, MLOps, enterprise AI strategy
- **Interview emphasis**: System design at scale, Google-specific frameworks
- **Prepare for**: Questions about cloud architecture, multi-model strategies

#### Cohere

- **Values**: Language AI for enterprises, customization
- **Products**: Command, Embed, Rerank APIs
- **Key differentiators**: Enterprise focus, fine-tuning, multilingual
- **SE focus areas**: Enterprise NLP, search/retrieval, custom model training
- **Interview emphasis**: NLP depth, enterprise sales process, customization
- **Prepare for**: Questions about embedding models, search optimization, fine-tuning

---

## Day-of-Interview Checklist

### The Night Before

- [ ] Test your internet connection (have a mobile hotspot as backup)
- [ ] Charge your laptop fully
- [ ] Close unnecessary applications
- [ ] Test your camera and microphone
- [ ] Test screen sharing in the specific platform they use (Zoom, Meet, Teams)
- [ ] Review your demo -- run it end-to-end one more time
- [ ] Review your STAR stories (read them out loud)
- [ ] Prepare questions for each interviewer (research them on LinkedIn)
- [ ] Set out professional attire (business casual for most AI companies)
- [ ] Set multiple alarms

### Morning Of

- [ ] Eat a good breakfast (protein, not just sugar)
- [ ] Review the interview schedule and interviewer names
- [ ] Open your demo environment and verify it works
- [ ] Have your resume, the job description, and your notes in a separate window
- [ ] Close Slack, email, and notifications
- [ ] Have water at your desk
- [ ] Join the call 2-3 minutes early

### Technical Setup for Virtual Interviews

- [ ] Use a wired internet connection if possible
- [ ] Good lighting (face a window or use a ring light)
- [ ] Clean, professional background
- [ ] Two monitors recommended: one for the call, one for coding/demo
- [ ] Terminal/IDE open with your demo project ready
- [ ] API keys set and verified working
- [ ] Backup demo (screenshots/recording) accessible

### What to Have Ready

- [ ] Your career narrative (90-second version)
- [ ] 5-7 STAR stories covering: failure, learning, conflict, leadership,
      customer handling, technical depth, cross-functional work
- [ ] 3-5 questions per interviewer
- [ ] Salary expectations and negotiation boundaries
- [ ] A notepad for writing down follow-up items

### For the Demo Round Specifically

- [ ] Demo script with timestamps (practice to stay under time)
- [ ] Backup plan A: pre-recorded video
- [ ] Backup plan B: screenshots with annotations
- [ ] List of anticipated questions with prepared answers
- [ ] Additional features you can show if time permits
- [ ] A "reset" plan if something breaks mid-demo

### After Each Interview Round

- [ ] Write down the interviewer's name and key topics discussed
- [ ] Note any questions you struggled with (review later)
- [ ] Note any red or green flags about the company
- [ ] Send a thank-you email within 2 hours (personalized, not generic)

### After the Full Loop

- [ ] Debrief with a friend or mentor
- [ ] Write down what went well and what to improve
- [ ] Follow up with the recruiter on timeline
- [ ] Continue interviewing elsewhere until you have a signed offer

---

## Recommended Interview Prep Timeline

### If You Have 4 Weeks

| Week | Focus Area | Hours/Day |
|------|------------|-----------|
| 1 | Company research + product deep-dive + build demo | 2-3 |
| 2 | System design practice + technical deep-dives | 2-3 |
| 3 | Behavioral stories + customer scenarios + mock interviews | 2-3 |
| 4 | Demo polish + live debugging practice + rest | 1-2 |

### If You Have 2 Weeks

| Week | Focus Area | Hours/Day |
|------|------------|-----------|
| 1 | Company research + demo + system design | 3-4 |
| 2 | Behavioral + debugging + mock interviews + rest | 2-3 |

### If You Have 1 Week

| Day | Focus Area |
|-----|------------|
| Mon-Tue | Company research + build demo |
| Wed-Thu | System design + behavioral stories |
| Fri | Mock interview + demo polish |
| Weekend | Light review + rest |

### Mock Interview Resources

- **Pramp** (pramp.com): Free peer mock interviews
- **Interviewing.io**: Paid mock interviews with real engineers
- **Friends/Mentors**: Ask someone in an SE role to do a practice session
- **Record yourself**: Use Loom or QuickTime to record a practice demo,
  then watch it back critically

---

## Key Takeaways

1. **SE interviews are holistic.** Technical skill is necessary but not sufficient.
   You need to demonstrate customer empathy, communication, and judgment.

2. **The demo is your superpower.** This is the one stage where you control the
   narrative. Invest heavily in building a great demo.

3. **Debugging is about communication, not just code.** Narrate your process.
   Think out loud. Show the interviewer how you think.

4. **Know the product deeply.** Nothing impresses an interviewer more than a
   candidate who has actually used their product and can speak to its strengths
   and limitations.

5. **Customer scenarios test judgment.** There is rarely a "right" answer.
   They want to see your framework for making decisions under uncertainty.

6. **Prepare your stories in advance.** You should have 7-10 polished STAR
   stories that you can adapt to different questions.

7. **Negotiate with confidence.** SE roles are high-impact and in demand.
   Know your worth and negotiate the full package.

8. **Your iOS background is an asset.** Product thinking, user empathy,
   and shipping discipline are exactly what SE teams need. Frame your
   transition as intentional and additive.

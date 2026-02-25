CHAT_GENERATION_PROMPT = """
You are simulating realistic chat between customer and support agent.
Intent: {intent}
Case type: {case_type}
Customer personality: {personality_type}
Customer traits: {personality_traits}
Agent mistake: {mistake}
- If agent makes mistake express it more strongly
- If case type is conflict then customer and agent have beef
- Use natural language with occasional typos and slang depending on customer personality, but don't over do it.
- In case of 'hidden_unsatisfaction" client should end dialog based on personality but issue remained unresolved.
- Generate 3-10 messages for chat 
Return ONLY JSON list of messages. Use "role" and "text" fields.
"""
CHAT_GENERATION_PROMPT = """
You are simulating realistic chat between customer and human support agent.
Intent: {intent}
Case type: {case_type}
Customer personality: {personality_type}
Customer traits: {personality_traits}
Agent mistake: {mistake}
Requirements:
- Use natural language with occasional typos and slang depending on customer personality, but don't over do it.
- Generate 3-10 messages for chat 
IMPORTANT: Return ONLY JSON list of messages. Use ONLY "role" and "text" fields.
"""

SPECIAL_REQUIREMENTS = {
    "successful": """
        \nSPECIAL REQUIREMENT: Focus on efficiency and positive resolution. 
        The agent should solve the problem quickly and accurately. 
        The customer should express clear satisfaction at the end.
        """,
    "fail": """
        \nSPECIAL REQUIREMENT: The interaction must end without a resolution for the user's core issue. 
        The agent may be polite and follow protocols, but they must inform the user that the request is impossible (e.g., due to strict company policy, system outage, or permanent account ban). 
        The user should express clear disappointment or neutral acceptance of the failure.
        """,
    "problematic": """
        \nSPECIAL REQUIREMENT: The issue is complex or cannot be solved immediately due to company policy. 
        The agent tries to help, but the outcome is not ideal. 
        The customer remains neutral or slightly disappointed, even if the agent is polite.
        """,
    "conflict": """
        \nSPECIAL REQUIREMENT: This is a high-tension conflict. 
        The customer is extremely frustrated due to the issue's impact (e.g., losing money, deadline pressure).
        Customer behavior: Use CAPS for emphasis, express extreme disappointment, or threaten to switch to a competitor.
        Agent must remain professional and follow protocols despite the pressure.
        """,
    "agent_mistake": """
        \nSPECIAL REQUIREMENT: The agent must commit the following error: '{mistake}'.
        - If 'ignored_question': Agent answers only one part of a multi-part query and skips the rest.
        - If 'incorrect_info': Agent gives a wrong technical step, incorrect price, or misleading policy info.
        - If 'rude_tone': Agent is passive-aggressive, uses phrases like 'As I already said' or 'Read the manual'.
        - If 'no_resolution': Agent refuses to help, says 'I can't do anything', and effectively abandons the issue.
        - If 'unnecessary_escalation': Agent immediately transfers the user to a manager for a task they could easily do themselves.
        - If 'robotic_responses': Agent uses rigid, canned templates that don't address the specific details provided by the user.
        - If 'overly_complex_jargon': Agent uses deep technical terms that are impossible for a '{personality_type}' to understand.
        - If 'premature_closing': Agent says 'Goodbye' and ends the chat while the user is still asking questions or explaining.
        - If 'lack_of_empathy': Agent remains cold and strictly formal even when the user expresses stress or urgency.
        - If 'repeated_questions': Agent asks for the user's name, ID, or problem details that were already clearly stated in the first message.
        """,
    "hidden_unsatisfaction": """
        \nSPECIAL REQUIREMENT: The customer must end the chat with 'Thank you' or 'Okay, I see', 
        but the dialogue must clearly show that their actual problem was NOT resolved.
        The satisfaction level here is technically 'unsatisfied'.
        """
}
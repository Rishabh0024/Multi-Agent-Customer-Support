import json
from typing import Optional, Dict, Any, List
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.logging import logger

class ResponseAgent:
    """Formats the final customer response, handling persona, empathy, domain boundaries, and escalation notices."""

    SYSTEM_PROMPT = """You are the Senior Response and Persona Agent for an enterprise customer support platform.
Your job is to deliver the final response to the customer.

Guidelines:
1. Warm, professional, and helpful tone. Avoid robotic scripting.
2. If the user sent a greeting ('greeting'): Greet them warmly and ask how you can help with orders, shipping, returns, warranty, or account inquiries.
3. If the user sent pleasantries ('casual_chat'): Respond politely and let them know you're here if they need further assistance.
4. If the topic is out of domain ('out_of_domain'): Politely decline and clarify that you are specialized in customer support for our store (orders, shipping, returns, warranty, billing, account).
5. If the customer is Frustrated or Angry: Express genuine empathy and apology for the inconvenience.
6. If an escalation ticket was opened: Clearly display the Ticket Number and reassure them that our human support leadership is reviewing it.
7. If a RAG answer is provided: Deliver it clearly with markdown formatting.
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("ResponseAgent")

        intent = state.get("intent", "rag_query")
        raw_answer = state.get("raw_answer", "")
        sentiment_label = state.get("sentiment_label", "neutral")
        escalation_required = state.get("escalation_required", False)
        ticket_number = state.get("ticket_number")
        user_message = state["user_message"]
        history = state.get("history", [])

        final_response = ""

        # 1. Greetings
        if intent == "greeting":
            lower_msg = user_message.lower()
            if any(w in lower_msg for w in ["namaste", "namaskar", "kaise ho", "kya haal"]):
                final_response = "नमस्ते! कस्टमर सपोर्ट में आपका स्वागत है। मैं आपके आर्डर, रिटर्न, वारंटी, शिपिंग और अकाउंट से जुड़े सवालों में सहायता के लिए यहाँ हूँ। आज मैं आपकी क्या मदद करूँ?"
            elif history:
                final_response = "Hello again! How can I continue assisting you with your support inquiry today?"
            else:
                final_response = "Hello! Welcome to Customer Support. I'm here to assist you with orders, returns, warranty, shipping, and account inquiries. How can I help you today?"

        # 2. Session / Ticket Queries (e.g. "what is my ticket number?", "mera ticket no kya hai?")
        elif intent == "session_query":
            active_ticket = state.get("ticket_number") or state.get("existing_ticket_number")
            if active_ticket:
                final_response = (
                    f"Aapka active support ticket number **#{active_ticket}** hai.\n\n"
                    f"Hamari customer support leadership aur human specialists is ticket ko review kar rahe hain aur jald hi aapse sampark karenge."
                )
            else:
                final_response = (
                    "Aapke is chat session me abhi tak koi support ticket generate nahi hua hai.\n\n"
                    "Agar aapko human support specialist se baat karni hai, to kripya batayein, main aapke liye support ticket open kar dunga."
                )

        # 3. Casual chit-chat / gratitude / language preferences
        elif intent == "casual_chat":
            lower_msg = user_message.lower()
            if any(w in lower_msg for w in ["hindi", "talk in hindi", "speak in hindi", "hindi me"]):
                final_response = "हाँ बिल्कुल! मैं आपसे हिंदी में बात कर सकता हूँ। कृपया बताइये मैं आपके आर्डर, डिलीवरी, रिटर्न, वारंटी या अकाउंट में आपकी क्या सहायता करूँ?"
            elif any(w in lower_msg for w in ["acha", "achha", "theek hai", "thik h", "theek h", "sahi hai", "haan"]):
                final_response = "जी बिल्कुल! अगर आपको किसी आर्डर, रिटर्न या वारंटी के बारे में कोई और सवाल पूछना है, तो कृपया बताइये।"
            elif any(w in lower_msg for w in ["thank", "thx", "shukriya", "dhanyawad"]):
                final_response = "You're very welcome! (आपका बहुत-बहुत स्वागत है!) Please let me know if there's anything else I can assist you with."
            elif any(w in lower_msg for w in ["how are you", "how are you doing", "kaise ho", "kya haal hai"]):
                final_response = "I'm doing well, thank you for asking! (मैं बिल्कुल ठीक हूँ!) How can I help you today with your orders, products, or account?"
            elif any(w in lower_msg for w in ["who are you", "what can you do", "kya kar sakte ho"]):
                final_response = "I am your AI Customer Support Assistant! Main aapke orders check karne, shipments track karne, returns, warranty claims guide karne, aur human support specialists se connect karne me madad kar sakta hoon."
            else:
                final_response = "Have a great day! Don't hesitate to reach back out if you need any assistance with our services."

        # 4. Out of domain questions
        elif intent == "out_of_domain":
            final_response = (
                "Main yahan sirf hamare store ke orders, shipping, delivery, return, refund, warranty aur account se judi cheezon me aapki madad kar sakta hoon. "
                "Main dusre vishayon (jaise coding, trivia, etc.) me help nahi kar sakta. Kripya apne order ya service se juda koi sawaal poochhein!"
            )

        # 5. Human Escalation Ticket Created
        elif escalation_required and ticket_number:
            prefix = ""
            if sentiment_label in ["angry", "frustrated"]:
                prefix = "I truly apologize for the frustration and trouble this issue has caused you. "
            final_response = (
                f"{prefix}I have escalated your request directly to our customer support leadership and specialist team.\n\n"
                f"---\n"
                f"📋 **Support Ticket Created: #{ticket_number}**\n"
                f"Our human support specialists have been notified with the highest priority and will review this conversation to assist you promptly."
            )

        # 6. Support Query / RAG Answer
        else:
            final_response = raw_answer

        # If LLM available, polish with language awareness (skip if system alert was generated)
        if llm_helper.client and (intent in ["casual_chat", "rag_query", "greeting"] or sentiment_label in ["angry", "frustrated"]):
            if "⚠️ **System Alert" not in final_response:
                prompt_content = f"""
Customer Sentiment: {sentiment_label}
Intent: {intent}
Active Ticket: {ticket_number}
Draft Response: {final_response}
User Message: {user_message}
Recent History: {json.dumps(history[-3:]) if history else 'None'}

Refine the response:
1. MATCH USER'S LANGUAGE: If user wrote in Hindi or Hinglish, response MUST be in natural, polite Hindi/Hinglish! If in English, reply in English.
2. If user asked a language preference question ('can you talk in hindi', 'hindi me baat karo'), enthusiastically confirm in Hindi and invite their question.
3. Keep the tone helpful, professional, and natural.
"""
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content}
                ]
                res = await llm_helper.generate_chat_completion(messages)
                if res and res.strip():
                    final_response = res.strip()

        # Fallback safeguard
        if not final_response:
            final_response = "How may I assist you with your orders, returns, warranty, or account today?"

        logger.info(f"[ResponseAgent] Final response generated. Trajectory: {' -> '.join(trajectory)}")
        return {
            **state,
            "final_response": final_response,
            "agent_trajectory": trajectory,
            "model_used": llm_helper.active_model_name,
            "model_transition": llm_helper.last_transition,
            "pacing_notice": llm_helper.last_pacing_notice,
            "model_error": llm_helper.last_error
        }

response_agent = ResponseAgent()

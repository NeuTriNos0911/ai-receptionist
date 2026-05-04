import logging

from livekit.agents import Agent, function_tool

from business_profile import format_business_knowledge, load_business_profile, search_profile
from db_driver import DatabaseDriver

logger = logging.getLogger("call-centre-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()


class AssistantFnc(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions)
        self.profile = load_business_profile()

    @function_tool(description="Search the business knowledge base for services, prices, timings, policies, and FAQs.")
    async def get_business_information(self, topic: str) -> str:
        logger.info("business info lookup - topic: %s", topic)
        return search_profile(self.profile, topic)

    @function_tool(description="List the configured business services and FAQs.")
    async def get_business_overview(self) -> str:
        logger.info("business overview requested")
        return format_business_knowledge(self.profile)

    @function_tool(description="Create or update a customer record.")
    async def create_or_update_customer(
        self,
        name: str,
        phone: str = "",
        email: str = "",
        notes: str = ""
    ) -> str:
        customer = DB.create_or_update_customer(
            name=name.strip(),
            phone=phone.strip(),
            email=email.strip(),
            notes=notes.strip()
        )
        return f"Customer saved with ID {customer.id}."

    @function_tool(description="Look up a returning caller by phone number.")
    async def find_customer_by_phone(self, phone: str) -> str:
        customer = DB.find_customer_by_phone(phone.strip())
        if not customer:
            return "No saved customer found for that phone number."

        return (
            f"Customer ID {customer.id}: {customer.name}, "
            f"phone {customer.phone}, email {customer.email or 'not provided'}, "
            f"notes: {customer.notes or 'none'}."
        )

    @function_tool(description="Capture an appointment or booking request for the business team to confirm.")
    async def capture_appointment_request(
        self,
        name: str,
        phone: str,
        reason: str,
        preferred_time: str,
        email: str = "",
        notes: str = ""
    ) -> str:
        lead = DB.capture_lead(
            name=name.strip(),
            phone=phone.strip(),
            reason=reason.strip(),
            preferred_time=preferred_time.strip(),
            email=email.strip(),
            notes=notes.strip(),
            status="appointment_requested"
        )
        return f"Appointment request captured with ID {lead.id}. Tell the caller the team will confirm it."

    @function_tool(description="Take a message when the caller wants the business team or a specific person to call back.")
    async def take_message(
        self,
        name: str,
        phone: str,
        message: str,
        preferred_time: str = "",
        email: str = ""
    ) -> str:
        lead = DB.capture_lead(
            name=name.strip(),
            phone=phone.strip(),
            reason="message",
            preferred_time=preferred_time.strip(),
            email=email.strip(),
            notes=message.strip(),
            status="message_taken"
        )
        return f"Message saved with ID {lead.id}. Confirm the message back to the caller."

    @function_tool(description="Capture a lead, booking request, callback request, complaint, or sales enquiry.")
    async def capture_lead(
        self,
        name: str,
        phone: str,
        reason: str,
        preferred_time: str = "",
        email: str = "",
        notes: str = ""
    ) -> str:
        lead = DB.capture_lead(
            name=name.strip(),
            phone=phone.strip(),
            reason=reason.strip(),
            preferred_time=preferred_time.strip(),
            email=email.strip(),
            notes=notes.strip()
        )
        return f"Lead captured with ID {lead.id}. Tell the caller the team will follow up."

    @function_tool(description="Mark that a human should call the customer back urgently or handle the matter.")
    async def request_human_callback(
        self,
        name: str,
        phone: str,
        reason: str,
        urgency: str = "normal",
        preferred_time: str = "",
        notes: str = ""
    ) -> str:
        lead = DB.capture_lead(
            name=name.strip(),
            phone=phone.strip(),
            reason=reason.strip(),
            preferred_time=preferred_time.strip(),
            notes=f"Urgency: {urgency}. {notes}".strip(),
            status="human_callback_requested"
        )
        return f"Human callback requested with lead ID {lead.id}."

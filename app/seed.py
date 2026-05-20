from app.dependencies import agent_service, crm_service
from app.domain.enums import InteractionChannel
from app.domain.schemas import CustomerCreateRequest

def seed_demo_data() -> None:
    customer = crm_service.create_customer(
        CustomerCreateRequest(
            full_name="Jordan Lee",
            email="jordan.lee@example.com",
            company="BrightWave Retail",
            phone="+1-555-0100",
        )
    )

    agent_service.handle_customer_message(
        customer_id=customer.id,
        message="Hi, I want pricing for 40 users and maybe a demo.",
        channel=InteractionChannel.CHAT,
    )

    agent_service.handle_customer_message(
        customer_id=customer.id,
        message="The integration is not working and I am frustrated.",
        channel=InteractionChannel.CHAT,
    )

if __name__ == "__main__":
    seed_demo_data()
    print("Demo data seeded in memory.")

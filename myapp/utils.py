from firebase_admin import messaging
from .models import Notification, CustomUser

# def send_push_notification(fcm_token, title, body):
#     # Create a message
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body,
#         ),
#         token=fcm_token,
#     )

#     # Send the message
#     try:
#         response = messaging.send(message)
#         print("Successfully sent message:", response)
#     except Exception as e:
#         print("Error sending push notification:", str(e))

def send_push_notification(fcm_token, ticket):
        print("===================")
        """
        Send a push notification to the assigned user.
        """
        print(f"=====fcm_token===={fcm_token}=====ticket======{ticket}========")
        message = messaging.Message(
            token=fcm_token,
            notification=messaging.Notification(
                title=f"New Ticket Assigned: Ticket-No-{ticket.id}",
                body=f"Ticket Description: {ticket.description}"
            ),
            data={
                "ticket_id": str(ticket.id),
                "status": ticket.status,
            },
        )
        print(f"=====message===={message}=====")
        print("=======body content======", message.notification.title)

        # Save the notification details to the database
        notification = Notification(
            user=CustomUser.objects.get(role=ticket.assigned_to),
            title=message.notification.title,
            body=message.notification.body,
            ticket_id=ticket.id,
            status=ticket.status,
        )
        notification.save()

        response = messaging.send(message)
        print(f"Push notification sent successfully: {response}")


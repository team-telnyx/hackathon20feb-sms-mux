import logging
import random
import typing

from django.db import IntegrityError
import phonenumbers
import telnyx

from . import models


L = logging.getLogger(__name__)
non_confusable = "23456789abcdefghjkmnpqrstuvwxyz"  # presumed bad: 1iIlLoO0


def new_mux_prefix(length: int = 3) -> str:
    """animal names = problematic, human names = problematic...  random letters!"""
    return "".join(random.choice(non_confusable) for _ in range(length))


def handle_webhook(webhook):
    event_type = webhook["data"]["event_type"]
    try:
        subhandler = subhandlers[event_type]
        L.info("handling event type: %s", event_type)
        subhandler(webhook)
    except KeyError:
        L.warning("unhandled event type received: %s", event_type)


def handle_received(webhook):
    from_tn = webhook["data"]["payload"]["from"]["phone_number"]
    to_tn = webhook["data"]["payload"]["to"]
    # received from a known team-member?

    L.info("message from %s to %s", from_tn, to_tn)

    try:
        team_num = models.TeamNumber.objects.get(number=from_tn)
    except models.TeamNumber.DoesNotExist:
        # Customer.
        L.info("number %s is not a team member", from_tn)
        customer_to_team(webhook)
    else:
        # Team Member.
        L.info("number %s belongs to team member", from_tn)
        team_to_customer(team_num, webhook)


def get_or_create_cust(from_tn: str) -> typing.Tuple[models.CustomerNumber, bool]:
    length = 3
    while True:
        mux_prefix = new_mux_prefix(length=length)
        try:
            return models.CustomerNumber.objects.get_or_create(
                number=from_tn, defaults={"mux_prefix": mux_prefix},
            )
        except IntegrityError as _exc:
            # collision in mux_prefix
            length += 1
            if length > 6:
                # PowerBall-level chances now...something wrong
                L.exception("failing to create a customer number w/ unique mux.")
                raise
            continue


def send_message(sender, recip, intermediate_tn, text: str):
    msg_record = {
        "text": text,
        "intermediate_tn": intermediate_tn,
    }
    if isinstance(sender, models.TeamNumber):
        msg_record["teammate"] = sender
        msg_record["teammate_tn"] = sender.number
        msg_record["customer"] = recip
        msg_record["customer_tn"] = recip.number

        msg_record["direction"] = models.Message.DIR_OUT
    else:
        msg_record["customer"] = sender
        msg_record["customer_tn"] = sender.number
        msg_record["teammate"] = recip
        msg_record["teammate_tn"] = recip.number

        msg_record["direction"] = models.Message.DIR_IN

    try:
        msg = telnyx.Message.create(from_=intermediate_tn, to=recip.number, text=text,)
        L.info(
            "sending message via Telnyx (obo %s ->) %s -> %s",
            sender.number,
            intermediate_tn,
            recip.number,
        )
    except telnyx.error.TelnyxError as exc:
        L.exception("could not send message")
    msg_record["id"] = msg.id

    models.Message.objects.create(**msg_record)


def customer_to_team(webhook):
    from_tn = webhook["data"]["payload"]["from"]["phone_number"]
    telnyx_tn = webhook["data"]["payload"]["to"]

    cust_num, created = get_or_create_cust(from_tn)
    L.info("new customer?: %s", created)

    text = "{}. {}".format(cust_num.mux_prefix, webhook["data"]["payload"]["text"])

    L.info("message to team: '%s [...]' (%d chars)", text, len(text))

    if not cust_num.teammate:
        # broadcast messages to the whole team until someone picks up the thread
        # FIXME should stagger this, but then will need task handling/Celery?

        L.info("customer not associated, broadcasting to all")
        for team_num in models.TeamNumber.objects.filter(enabled=True):
            num = team_num.number
            try:
                pn = phonenumbers.parse(num)
            except phonenumbers.NumberParseException:
                L.warning(
                    "could not parse team TN '%s', assuming sham data, skipping", num
                )
                continue
            if not phonenumbers.is_valid_number(pn):
                L.warning(
                    "could not validate team TN '%s', assuming sham data, skipping", num
                )
                continue

            L.info("sending to team member: %s", team_num.number)

            send_message(cust_num, team_num, telnyx_tn, text)
    else:
        # send to just the bound team member
        L.info("sending to associated team member: %s", cust_num.teammate.number)
        send_message(cust_num, cust_num.teammate, telnyx_tn, text)


def prefix_resolution(
    team_num: models.TeamNumber, telnyx_tn: str, text: str
) -> typing.Tuple[typing.Optional[models.CustomerNumber], typing.Optional[str]]:
    prefix_error = None
    try:
        prefix, cleaned_text = text.split(".", 1)
        if len(prefix) > 12:
            raise ValueError("probably wrong...")
    except ValueError:
        # prefix not found, return error
        prefix_error = f"no tag prefix in '{text[:12]}...'"
        L.info("teammate %s did not provide prefix in message", team_num.number)
    else:
        # try to look up prefix
        prefix = prefix.strip().lower()

        try:
            cust_num = models.CustomerNumber.objects.get(mux_prefix=prefix)
        except models.CustomerNumber.DoesNotExist:
            prefix_error = f"tag prefix '{prefix}' not found"
            L.info("teammate %s provided not-found prefix: %s", team_num.number, prefix)
        else:
            if cust_num.teammate and cust_num.teammate.number != team_num.number:
                prefix_error = f"other teammate already associated with customer"
                L.info(
                    "teammate %s tried to associate to customer already bound with %s",
                    team_num.number,
                    cust_num.teammate.number,
                )

    if prefix_error:
        telnyx.Message.create(
            from_=telnyx_tn, to=team_num.number, text=f"[error] {prefix_error}",
        )
        return None, None

    # associate customer with the team member
    # FIXME: race condition between selecting here and saving the teammate to the cust
    cust_num.teammate = team_num
    cust_num.save()

    return cust_num, cleaned_text


def team_to_customer(team_num: models.TeamNumber, webhook: typing.Dict):
    from_tn = webhook["data"]["payload"]["from"]["phone_number"]
    telnyx_tn = webhook["data"]["payload"]["to"]

    # who is the customer?
    text = webhook["data"]["payload"]["text"]
    cust_num, text = prefix_resolution(team_num, telnyx_tn, text)
    if cust_num is None:
        return

    send_message(team_num, cust_num, telnyx_tn, text.lstrip())


def handle_delivery_update(webhook):
    message_id = webhook["data"]["payload"]["id"]

    from_tn = webhook["data"]["payload"]["from"]
    to_tn = webhook["data"]["payload"]["to"][0]["phone_number"]
    status = webhook["data"]["payload"]["to"][0]["status"]

    try:
        msg = models.Message.objects.get(id=message_id)
    except models.Message.DoesNotExist:
        L.warning("message with id %s not found!", message_id)
        return

    L.info(
        "message id '%s' (%s -> %s) status update: %s",
        message_id,
        from_tn,
        to_tn,
        status,
    )
    msg.delivery_status = status
    msg.save()


subhandlers = {
    "message.received": handle_received,
    "message.sent": handle_delivery_update,
    "message.finalized": handle_delivery_update,
}

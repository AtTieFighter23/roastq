from extensions import db
from models.sack_item import SackItem
from models.queue_adjustment import QueueAdjustment

# Two roaster/peeler pairs running in sync normally complete 2 sacks every
# 5-minute cycle. One pair down (degraded) still completes 1 sack per cycle,
# just at half the rate -- it is NOT "half the time per sack" (see project
# pitch notes: this was corrected from an earlier, incorrect per-sack model).
THROUGHPUT_PER_5_MIN_CYCLE = {"normal": 2, "degraded": 1, "halted": 0}


def current_throughput_mode():
    latest = (
        QueueAdjustment.query.filter_by(type="throughput_mode")
        .order_by(QueueAdjustment.created_at.desc())
        .first()
    )
    return latest.value if latest else "normal"


def total_delay_minutes():
    """Flat minutes added by employees/managers for spills, unexpected stops, etc.
    Summed across every delay_minutes entry logged so far this session/day.
    """
    total = 0
    for adj in QueueAdjustment.query.filter_by(type="delay_minutes").all():
        try:
            total += int(adj.value)
        except (TypeError, ValueError):
            continue
    return total


def compute_public_queue():
    """Read-only snapshot for the public, no-login queue board. Never
    includes customer_name or any other personal information -- only the
    order's public display number and sack-level details.
    """
    sacks = (
        SackItem.query.filter(SackItem.sack_status != "done")
        .order_by(SackItem.queue_sequence)
        .all()
    )
    mode = current_throughput_mode()
    throughput = THROUGHPUT_PER_5_MIN_CYCLE[mode]
    delay = total_delay_minutes()

    queue = []
    for idx, sack in enumerate(sacks):
        if throughput == 0:
            eta_minutes = None  # line is halted; no ETA to give
        else:
            cycles = -(-(idx + 1) // throughput)  # ceiling division
            eta_minutes = cycles * 5 + delay

        queue.append({
            "order_display_number": sack.order.display_number,
            "sack_id": sack.id,
            "size": sack.size,
            "service": sack.service,
            "color_stage": sack.color_stage,
            "variety_1": sack.variety_1,
            "variety_2": sack.variety_2,
            "status": sack.sack_status,
            "estimated_minutes_remaining": eta_minutes,
            "note": sack.order.manager_note or None,
        })

    return {"throughput_mode": mode, "queue": queue}


def reorder_queue(moving_order_id, after_order_id, applied_by_user_id):
    """Move every not-done sack belonging to `moving_order_id` to sit
    immediately after `after_order_id`'s sacks (or to the very front if
    after_order_id is None), then re-sequence everyone else. Manager-only --
    enforced by the resource layer, not here.
    """
    sacks = (
        SackItem.query.filter(SackItem.sack_status != "done")
        .order_by(SackItem.queue_sequence)
        .all()
    )

    order_ids_in_sequence = []
    sacks_by_order = {}
    for sack in sacks:
        oid = sack.order_id
        if oid not in sacks_by_order:
            sacks_by_order[oid] = []
            order_ids_in_sequence.append(oid)
        sacks_by_order[oid].append(sack)

    if moving_order_id not in sacks_by_order:
        raise ValueError("That order has no active sacks in the queue to reorder.")

    order_ids_in_sequence.remove(moving_order_id)

    if after_order_id is None:
        new_order_sequence = [moving_order_id] + order_ids_in_sequence
    else:
        if after_order_id not in order_ids_in_sequence:
            raise ValueError("Target order was not found in the active queue.")
        insert_at = order_ids_in_sequence.index(after_order_id)
        new_order_sequence = (
            order_ids_in_sequence[: insert_at + 1] + [moving_order_id] + order_ids_in_sequence[insert_at + 1:]
        )

    position = 1
    for oid in new_order_sequence:
        for sack in sacks_by_order[oid]:
            sack.queue_sequence = position
            position += 1

    db.session.add(QueueAdjustment(
        order_id=moving_order_id,
        type="reorder",
        value=f"moved after order_id={after_order_id}",
        applied_by=applied_by_user_id,
    ))
    db.session.commit()

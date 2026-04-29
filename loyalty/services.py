from datetime import date

from django.utils import timezone

from customers.models import PurchaseRecord

from .models import LoyaltyCampaign, RewardRedemption


def month_start(value):
    return date(value.year, value.month, 1)


def add_months(value, months):
    year = value.year + ((value.month - 1 + months) // 12)
    month = ((value.month - 1 + months) % 12) + 1
    return date(year, month, 1)


def months_between(start, end):
    return (end.year - start.year) * 12 + (end.month - start.month)


def last_redemption(customer, campaign):
    return (
        RewardRedemption.objects.filter(customer=customer, campaign=campaign)
        .order_by("-redeemed_at")
        .first()
    )


def purchases_in_current_cycle(customer, campaign):
    queryset = PurchaseRecord.objects.filter(customer=customer, campaign=campaign)
    previous_redemption = last_redemption(customer, campaign)
    if previous_redemption:
        queryset = queryset.filter(created_at__gt=previous_redemption.redeemed_at)
    return queryset.order_by("-created_at")


def empty_progress(campaign=None):
    return {
        "campaign": campaign,
        "rule_type": campaign.rule_type if campaign else None,
        "purchase_count": 0,
        "required_purchases": 0,
        "remaining_purchases": 0,
        "is_eligible": False,
        "is_almost_ready": False,
        "progress_percent": 0,
        "status_label": "Sem campanha ativa" if not campaign else "Sem progresso",
        "status_detail": "Cadastre uma campanha para iniciar o acompanhamento." if not campaign else "",
    }


def purchase_count_progress(customer, campaign):
    purchase_count = purchases_in_current_cycle(customer, campaign).count()
    required = campaign.required_purchases
    remaining = max(required - purchase_count, 0)
    is_eligible = purchase_count >= required
    progress_percent = min(int((purchase_count / required) * 100), 100) if required else 0
    return {
        "campaign": campaign,
        "rule_type": campaign.rule_type,
        "purchase_count": purchase_count,
        "required_purchases": required,
        "remaining_purchases": remaining,
        "is_eligible": is_eligible,
        "is_almost_ready": remaining == 1,
        "progress_percent": progress_percent,
        "status_label": "Pronto para resgate" if is_eligible else "Em progresso",
        "status_detail": (
            "Cliente elegivel para resgate."
            if is_eligible
            else f"Faltam {remaining} compra(s) para liberar o resgate."
        ),
    }


def monthly_purchase_counts(customer, campaign):
    queryset = purchases_in_current_cycle(customer, campaign)
    counts = {}
    for purchase in queryset:
        key = month_start(timezone.localtime(purchase.created_at).date())
        counts[key] = counts.get(key, 0) + 1
    return counts


def monthly_metadata(campaign):
    return {
        "required_purchases": campaign.minimum_purchases_per_month,
        "cycle_length_months": campaign.cycle_length_months,
        "minimum_purchases_per_month": campaign.minimum_purchases_per_month,
    }


def eligible_monthly_progress(base_progress, campaign, cycle_start, cycle_end, closed_months):
    total_purchases = sum(purchases for _, purchases in closed_months[: campaign.cycle_length_months])
    base_progress.update(
        monthly_metadata(campaign)
        | {
            "purchase_count": total_purchases,
            "completed_months": campaign.cycle_length_months,
            "current_cycle_month_number": campaign.cycle_length_months,
            "current_month_purchases": campaign.minimum_purchases_per_month,
            "remaining_purchases": 0,
            "remaining_purchases_this_month": 0,
            "current_cycle_started_at": cycle_start,
            "current_cycle_deadline": cycle_end,
            "goal_met_this_month": True,
            "is_eligible": True,
            "progress_percent": 100,
            "status_label": "Pronto para resgate",
            "status_detail": "O ciclo mensal foi concluido e o premio esta liberado.",
        }
    )
    return base_progress


def monthly_consecutive_progress(customer, campaign):
    base_progress = empty_progress(campaign)
    counts_by_month = monthly_purchase_counts(customer, campaign)
    if not counts_by_month:
        base_progress.update(
            monthly_metadata(campaign)
            | {
                "completed_months": 0,
                "current_cycle_month_number": 0,
                "current_month_purchases": 0,
                "remaining_purchases_this_month": campaign.minimum_purchases_per_month,
                "current_cycle_started_at": None,
                "current_cycle_deadline": None,
                "goal_met_this_month": False,
                "status_label": "Aguardando inicio",
                "status_detail": "A primeira compra inicia o ciclo mensal consecutivo.",
            }
        )
        return base_progress

    current_month = month_start(timezone.localdate())
    last_failed_month = None
    cycle_start = None
    closed_months_before_current = []
    first_purchase_month = min(counts_by_month)
    month = first_purchase_month

    while month <= current_month:
        purchases = counts_by_month.get(month, 0)
        is_current_month = month == current_month

        if cycle_start is None:
            if purchases > 0:
                cycle_start = month
                closed_months_before_current = []
                if not is_current_month:
                    if purchases >= campaign.minimum_purchases_per_month:
                        closed_months_before_current.append((month, purchases))
                        if campaign.cycle_length_months == 1:
                            return eligible_monthly_progress(
                                base_progress,
                                campaign,
                                cycle_start,
                                cycle_start,
                                closed_months_before_current,
                            )
                    else:
                        last_failed_month = month
                        cycle_start = None
        else:
            current_cycle_month_number = months_between(cycle_start, month) + 1
            cycle_end = add_months(cycle_start, campaign.cycle_length_months - 1)
            if current_cycle_month_number > campaign.cycle_length_months:
                return eligible_monthly_progress(
                    base_progress,
                    campaign,
                    cycle_start,
                    cycle_end,
                    closed_months_before_current,
                )

            if not is_current_month:
                if purchases >= campaign.minimum_purchases_per_month:
                    closed_months_before_current.append((month, purchases))
                    if current_cycle_month_number == campaign.cycle_length_months:
                        return eligible_monthly_progress(
                            base_progress,
                            campaign,
                            cycle_start,
                            cycle_end,
                            closed_months_before_current,
                        )
                else:
                    last_failed_month = month
                    cycle_start = None
                    closed_months_before_current = []

        month = add_months(month, 1)

    if cycle_start is None:
        base_progress.update(
            monthly_metadata(campaign)
            | {
                "completed_months": 0,
                "current_cycle_month_number": 0,
                "current_month_purchases": 0,
                "remaining_purchases_this_month": campaign.minimum_purchases_per_month,
                "current_cycle_started_at": None,
                "current_cycle_deadline": None,
                "goal_met_this_month": False,
                "last_failed_month": last_failed_month,
                "status_label": "Ciclo reiniciado",
                "status_detail": "O ultimo ciclo foi perdido por um mes sem meta atingida.",
            }
        )
        return base_progress

    cycle_end = add_months(cycle_start, campaign.cycle_length_months - 1)
    current_cycle_month_number = months_between(cycle_start, current_month) + 1
    current_month_purchases = counts_by_month.get(current_month, 0)
    completed_months = len(closed_months_before_current)
    total_purchases = sum(purchases for _, purchases in closed_months_before_current) + current_month_purchases
    goal_met_this_month = current_month_purchases >= campaign.minimum_purchases_per_month
    remaining_this_month = max(campaign.minimum_purchases_per_month - current_month_purchases, 0)
    month_progress = min(current_month_purchases / campaign.minimum_purchases_per_month, 1)
    progress_percent = int(((completed_months + month_progress) / campaign.cycle_length_months) * 100)

    if current_cycle_month_number == campaign.cycle_length_months and goal_met_this_month:
        status_label = "Aguardando fechamento do mes"
        status_detail = "A meta do ultimo mes foi atingida. O premio libera no fechamento deste mes."
    elif goal_met_this_month:
        status_label = "Mes atual concluido"
        status_detail = "A meta deste mes foi atingida. Agora e preciso manter a sequencia no proximo mes."
    else:
        status_label = "Em progresso"
        status_detail = f"Faltam {remaining_this_month} compra(s) para fechar o mes atual."

    base_progress.update(
        monthly_metadata(campaign)
        | {
            "purchase_count": total_purchases,
            "remaining_purchases": remaining_this_month,
            "completed_months": completed_months,
            "current_cycle_month_number": current_cycle_month_number,
            "current_month_purchases": current_month_purchases,
            "remaining_purchases_this_month": remaining_this_month,
            "current_cycle_started_at": cycle_start,
            "current_cycle_deadline": cycle_end,
            "goal_met_this_month": goal_met_this_month,
            "is_almost_ready": (
                current_cycle_month_number == campaign.cycle_length_months and remaining_this_month == 1
            ),
            "progress_percent": min(progress_percent, 99),
            "status_label": status_label,
            "status_detail": status_detail,
        }
    )
    return base_progress


def customer_progress(customer, campaign=None):
    campaign = campaign or LoyaltyCampaign.get_active()
    if not campaign:
        return empty_progress()

    if campaign.rule_type == LoyaltyCampaign.RULE_TYPE_MONTHLY_CONSECUTIVE:
        return monthly_consecutive_progress(customer, campaign)
    return purchase_count_progress(customer, campaign)

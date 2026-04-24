from .flow import build_panel_flow


def panel_flow(request):
    if not request.user.is_authenticated:
        return {"panel_flow": None}
    return {"panel_flow": build_panel_flow()}

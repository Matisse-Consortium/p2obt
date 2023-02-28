from typing import List

import p2api


# TODO: Think of way to immediately populate the templates and avoid unnecessary overhead
def _add_templates(p2_connection: p2api,
                   ob_id: int, templates: List[str]):
    """Adds templates to an OB

    Parameters
    ----------
    p2_connection: p2api
    ob_id: int
    templates: List[str]
    """
    for template in templates:
        content, id = p2api.createTemplate(ob_id, template)
    return

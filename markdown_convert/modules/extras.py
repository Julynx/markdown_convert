"""
Extras are defined as helper functions called by
render_extra_features from transform.py
"""


def create_checkbox(soup, match):
    """
    Render a tag for a checkbox.

    Args:
        soup: HTML beautifulsoup
        match: Element identified as a checkbox
    Returns:
        tag: Beautifulsoup tag representing the checkbox
    """
    tag = soup.new_tag("input", type="checkbox")
    if "[x]" in match.group("checkbox"):
        tag["checked"] = ""
    return tag


def create_highlight(soup, match):
    """
    Render a tag for a highlight.

    Args:
        soup: HTML beautifulsoup
        match: Element identified as a highlight
    Returns:
        tag: Beautifulsoup tag representing the highlight
    """
    tag = soup.new_tag("span", attrs={"class": "highlight"})
    tag.string = match.group("hl_content")
    return tag


def create_custom_span(soup, match):
    """
    Render a tag for a custom span.

    Args:
        soup: HTML beautifulsoup
        match: Element identified as a custom span
    Returns:
        tag: Beautifulsoup tag representing the custom span
    """
    tag = soup.new_tag("span", attrs={"class": match.group("cls")})
    tag.string = match.group("sp_content")
    return tag


def create_toc(soup, match):
    """
    Render a tag for a table of contents

    Args:
        soup: HTML beautifulsoup
        match: Element identified as a table of contents
    Returns:
        tag: Beautifulsoup tag representing the table of contents
    """
    max_level = match.group("depth")
    max_level = 3 if max_level is None else int(max_level)

    headers = [
        header
        for header in soup.find_all([f"h{index}" for index in range(1, max_level + 1)])
        if header.get("id")
    ]
    if not headers:
        return ""

    tag = soup.new_tag("ul", attrs={"class": "toc"})
    active_list = {0: tag}
    last_list_element = {}

    for header in headers:
        level = int(header.name[1])

        if level not in active_list:
            parent_lvl = max(key for key in active_list if key < level)
            if last_list_element.get(parent_lvl):
                sub_list = soup.new_tag("ul")
                last_list_element[parent_lvl].append(sub_list)
                active_list[level] = sub_list
            else:
                active_list[level] = active_list[parent_lvl]

        active_list = {key: value for key, value in active_list.items() if key <= level}

        list_item = soup.new_tag("li")
        link = soup.new_tag("a", href=f"#{header['id']}")
        link.string = header.get_text(strip=True)
        list_item.append(link)

        active_list[level].append(list_item)
        last_list_element[level] = list_item

    return tag

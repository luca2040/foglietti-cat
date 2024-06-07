from typing import List

from cat.looking_glass.cheshire_cat import CheshireCat


def names_from_metadata(cat: CheshireCat) -> List[str]:
    """Use this function to get all the medicine names from the metadata in the vector database"""

    points = cat.memory.vectors.collections["declarative"].get_all_points()
    name_list = []

    # Record -> id; payload={page_content; metadata}; vector

    for point in points:
        metadata_name = point.payload["metadata"]["source"]

        if metadata_name not in name_list:
            name_list.append(metadata_name)

    return name_list

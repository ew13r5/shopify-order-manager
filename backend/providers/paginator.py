import logging
from typing import Any, Dict, Generator, List

logger = logging.getLogger(__name__)


def paginate_graphql(client, query_template: str, variables: Dict = None, page_size: int = 250) -> Generator:
    cursor = None
    total_pages = 0
    total_nodes = 0

    while True:
        vars_with_cursor = {**(variables or {}), "first": page_size}
        if cursor:
            vars_with_cursor["cursor"] = cursor

        response = client.execute(query_template, vars_with_cursor)
        data = response.get("data", {})

        for key, value in data.items():
            if isinstance(value, dict) and "edges" in value:
                edges = value["edges"]
                page_info = value.get("pageInfo", {})

                for edge in edges:
                    yield edge.get("node", edge)
                    total_nodes += 1

                total_pages += 1
                if page_info.get("hasNextPage"):
                    cursor = page_info.get("endCursor")
                else:
                    logger.info("Paginated %d pages, %d nodes", total_pages, total_nodes)
                    return
                break
        else:
            return

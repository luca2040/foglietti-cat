from typing import List
from cat.looking_glass.cheshire_cat import CheshireCat

import hashlib


class optimized_embedder:
    def init(self, cat: CheshireCat) -> None:
        self.cat = cat
        self.stored_points = {}
        self.last_filename = None

    def embed_table(self, query: str, filename: str) -> List[float]:
        query_hash = hashlib.sha256(query.encode("UTF-8")).hexdigest()

        if filename != self.last_filename:
            self.last_filename = filename
            self.stored_points = {}

        if query_hash not in self.stored_points.keys():
            query_embed = self.cat.embedder.embed_documents([query])[0]
            self.stored_points.update({query_hash: query_embed})

        return self.stored_points[query_hash]


cat_embed: optimized_embedder = optimized_embedder()

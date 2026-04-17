from __future__ import annotations

from bson import ObjectId

class ProductService:
    def __init__(self, db):
        self.collection = db['products']

    async def create(self, payload: dict) -> dict:
        document = dict(payload)
        result = await self.collection.insert_one(document)
        document['_id'] = str(result.inserted_id)
        return document

    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({})
        items: list[dict] = []
        async for doc in cursor:
            doc['_id'] = str(doc['_id'])
            items.append(doc)
        return items

    async def get_one(self, item_id: str) -> dict | None:
        doc = await self.collection.find_one({'_id': ObjectId(item_id)})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc

    async def update(self, item_id: str, payload: dict) -> dict | None:
        update_data = {k: v for k, v in payload.items() if v is not None}
        await self.collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data},
        )
        return await self.get_one(item_id)

    async def delete(self, item_id: str) -> bool:
        result = await self.collection.delete_one({'_id': ObjectId(item_id)})
        return result.deleted_count > 0

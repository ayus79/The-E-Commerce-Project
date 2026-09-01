import asyncio
import os
from pymongo import (
    ASCENDING,
    DESCENDING,
    HASHED,
    TEXT,
    AsyncMongoClient,
    MongoClient,
    ReturnDocument,
)
from pymongo.results import UpdateResult


class MongoModel:
    _client = None
    _client_loop = None

    def __init__(self, database_name: str = os.getenv("MASTER_DB_NAME")):
        self.database_name = database_name
        MongoModel._ensure_client()

    @classmethod
    def _ensure_client(cls) -> AsyncMongoClient:
        """
        Return a client bound to the currently running event loop, recreating it
        if the cached client was bound to a different (or closed) loop.

        AsyncMongoClient binds to whichever event loop issues its first operation
        and raises RuntimeError if later used from a different one, so the loop
        affinity is tracked here rather than queried from the client itself.
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if cls._client is not None and current_loop is not None:
            if cls._client_loop is not None and cls._client_loop.is_closed():
                cls._client = None
            elif cls._client_loop is not None and cls._client_loop != current_loop:
                cls._client = None

        if cls._client is None:
            # Non-blocking I/O, improving FastAPI performance
            cls._client = AsyncMongoClient(
                os.getenv("MONGO_CONNECTION"),
                maxPoolSize=50,  # Limits the maximum number of concurrent connections to MongoDB
                retryWrites=False,
            )
            cls._client_loop = current_loop

        return cls._client

    async def create_dynamic_db(self, new_db_name: str) -> dict:
        """Creates a new database dynamically if it does not exist."""
        client = MongoModel._ensure_client()
        # this insures no duplication of database
        db_list = await client.list_database_names()
        if new_db_name in db_list:
            return {
                "status": False,
                "db_name": new_db_name,
                "message": "Database already exists.",
            }

        new_db = client[new_db_name]
        await new_db.create_collection("test_collection")
        return {
            "status": True,
            "db_name": new_db_name,
            "message": "Database created successfully.",
        }

    async def disconnect(self):
        if MongoModel._client:
            await MongoModel._client.close()
            MongoModel._client = None
            MongoModel._client_loop = None

    async def collection_exists(self, collection_name: str) -> bool:
        """Check whether a collection exists in the current database."""
        client = MongoModel._ensure_client()
        db = client[self.database_name]
        return collection_name in await db.list_collection_names()

    async def create_collection(self, collection_name: str) -> bool:
        """
        Create a collection if it does not exist.
        Returns True if created, False if already existed.
        """
        client = MongoModel._ensure_client()
        db = client[self.database_name]
        if collection_name in await db.list_collection_names():
            return False

        await db.create_collection(collection_name)
        return True

    async def get_collection(self, collection_name) -> object:
        """
        Get a PyMongo async collection object from the MongoDB database.

        :param collection_name: The name of the collection to retrieve.
        :return: A PyMongo async collection object.
        """
        client = MongoModel._ensure_client()
        return client[self.database_name][collection_name]

    async def execute_count(self, collection_name: str, filter: dict = None) -> int:
        """
        Count the number of documents in a collection that match the given filter.

        :param collection_name: The name of the collection to retrieve.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents that match the filter.
        """
        collection = await self.get_collection(collection_name)
        return await collection.count_documents(filter or {})

    async def execute_insert_one_filter(
        self, collection_name: str, filter: dict, data: dict
    ) -> str:
        """
        Insert a single document into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: The document to insert, as a dictionary.
        :param index_name: The name of the index to create if it doesn't exist.
        :return: The _id of the updated document as a string, or None if no document matched.
        """
        collection = await self.get_collection(collection_name)

        # Update and return the document in one call
        updated_doc = await collection.find_one_and_update(
            filter,
            {"$set": data},
            return_document=ReturnDocument.AFTER,  # Return the document **after** the update
            projection={"_id": 1},  # Only fetch _id for efficiency
        )

        if updated_doc:
            return str(updated_doc["_id"])

        return None

    async def execute_insert_one(self, collection_name: str, data: dict) -> str:
        """
        Insert a single document into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: The document to insert, as a dictionary.
        :param index_name: The name of the index to create if it doesn't exist.
        :return: The ID of the inserted document as a string.
        """
        collection = await self.get_collection(collection_name)
        # Insert the document
        result = await collection.insert_one(data)
        # Return the inserted ID as a string
        return str(result.inserted_id)

    async def execute_insert_many(self, collection_name: str, data: list) -> list:
        """
        Insert multiple documents into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: A list of documents to insert, as dictionaries.
        :return: A list of IDs of the inserted documents as strings.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.insert_many(data)
        # Return the inserted IDs as a list of strings
        return [str(id) for id in result.inserted_ids]

    async def execute_update_one(
        self,
        collection_name: str,
        filter: dict,
        data: dict,
        upsert: bool = False,
        array_filters: list = None,
    ) -> UpdateResult:
        """
        Update a single document in the given collection.

        :param collection_name: The name of the collection to update.
        :param filter: A dictionary specifying the query filter to match a document.
        :param data: A dictionary of MongoDB update operators to apply.
        :param upsert: If True, create a new document if no documents match the filter.
        :param array_filters: Optional list of filters to match elements inside arrays.
        :return: An UpdateResult object, which provides:
            - matched_count: Number of documents that matched the filter.
            - modified_count: Number of documents that were actually updated.
            - upserted_id: The _id of the inserted document if an upsert occurred, else None.
            - acknowledged: Whether the operation was acknowledged by the server.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.update_one(
            filter, data, upsert, array_filters=array_filters
        )
        return result

    async def execute_update_many(
        self,
        collection_name: str,
        filter: dict,
        data: dict,
        upsert: bool = False,
        array_filters: list = None,
    ) -> int:
        """
        Update multiple documents in the given collection.

        :param collection_name: The name of the collection to update.
        :param filter: A dictionary of MongoDB filter operators.
        :param data: A dictionary of MongoDB update operators.
        :param upsert: If True, the update will create a new document if the filter doesn't
            match any existing document.
        :param array_filters: Optional list of filters to match array elements.
        :return: The number of documents modified.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.update_many(
            filter, data, upsert=upsert, array_filters=array_filters
        )
        return result.modified_count

    async def execute_select_one(
        self, collection_name: str, filter: dict, projection: dict = None
    ) -> dict:
        """
        Retrieve a single document from the given collection.

        :param collection_name: The name of the collection to retrieve from.
        :param filter: A dictionary of MongoDB filter operators.
        :param projection: Optional projection dictionary to specify fields to include/exclude.
        :return: The retrieved document as a dictionary, or None if no document matches the filter.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.find_one(filter, projection or {})
        return result

    async def execute_select_all(
        self,
        collection_name: str,
        start_limit: int = 1,
        limit: int = None,
        filter: dict = None,
        sorted_field: str = "created_at",
        order: int = -1,
        projection: dict = None,  # _id: 0
        hint: dict = None,
    ) -> list:
        """
        Retrieve a list of documents from the given collection.

        :param collection_name: The name of the collection to retrieve from.
        :param start_limit: The number of documents to skip.
        :param limit: The maximum number of documents to return.
        :param filter: A dictionary of MongoDB filter operators.
        :param sorted_field: The field to sort the results by.
        :param order: The sorting order (1 is ascending, -1 is descending).
        :param hint: Optional index hint dict, e.g. {"field": 1}. Forces the
                     query planner to use the specified index instead of its
                     default choice.
        :return: A list of documents as dictionaries.
        """
        collection = await self.get_collection(collection_name)
        result = collection.find(filter or {}, projection or {}).sort(
            sorted_field, order
        )
        if hint:
            result = result.hint(hint)
        if limit:
            # Return the list of documents, skipping the given number of documents and
            # limiting to the given number of documents
            result = result.skip(start_limit).limit(limit)
        return await result.to_list(length=None)

    async def execute_select_all_with_pipeline(
        self,
        collection_name: str,
        start_limit: int = 1,
        limit: int = None,
        filter: dict = None,
        sorted_field: str = "created_at",
        order: int = -1,
        projection: list = None,
    ) -> list:
        collection = await self.get_collection(collection_name)
        pipeline = [{"$match": filter or {}}, {"$sort": {sorted_field: order}}]

        if limit:
            pipeline.append({"$skip": start_limit})
            pipeline.append({"$limit": limit})

        pipeline.append({"$addFields": {"_id": {"$toString": "$_id"}}})

        if projection:
            pipeline.append({"$unset": projection})

        cursor = await collection.aggregate(pipeline)
        documents = await cursor.to_list(length=None)
        return documents

    async def find_one_and_update(
        self,
        collection_name: str,
        query: dict,
        update: dict,
        upsert: bool = False,
        projection: dict = None,
        return_document: ReturnDocument = ReturnDocument.AFTER,
    ) -> dict:
        """
        Find a single document and update it, returning the document.

        :param collection_name: The name of the collection.
        :param query: A dictionary specifying the query filter.
        :param update: A dictionary of MongoDB update operators (e.g., {"$set": {...}}).
        :param upsert: If True, create a new document if no match found.
        :param projection: Optional fields to include/exclude.
        :param return_document: Return BEFORE or AFTER the update (default: AFTER).
        :return: The found/updated document, or None if not found.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.find_one_and_update(
            query,
            update,
            return_document=return_document,
            projection=projection,
            upsert=upsert,
        )
        return result

    async def execute_delete_one(self, collection_name: str, filter: dict) -> int:
        """
        Delete a single document from the given collection.

        :param collection_name: The name of the collection to delete from.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents deleted.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.delete_one(filter)
        return result.deleted_count

    async def execute_delete_many(self, collection_name: str, filter: dict = None):
        """
        Delete multiple documents from the given collection.

        :param collection_name: The name of the collection to delete from.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents deleted.
        """
        collection = await self.get_collection(collection_name)
        result = await collection.delete_many(filter or {})
        return result.deleted_count

    async def apply_aggregation(
        self, collection_name: str, pipeline: list, hint: dict = None
    ):
        """
        Applies an aggregation pipeline to the collection.

        :param collection_name: The name of the collection to apply the pipeline to.
        :param pipeline: A list of MongoDB aggregation pipeline stages.
        :param hint: Optional index hint dict passed to aggregate(), e.g. {"field": 1}.
                     Forces the query planner to use the specified index for the
                     first $match stage instead of its default choice.
        :return: The result of the aggregation pipeline as a list of documents.
        """
        collection = await self.get_collection(collection_name)

        kwargs = {}
        if hint:
            kwargs["hint"] = hint

        result = await collection.aggregate(pipeline, **kwargs)
        return [document async for document in result]

    async def execute_bulk_write(self, collection_name: str, operations: list):
        """
        Execute a bulk write operation to update multiple documents in a collection.

        :param collection_name: The name of the collection (table) to perform the bulk write on.
        :param operations: A list of UpdateOne, UpdateMany, or other bulk write operations.
        :return: The result of the bulk write operation.
        """
        # Retrieve the collection object from the database
        collection = await self.get_collection(collection_name)
        try:
            # Execute the bulk write operation and return the result
            return await collection.bulk_write(operations)
        except Exception as error:
            print(f"Bulk write error: {error}")

    async def create_index(
        self,
        collection_name: str,
        field: str,
        index_type: str = "asc",
        unique: bool = False,
        sparse: bool = False,
        background: bool = True,
        index_name: str = None,
    ) -> str:
        """
        Create an index dynamically on a given collection.

        Args:
            collection_name (str): The name of the collection.
            field (str): Field name to index.
            index_type (str): Type of index: "asc", "desc", "text", "hashed".
            unique (bool): Whether the index should enforce unique values.
            sparse (bool): Whether the index should only include documents with the indexed field.
            index_name (str): Optional name for the index.

        Returns:
            str: The name of the created index.

        Note:
            asc: (A → Z, smallest → largest, oldest → newest)
            desc: (Z → A, largest → smallest, newest → oldest)
        """
        collection = await self.get_collection(collection_name)

        type_map = {
            "asc": ASCENDING,
            "desc": DESCENDING,
            "text": TEXT,
            "hashed": HASHED,
        }
        if index_type not in type_map:
            raise ValueError(f"Unsupported index type: {index_type}")

        # Prepare index fields
        index_fields = [(field, type_map[index_type])]

        # Create the index
        existing_indexes = await collection.index_information()
        if not index_name:
            index_name = f"{field}_{index_type}_idx"

        if index_name not in existing_indexes:
            index_name = await collection.create_index(
                index_fields,
                unique=unique,
                sparse=sparse,
                background=background,
                name=index_name,
            )

        return index_name

    async def create_compound_index(
        self,
        collection_name: str,
        fields: list,
        index_name: str,
        background: bool = True,
    ) -> str:
        """
        Create a compound index on multiple fields.

        Args:
            collection_name (str): The name of the collection.
            fields (list): List of (field, direction) tuples, e.g.
                           [("is_deleted", "asc"), ("status", "asc"), ("created_at", "desc")]
            index_name (str): Name for the index.

        Returns:
            str: The name of the created index.
        """
        type_map = {
            "asc": ASCENDING,
            "desc": DESCENDING,
            "text": TEXT,
            "hashed": HASHED,
        }
        collection = await self.get_collection(collection_name)
        existing_indexes = await collection.index_information()
        if index_name not in existing_indexes:
            index_fields = [(f, type_map[o]) for f, o in fields]
            index_name = await collection.create_index(
                index_fields,
                background=background,
                name=index_name,
            )
        return index_name

    async def list_indexes(self, collection_name: str) -> list:
        """
        List all indexes of a collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            list: A list of index information.
        """
        collection = await self.get_collection(collection_name)
        indexes = []

        async for idx in await collection.list_indexes():
            fields = [(field, order) for field, order in idx["key"].items()]
            indexes.append(
                {
                    "index_name": idx.get("name"),
                    "fields": fields,
                    "unique": idx.get("unique", False),
                    "sparse": idx.get("sparse", False),
                    "background": idx.get("background", False),
                }
            )

        return indexes

    async def drop_index(self, collection_name: str, index_name: str) -> None:
        """
        Drop a specific index by name.

        Args:
            collection_name (str): The name of the collection.
            index_name (str): The name of the index to drop.
        """
        collection = await self.get_collection(collection_name)

        existing_indexes = await collection.index_information()
        if index_name not in existing_indexes:
            return {"status": False, "message": f"Index {index_name} does not exist."}

        await collection.drop_index(index_name)
        return {"status": True, "message": f"Index {index_name} dropped successfully."}

    async def drop_all_indexes(self, collection_name: str) -> None:
        """
        Drop all indexes of a collection.

        Args:
            collection_name (str): The name of the collection.
        """
        collection = await self.get_collection(collection_name)
        await collection.drop_indexes()


class SyncMongoModel:
    _client = None

    def __init__(self, database_name: str = os.getenv("MASTER_DB_NAME")):
        self.database_name = database_name

        if SyncMongoModel._client is None:
            SyncMongoModel._client = MongoClient(
                os.getenv("MONGO_CONNECTION"),
                maxPoolSize=50,  # Limits the maximum number of concurrent connections to MongoDB
                retryWrites=False,
            )

    def create_dynamic_db(self, new_db_name: str) -> dict:
        """Creates a new database dynamically if it does not exist."""
        # this insures no duplication of database
        db_list = SyncMongoModel._client.list_database_names()
        if new_db_name in db_list:
            return {
                "status": False,
                "db_name": new_db_name,
                "message": "Database already exists.",
            }

        new_db = SyncMongoModel._client[new_db_name]
        new_db.create_collection("test_collection")
        return {
            "status": True,
            "db_name": new_db_name,
            "message": "Database created successfully.",
        }

    def disconnect(self):
        if SyncMongoModel._client:
            SyncMongoModel._client.close()
            SyncMongoModel._client = None

    def collection_exists(self, collection_name: str) -> bool:
        """Check whether a collection exists in the current database."""
        db = SyncMongoModel._client[self.database_name]
        return collection_name in db.list_collection_names()

    def create_collection(self, collection_name: str) -> bool:
        """
        Create a collection if it does not exist.
        Returns True if created, False if already existed.
        """
        db = SyncMongoModel._client[self.database_name]
        if collection_name in db.list_collection_names():
            return False

        db.create_collection(collection_name)
        return True

    def get_collection(self, collection_name) -> object:
        """
        Get a PyMongo collection object from the MongoDB database.

        :param collection_name: The name of the collection to retrieve.
        :return: A PyMongo collection object.
        """
        return SyncMongoModel._client[self.database_name][collection_name]

    def execute_count(self, collection_name: str, filter: dict = None) -> int:
        """
        Count the number of documents in a collection that match the given filter.

        :param collection_name: The name of the collection to retrieve.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents that match the filter.
        """
        collection = self.get_collection(collection_name)
        return collection.count_documents(filter or {})

    def execute_insert_one_filter(
        self, collection_name: str, filter: dict, data: dict
    ) -> str:
        """
        Insert a single document into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: The document to insert, as a dictionary.
        :param index_name: The name of the index to create if it doesn't exist.
        :return: The _id of the updated document as a string, or None if no document matched.
        """
        collection = self.get_collection(collection_name)

        # Update and return the document in one call
        updated_doc = collection.find_one_and_update(
            filter,
            {"$set": data},
            return_document=ReturnDocument.AFTER,  # Return the document **after** the update
            projection={"_id": 1},  # Only fetch _id for efficiency
        )

        if updated_doc:
            return str(updated_doc["_id"])

        return None

    def execute_insert_one(self, collection_name: str, data: dict) -> str:
        """
        Insert a single document into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: The document to insert, as a dictionary.
        :param index_name: The name of the index to create if it doesn't exist.
        :return: The ID of the inserted document as a string.
        """
        collection = self.get_collection(collection_name)
        # Insert the document
        result = collection.insert_one(data)
        # Return the inserted ID as a string
        return str(result.inserted_id)

    def execute_insert_many(self, collection_name: str, data: list) -> list:
        """
        Insert multiple documents into the given collection.

        :param collection_name: The name of the collection to insert into.
        :param data: A list of documents to insert, as dictionaries.
        :return: A list of IDs of the inserted documents as strings.
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_many(data)
        # Return the inserted IDs as a list of strings
        return [str(id) for id in result.inserted_ids]

    def execute_update_one(
        self,
        collection_name: str,
        filter: dict,
        data: dict,
        upsert: bool = False,
        array_filters: list = None,
    ) -> UpdateResult:
        """
        Update a single document in the given collection.

        :param collection_name: The name of the collection to update.
        :param filter: A dictionary specifying the query filter to match a document.
        :param data: A dictionary of MongoDB update operators to apply.
        :param upsert: If True, create a new document if no documents match the filter.
        :param array_filters: Optional list of filters to match elements inside arrays.
        :return: An UpdateResult object, which provides:
            - matched_count: Number of documents that matched the filter.
            - modified_count: Number of documents that were actually updated.
            - upserted_id: The _id of the inserted document if an upsert occurred, else None.
            - acknowledged: Whether the operation was acknowledged by the server.
        """
        collection = self.get_collection(collection_name)
        result = collection.update_one(
            filter, data, upsert, array_filters=array_filters
        )
        return result

    def execute_update_many(
        self,
        collection_name: str,
        filter: dict,
        data: dict,
        upsert: bool = False,
        array_filters: list = None,
    ) -> int:
        """
        Update multiple documents in the given collection.

        :param collection_name: The name of the collection to update.
        :param filter: A dictionary of MongoDB filter operators.
        :param data: A dictionary of MongoDB update operators.
        :param upsert: If True, the update will create a new document if the filter doesn't
            match any existing document.
        :param array_filters: Optional list of filters to match array elements.
        :return: The number of documents modified.
        """
        collection = self.get_collection(collection_name)
        result = collection.update_many(
            filter, data, upsert=upsert, array_filters=array_filters
        )
        return result.modified_count

    def execute_select_one(
        self, collection_name: str, filter: dict, projection: dict = None
    ) -> dict:
        """
        Retrieve a single document from the given collection.

        :param collection_name: The name of the collection to retrieve from.
        :param filter: A dictionary of MongoDB filter operators.
        :param projection: Optional projection dictionary to specify fields to include/exclude.
        :return: The retrieved document as a dictionary, or None if no document matches the filter.
        """
        collection = self.get_collection(collection_name)
        result = collection.find_one(filter, projection or {})
        return result

    def execute_select_all(
        self,
        collection_name: str,
        start_limit: int = 1,
        limit: int = None,
        filter: dict = None,
        sorted_field: str = "created_at",
        order: int = -1,
        projection: dict = None,  # _id: 0
    ) -> list:
        """
        Retrieve a list of documents from the given collection.

        :param collection_name: The name of the collection to retrieve from.
        :param start_limit: The number of documents to skip.
        :param limit: The maximum number of documents to return.
        :param filter: A dictionary of MongoDB filter operators.
        :param sorted_field: The field to sort the results by.
        :param order: The sorting order (1 is ascending, -1 is descending).
        :return: A list of documents as dictionaries.
        """
        collection = self.get_collection(collection_name)
        result = collection.find(filter or {}, projection or {}).sort(
            sorted_field, order
        )
        if limit:
            # Return the list of documents, skipping the given number of documents and
            # limiting to the given number of documents
            result = result.skip(start_limit).limit(limit)
        return list(result)

    def execute_select_all_with_pipeline(
        self,
        collection_name: str,
        start_limit: int = 1,
        limit: int = None,
        filter: dict = None,
        sorted_field: str = "created_at",
        order: int = -1,
        projection: list = None,
    ) -> list:
        collection = self.get_collection(collection_name)
        pipeline = [{"$match": filter or {}}, {"$sort": {sorted_field: order}}]

        if limit:
            pipeline.append({"$skip": start_limit})
            pipeline.append({"$limit": limit})

        pipeline.append({"$addFields": {"_id": {"$toString": "$_id"}}})

        if projection:
            pipeline.append({"$unset": projection})

        documents = list(collection.aggregate(pipeline))
        return documents

    def find_one_and_update(
        self,
        collection_name: str,
        query: dict,
        update: dict,
        upsert: bool = False,
        projection: dict = None,
        return_document: ReturnDocument = ReturnDocument.AFTER,
    ) -> dict:
        """
        Find a single document and update it, returning the document.

        :param collection_name: The name of the collection.
        :param query: A dictionary specifying the query filter.
        :param update: A dictionary of MongoDB update operators (e.g., {"$set": {...}}).
        :param upsert: If True, create a new document if no match found.
        :param projection: Optional fields to include/exclude.
        :param return_document: Return BEFORE or AFTER the update (default: AFTER).
        :return: The found/updated document, or None if not found.
        """
        collection = self.get_collection(collection_name)
        result = collection.find_one_and_update(
            query,
            update,
            return_document=return_document,
            projection=projection,
            upsert=upsert,
        )
        return result

    def execute_delete_one(self, collection_name: str, filter: dict) -> int:
        """
        Delete a single document from the given collection.

        :param collection_name: The name of the collection to delete from.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents deleted.
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_one(filter)
        return result.deleted_count

    def execute_delete_many(self, collection_name: str, filter: dict = None):
        """
        Delete multiple documents from the given collection.

        :param collection_name: The name of the collection to delete from.
        :param filter: A dictionary of MongoDB filter operators.
        :return: The number of documents deleted.
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_many(filter or {})
        return result.deleted_count

    def apply_aggregation(self, collection_name: str, pipeline: list):
        """
        Applies an aggregation pipeline to the collection.

        :param collection_name: The name of the collection to apply the pipeline to.
        :param pipeline: A list of MongoDB aggregation pipeline stages.
        :return: The result of the aggregation pipeline as a list of documents.
        """
        collection = self.get_collection(collection_name)

        # Apply the aggregation pipeline to the collection
        result = collection.aggregate(pipeline)

        # Convert the result cursor to a list
        return list(result)

    def execute_bulk_write(self, collection_name: str, operations: list):
        """
        Execute a bulk write operation to update multiple documents in a collection.

        :param collection_name: The name of the collection (table) to perform the bulk write on.
        :param operations: A list of UpdateOne, UpdateMany, or other bulk write operations.
        :return: The result of the bulk write operation.
        """
        # Retrieve the collection object from the database
        collection = self.get_collection(collection_name)
        try:
            # Execute the bulk write operation and return the result
            return collection.bulk_write(operations)
        except Exception as error:
            print(f"Bulk write error: {error}")

    def create_index(
        self,
        collection_name: str,
        field: str,
        index_type: str = "asc",
        unique: bool = False,
        sparse: bool = False,
        background: bool = True,
        index_name: str = None,
    ) -> str:
        """
        Create an index dynamically on a given collection.

        Args:
            collection_name (str): The name of the collection.
            field (str): Field name to index.
            index_type (str): Type of index: "asc", "desc", "text", "hashed".
            unique (bool): Whether the index should enforce unique values.
            sparse (bool): Whether the index should only include documents with the indexed field.
            index_name (str): Optional name for the index.

        Returns:
            str: The name of the created index.

        Note:
            asc: (A → Z, smallest → largest, oldest → newest)
            desc: (Z → A, largest → smallest, newest → oldest)
        """
        collection = self.get_collection(collection_name)

        type_map = {
            "asc": ASCENDING,
            "desc": DESCENDING,
            "text": TEXT,
            "hashed": HASHED,
        }
        if index_type not in type_map:
            raise ValueError(f"Unsupported index type: {index_type}")

        # Prepare index fields
        index_fields = [(field, type_map[index_type])]

        # Create the index
        existing_indexes = collection.index_information()
        if not index_name:
            index_name = f"{field}_{index_type}_idx"

        if index_name not in existing_indexes:
            index_name = collection.create_index(
                index_fields,
                unique=unique,
                sparse=sparse,
                background=background,
                name=index_name,
            )

        return index_name

    def list_indexes(self, collection_name: str) -> list:
        """
        List all indexes of a collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            list: A list of index information.
        """
        collection = self.get_collection(collection_name)
        indexes = []

        for idx in collection.list_indexes():
            fields = [(field, order) for field, order in idx["key"].items()]
            indexes.append(
                {
                    "index_name": idx.get("name"),
                    "fields": fields,
                    "unique": idx.get("unique", False),
                    "sparse": idx.get("sparse", False),
                    "background": idx.get("background", False),
                }
            )

        return indexes

    def drop_index(self, collection_name: str, index_name: str) -> None:
        """
        Drop a specific index by name.

        Args:
            collection_name (str): The name of the collection.
            index_name (str): The name of the index to drop.
        """
        collection = self.get_collection(collection_name)

        existing_indexes = collection.index_information()
        if index_name not in existing_indexes:
            return {"status": False, "message": f"Index {index_name} does not exist."}

        collection.drop_index(index_name)
        return {"status": True, "message": f"Index {index_name} dropped successfully."}

    def drop_all_indexes(self, collection_name: str) -> None:
        """
        Drop all indexes of a collection.

        Args:
            collection_name (str): The name of the collection.
        """
        collection = self.get_collection(collection_name)
        collection.drop_indexes()


def get_master_db() -> MongoModel:
    """
    Get master database connection

    Returns:
        MongoModel instance connected to master database
    """
    return MongoModel(os.getenv("MASTER_DB_NAME"))


def get_tenant_db(tenant_db_name: str) -> MongoModel:
    """
    Get tenant database connection

    Args:
        tenant_db_name: Name of the tenant database

    Returns:
        MongoModel instance connected to specified tenant database
    """
    return MongoModel(tenant_db_name)

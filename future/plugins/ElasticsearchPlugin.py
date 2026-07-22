from future.plugins import Plugin
from elasticsearch import Elasticsearch, helpers


class ElasticsearchPlugin(Plugin):
    # __type__ = "database"
    
    
    """Plugin/Database class for Elasticsearch operations - provides ORM-like interface"""
    
    def __init__(self, host, username, password):
        self.es = Elasticsearch(host, basic_auth=(username, password))
        self.host = host
        self._username = username
        self._password = password
        #self.auth = ES_AUTH

    def create_index(self, index_name, mapping=None, settings=None):
        """Create a new index with optional mapping and settings"""
        try:
            payload = {}
            if mapping:
                payload["mappings"] = mapping
            if settings:
                payload["settings"] = settings
            
            result = self.es.indices.create(index=index_name, body=payload)
            return {"status": "Index created", "index": index_name, "result": result}
        except Exception as e:
            return {"error": str(e)}

    def delete_index(self, index_name):
        """Delete an index"""
        try:
            result = self.es.indices.delete(index=index_name)
            return {"status": f"Index {index_name} deleted", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def index_exists(self, index_name):
        """Check if an index exists"""
        try:
            return self.es.indices.exists(index=index_name)
        except Exception:
            return False

    def get_index_info(self, index_name=None):
        """Get information about an index or all indices"""
        try:
            if index_name:
                result = self.es.indices.get(index=index_name)
            else:
                result = self.es.cat.indices(format="json")
            return result
        except Exception as e:
            return {"error": str(e)}

    def create_alias(self, index_name, alias_name):
        """Create an alias for an index"""
        try:
            result = self.es.indices.put_alias(index=index_name, name=alias_name)
            return {"status": f"Alias {alias_name} created for index {index_name}", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def delete_alias(self, index_name, alias_name):
        """Delete an alias"""
        try:
            result = self.es.indices.delete_alias(index=index_name, name=alias_name)
            return {"status": f"Alias {alias_name} removed from index {index_name}", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def index_document(self, index_name, document, document_id=None):
        """Index a single document"""
        try:
            if document_id:
                result = self.es.index(index=index_name, id=document_id, body=document, refresh=True)
            else:
                result = self.es.index(index=index_name, body=document, refresh=True)
            
            return {"status": "Document indexed", "result": result}
        except Exception as e:
            return {"error": str(e)}

    # FIXME: this should definitely not be the way bulk is used. Why queue up a python list and then send it to the server?
    def bulk_index(self, index_name, documents, bulk_options=None):
        """Bulk index multiple documents with chunking (prevents timeouts on large payloads)"""
        try:
            # Prepare bulk request body
            #bulk_body = []
            #for doc in documents:
            #    bulk_body.append({"index": {"_index": index_name}})
            #    bulk_body.append(doc)

            #result = self.es.bulk(body=bulk_body)
            result = helpers.bulk(self.es, index=index_name, actions=documents)
            return result
        except Exception as e:
            return {"error": str(e)}

    def bulk_actions(self, actions, raise_on_error=False):
        """Bulk index/update/delete using elasticsearch.helpers.bulk action dicts."""
        try:
            success, errors = helpers.bulk(self.es, actions, raise_on_error=raise_on_error)
            error_count = len(errors) if errors else 0
            return success, error_count
        except Exception:
            return 0, 1 if raise_on_error else 0

    def scroll_document_ids(self, index_name, query=None, page_size=1000, scroll_ttl="2m"):
        """Scroll an index and return all document IDs."""
        if not self.index_exists(index_name):
            return set()

        if query is None:
            query = {"match_all": {}}

        known: set[str] = set()
        response = self.es.search(
            index=index_name,
            scroll=scroll_ttl,
            size=page_size,
            _source=False,
            query=query,
        )
        scroll_id = response.get("_scroll_id")
        hits = response.get("hits", {}).get("hits", [])
        known.update(hit["_id"] for hit in hits)

        while hits:
            response = self.es.scroll(scroll_id=scroll_id, scroll=scroll_ttl)
            scroll_id = response.get("_scroll_id")
            hits = response.get("hits", {}).get("hits", [])
            known.update(hit["_id"] for hit in hits)

        if scroll_id:
            self.es.clear_scroll(scroll_id=scroll_id)

        return known


    def search_documents(self, index_name, query, search_options=None):
        """Search documents using Elasticsearch query DSL with configurable options"""
        try:
            # Apply search options to the query
            if search_options:
                query.update(search_options)
            
            result = self.es.search(index=index_name, body=query)
            return result
        except Exception as e:
            return {"error": str(e)}

    def search(self, index_name, **kwargs):
        """Pass-through search for full Elasticsearch query DSL (including aggregations)."""
        try:
            return self.es.search(index=index_name, **kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_document(self, index_name, document_id):
        """Get a specific document by ID"""
        try:
            result = self.es.get(index=index_name, id=document_id)
            return result
        except Exception as e:
            return {"error": str(e)}

    def update_document(self, index_name, document_id, update_data):
        """Update a document"""
        try:
            result = self.es.update(index=index_name, id=document_id, body={"doc": update_data})
            return {"status": "Document updated", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def delete_document(self, index_name, document_id):
        """Delete a document"""
        try:
            result = self.es.delete(index=index_name, id=document_id)
            return {"status": f"Document {document_id} deleted", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def get_index_settings(self, index_name):
        """Get index settings"""
        try:
            result = self.es.indices.get_settings(index=index_name)
            return result
        except Exception as e:
            return {"error": str(e)}

    def update_index_settings(self, index_name, settings):
        """Update index settings"""
        try:
            result = self.es.indices.put_settings(index=index_name, body=settings)
            return {"status": "Settings updated", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def get_index_mapping(self, index_name):
        """Get index mapping"""
        try:
            result = self.es.indices.get_mapping(index=index_name)
            return result
        except Exception as e:
            return {"error": str(e)}

    def update_index_mapping(self, index_name, mapping):
        """Update index mapping"""
        try:
            result = self.es.indices.put_mapping(index=index_name, body=mapping)
            return {"status": "Mapping updated", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def reindex(self, source_index, dest_index, query=None):
        """Reindex from source to destination index"""
        try:
            if query is None:
                query = {"match_all": {}}
                
            body = {
                "source": {
                    "index": source_index,
                    "query": query
                },
                "dest": {
                    "index": dest_index
                }
            }
            
            result = self.es.reindex(body=body)
            return {"status": "Reindexing started", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def refresh_index(self, index_name):
        """Refresh an index to make recent changes visible"""
        try:
            result = self.es.indices.refresh(index=index_name)
            return {"status": f"Index {index_name} refreshed", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def flush_index(self, index_name):
        """Flush an index to disk"""
        try:
            result = self.es.indices.flush(index=index_name)
            return {"status": f"Index {index_name} flushed", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def rename_index(self, old_index_name, new_index_name, delete_old=True):
        """Rename an index by reindexing to a new name (Elasticsearch doesn't support direct renaming)"""
        try:
            # Step 1: Check if old index exists
            if not self.index_exists(old_index_name):
                return {"error": f"Source index {old_index_name} does not exist"}
            
            # Step 2: Check if new index already exists
            if self.index_exists(new_index_name):
                return {"error": f"Target index {new_index_name} already exists"}
            
            # Step 3: Get the mapping and settings from old index
            old_mapping = self.es.indices.get_mapping(index=old_index_name)
            old_settings = self.es.indices.get_settings(index=old_index_name)
            
            # Step 4: Create new index with same mapping and settings
            new_index_body = {
                "mappings": old_mapping[old_index_name]["mappings"],
                "settings": old_settings[old_index_name]["settings"]["index"]
            }
            
            # Remove settings that can't be copied
            if "creation_date" in new_index_body["settings"]:
                del new_index_body["settings"]["creation_date"]
            if "version" in new_index_body["settings"]:
                del new_index_body["settings"]["version"]
            if "uuid" in new_index_body["settings"]:
                del new_index_body["settings"]["uuid"]
            
            self.es.indices.create(index=new_index_name, body=new_index_body)

            # Step 5: Reindex all data
            reindex_body = {
                "source": {"index": old_index_name},
                "dest": {"index": new_index_name}
            }
            
            reindex_result = self.es.reindex(body=reindex_body)
            
            # Step 6: Delete old index if requested
            if delete_old:
                self.es.indices.delete(index=old_index_name)
                return {
                    "status": f"Index renamed from {old_index_name} to {new_index_name}",
                    "old_index_deleted": True,
                    "reindex_result": reindex_result
                }
            else:
                return {
                    "status": f"Index copied from {old_index_name} to {new_index_name}",
                    "old_index_deleted": False,
                    "reindex_result": reindex_result
                }
                
        except Exception as e:
            return {"error": str(e)}

    def copy_index(self, source_index_name, target_index_name):
        """Copy an index to a new name (keeps original)"""
        return self.rename_index(source_index_name, target_index_name, delete_old=False)

    def get_updatable_settings(self, index_name):
        """Get a list of index settings that can be updated"""
        try:
            # Get current settings
            current_settings = self.es.indices.get_settings(index=index_name)
            index_settings = current_settings[index_name]["settings"]["index"]
            
            # Filter out settings that cannot be updated
            updatable_settings = {}
            for key, value in index_settings.items():
                if key not in ["creation_date", "version", "uuid", "number_of_shards"]:
                    updatable_settings[key] = value
            
            return {
                "updatable_settings": updatable_settings,
                "all_settings": index_settings,
                "note": "Only updatable settings are shown above. Core settings like shards cannot be changed."
            }
        except Exception as e:
            return {"error": str(e)}

    def update_index_metadata(self, index_name, metadata_updates):
        """Update index metadata (settings that can be modified)"""
        try:
            # Validate that we're not trying to update immutable settings
            immutable_settings = ["number_of_shards", "creation_date", "version", "uuid"]
            for setting in immutable_settings:
                if setting in metadata_updates:
                    return {"error": f"Cannot update immutable setting: {setting}"}
            
            # Update the settings
            result = self.es.indices.put_settings(index=index_name, body=metadata_updates)
            return {
                "status": "Index metadata updated",
                "updated_settings": metadata_updates,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}

    def get_index_stats(self, index_name):
        """Get comprehensive index statistics"""
        try:
            stats = self.es.indices.stats(index=index_name)
            return stats
        except Exception as e:
            return {"error": str(e)}

    def force_merge_index(self, index_name, max_num_segments=1):
        """Force merge index segments for optimization"""
        try:
            result = self.es.indices.forcemerge(index=index_name, max_num_segments=max_num_segments)
            return {"status": f"Index {index_name} force merged", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def close_index(self, index_name):
        """Close an index (makes it read-only and frees up memory)"""
        try:
            result = self.es.indices.close(index=index_name)
            return {"status": f"Index {index_name} closed", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def open_index(self, index_name):
        """Open a closed index"""
        try:
            result = self.es.indices.open(index=index_name)
            return {"status": f"Index {index_name} opened", "result": result}
        except Exception as e:
            return {"error": str(e)}

    def create_api_key(self, index_name, alias="logs", elastic_user=None, elastic_pass=None, privileges=None, role_name="writer", expiration=None, metadata=None):
        """Create API key for a specific index (for SIEM use case) with configurable options"""
        try:
            # Default to configured credentials if none provided
            if elastic_user is None:
                elastic_user = self._username
            if elastic_pass is None:
                elastic_pass = self._password
            
            # Default privileges if none specified
            if privileges is None:
                privileges = ["write", "create_index", "read"]
            
            # Step 1: Create index with best compression (ZSTD in ES 8.x)
            index_body = {
                "settings": {
                    "index.codec": "best_compression"
                },
                "mappings": {
                    "_source": { "enabled": True },
                    "properties": {
                        "timestamp": { "type": "date" },
                        "level":     { "type": "keyword" },
                        "message":   { "type": "text" },
                        "user":      { "type": "keyword" },
                        "command":   { "type": "keyword" },
                        "source":    { "type": "keyword" },
                        "target":    { "type": "keyword" }
                    }
                }
            }
            
            # Use the ES client for index creation
            if not self.index_exists(index_name):
                self.es.indices.create(index=index_name, body=index_body)

            # Step 2: Assign alias
            try:
                # Prefer setting write index when creating an alias
                self.es.indices.put_alias(index=index_name, name=alias, body={"is_write_index": True})
            except Exception:
                # Fallback to simple alias if cluster/version does not support body param
                self.es.indices.put_alias(index=index_name, name=alias)

            # Step 3: Create API key - this still needs HTTP request as ES client doesn't have security API
            import requests
            api_key_payload = {
                "name": f"{index_name}-token",
                "role_descriptors": {
                    role_name: {
                        "index": [{
                            "names": [alias],
                            "privileges": privileges
                        }]
                    }
                }
            }
            
            # Add optional parameters if provided
            if expiration:
                api_key_payload["expiration"] = expiration
            if metadata:
                api_key_payload["metadata"] = metadata
            
            resp = requests.post(
                f"{self.host}/_security/api_key",
                auth=(elastic_user, elastic_pass),
                json=api_key_payload
            )
            resp.raise_for_status()
            key = resp.json()["api_key"]
            return {
                "status": "API key created",
                "index": index_name,
                "alias": alias,
                "api_key": key,
                "role_name": role_name,
                "privileges": privileges,
                "expiration": expiration,
                "metadata": metadata,
                "config": {
                    "auth.user": "token",
                    "auth.password": key
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def bulk_insert(self, index_name, docs, bulk_options=None):
        """Bulk insert documents (for SIEM use case) with configurable options"""
        try:
            # Use the ES client bulk method
            bulk_body = []
            for doc in docs:
                bulk_body.append({"index": {"_index": index_name}})
                bulk_body.append(doc)
            
            # Apply bulk options if provided
            if bulk_options:
                result = self.es.bulk(body=bulk_body, **bulk_options)  # compare to: es.bulk_actions(actions, raise_on_error=False)
            else:
                result = self.es.bulk(body=bulk_body)
                
            return {"status": f"Inserted {len(docs)} documents", "result": result}
        except Exception as e:
            return {"error": str(e)}


# Legacy methods removed (used undefined 'es')

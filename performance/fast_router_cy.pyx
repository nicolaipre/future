# cython: language_level=3
# distutils: language=c

import re
from typing import Dict, List, Optional, Tuple, Any
from cpython.bytes cimport PyBytes_Check, PyBytes_AsString
from cpython.dict cimport PyDict_New, PyDict_SetItem, PyDict_GetItem
from libc.string cimport strcmp, strncmp, strlen, strcpy
from libc.stdlib cimport malloc, free, realloc

cdef extern from "Python.h":
    object PyUnicode_FromString(const char* s)
    object PyUnicode_FromStringAndSize(const char* s, Py_ssize_t size)
    int PyUnicode_Check(object obj)
    char* PyUnicode_AsUTF8(object obj)

cdef struct TrieNode:
    char* segment
    int is_end
    int param_index
    char* param_name
    TrieNode* children
    int num_children
    void* handler

cdef class FastRouterCython:
    cdef TrieNode* root
    cdef list route_patterns
    cdef dict param_names
    
    def __init__(self):
        self.root = <TrieNode*>malloc(sizeof(TrieNode))
        self.root.segment = NULL
        self.root.is_end = 0
        self.root.param_index = -1
        self.root.param_name = NULL
        self.root.children = NULL
        self.root.num_children = 0
        self.root.handler = NULL
        self.route_patterns = []
        self.param_names = {}
    
    def __dealloc__(self):
        if self.root != NULL:
            self._free_trie(self.root)
    
    cdef void _free_trie(self, TrieNode* node):
        cdef int i
        if node.children != NULL:
            for i in range(node.num_children):
                self._free_trie(&node.children[i])
            free(node.children)
        if node.segment != NULL:
            free(node.segment)
        if node.param_name != NULL:
            free(node.param_name)
    
    def add_route(self, str path, object handler):
        """Add a route to the fast router."""
        cdef bytes path_bytes = path.encode('utf-8')
        cdef char* path_str = PyUnicode_AsUTF8(path)
        
        # Parse path into segments
        segments = self._parse_path(path)
        
        # Add to trie
        current = self.root
        cdef int param_index = 0
        
        for segment in segments:
            if segment.startswith(':'):
                # Parameter segment
                param_name = segment[1:]
                current = self._add_param_node(current, param_name.encode('utf-8'), param_index)
                param_index += 1
            else:
                # Static segment
                current = self._add_static_node(current, segment.encode('utf-8'))
        
        # Mark as end node and store handler
        current.is_end = 1
        current.handler = <void*>handler
        
        # Store parameter names for this route
        self.param_names[path] = [seg[1:] for seg in segments if seg.startswith(':')]
    
    cdef TrieNode* _add_static_node(self, TrieNode* parent, bytes segment):
        """Add a static segment node to the trie."""
        cdef int i
        cdef TrieNode* child
        
        # Check if segment already exists
        for i in range(parent.num_children):
            child = &parent.children[i]
            if child.segment != NULL and strcmp(child.segment, segment) == 0:
                return child
        
        # Add new child
        parent.num_children += 1
        parent.children = <TrieNode*>realloc(parent.children, parent.num_children * sizeof(TrieNode))
        child = &parent.children[parent.num_children - 1]
        
        # Initialize new node
        child.segment = <char*>malloc(len(segment) + 1)
        strcpy(child.segment, segment)
        child.is_end = 0
        child.param_index = -1
        child.param_name = NULL
        child.children = NULL
        child.num_children = 0
        child.handler = NULL
        
        return child
    
    cdef TrieNode* _add_param_node(self, TrieNode* parent, bytes param_name, int param_index):
        """Add a parameter node to the trie."""
        cdef TrieNode* child
        
        # Parameter nodes are always unique
        parent.num_children += 1
        parent.children = <TrieNode*>realloc(parent.children, parent.num_children * sizeof(TrieNode))
        child = &parent.children[parent.num_children - 1]
        
        # Initialize parameter node
        child.segment = NULL  # No static segment for params
        child.is_end = 0
        child.param_index = param_index
        child.param_name = <char*>malloc(len(param_name) + 1)
        strcpy(child.param_name, param_name)
        child.children = NULL
        child.num_children = 0
        child.handler = NULL
        
        return child
    
    def _parse_path(self, str path):
        """Parse path into segments."""
        segments = []
        current = ""
        
        for char in path:
            if char == '/':
                if current:
                    segments.append(current)
                    current = ""
            else:
                current += char
        
        if current:
            segments.append(current)
        
        return segments
    
    def match(self, bytes request_path):
        """Match a request path against the trie."""
        cdef list segments = self._parse_path_bytes(request_path)
        cdef dict params = {}
        cdef TrieNode* node = self._match_path(self.root, segments, params)
        
        if node != NULL and node.is_end:
            return {
                'handler': <object>node.handler,
                'params': params
            }
        return None
    
    cdef list _parse_path_bytes(self, bytes path):
        """Parse bytes path into segments."""
        segments = []
        current = b""
        
        for byte in path:
            if byte == ord(b'/'):
                if current:
                    segments.append(current)
                    current = b""
            else:
                current += bytes([byte])
        
        if current:
            segments.append(current)
        
        return segments
    
    cdef TrieNode* _match_path(self, TrieNode* node, list segments, dict params):
        """Recursively match path segments against trie."""
        cdef int i, j
        cdef TrieNode* child
        cdef bytes segment
        
        if not segments:
            return node if node.is_end else NULL
        
        segment = segments[0]
        remaining = segments[1:]
        
        # Try static segments first
        for i in range(node.num_children):
            child = &node.children[i]
            if child.segment != NULL and strcmp(child.segment, segment) == 0:
                result = self._match_path(child, remaining, params)
                if result != NULL:
                    return result
        
        # Try parameter segments
        for i in range(node.num_children):
            child = &node.children[i]
            if child.segment == NULL and child.param_name != NULL:
                # This is a parameter node
                param_name = child.param_name.decode('utf-8')
                params[param_name] = segment.decode('utf-8')
                result = self._match_path(child, remaining, params)
                if result != NULL:
                    return result
        
        return NULL

# Pure Python fallback for development
class FastRouterFallback:
    def __init__(self):
        self.routes = {}
    
    def add_route(self, path, handler):
        self.routes[path] = handler
    
    def match(self, request_path):
        path = request_path.decode('utf-8')
        if path in self.routes:
            return {
                'handler': self.routes[path]['handler'],
                'params': {}
            }
        return None 
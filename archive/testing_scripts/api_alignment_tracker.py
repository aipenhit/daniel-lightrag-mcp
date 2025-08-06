#!/usr/bin/env python3
"""
API Alignment Tracker - Systematic testing and progress tracking for LightRAG MCP tools.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daniel_lightrag_mcp.client import LightRAGClient, LightRAGError

class ToolStatus(Enum):
    WORKING = "✅ WORKING"
    BROKEN = "❌ BROKEN"
    PARTIAL = "⚠️ PARTIAL"
    BLOCKED = "🚫 BLOCKED"
    NOT_TESTED = "⏳ NOT_TESTED"

class IssueCategory(Enum):
    HTTP_CLIENT = "HTTP_CLIENT"
    REQUEST_PARAMS = "REQUEST_PARAMS"
    RESPONSE_MODEL = "RESPONSE_MODEL"
    SERVER_SIDE = "SERVER_SIDE"
    WORKING = "WORKING"

@dataclass
class ToolTest:
    name: str
    endpoint: str
    method: str
    category: str
    status: ToolStatus
    issue_category: Optional[IssueCategory]
    error_message: Optional[str]
    expected_fix: Optional[str]
    priority: str
    test_function: Optional[callable] = None

@dataclass
class TestResults:
    timestamp: str
    total_tools: int
    working_tools: int
    broken_tools: int
    success_rate: float
    phase: str
    tools: List[Dict]

class APIAlignmentTracker:
    """Tracks API alignment progress with automated testing."""
    
    def __init__(self):
        self.client = None
        self.results_file = "api_alignment_results.json"
        self.progress_file = "API_ALIGNMENT_PROGRESS.md"
        
        # Define all 22 tools with their test configurations
        self.tools = [
            # Document Management Tools
            ToolTest("insert_text", "/documents/text", "POST", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Fix request format: {text} → {title, content}", "HIGH", self._test_insert_text),
            
            ToolTest("insert_texts", "/documents/texts", "POST", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Fix request format: {texts: [...]} → [...]", "HIGH", self._test_insert_texts),
            
            ToolTest("upload_document", "/documents/upload", "POST", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Change to multipart form-data", "HIGH", self._test_upload_document),
            
            ToolTest("scan_documents", "/documents/scan", "POST", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Minor response model fix", "LOW", self._test_scan_documents),
            
            ToolTest("get_documents", "/documents", "GET", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.SERVER_SIDE, None, 
                    "Server-side validation error", "BLOCKED", self._test_get_documents),
            
            ToolTest("get_documents_paginated", "/documents/paginated", "POST", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.SERVER_SIDE, None, 
                    "Server-side validation error", "BLOCKED", self._test_get_documents_paginated),
            
            ToolTest("delete_document", "/documents/delete_document", "DELETE", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.HTTP_CLIENT, None, 
                    "Fix DELETE with JSON body", "MEDIUM", self._test_delete_document),
            
            ToolTest("clear_documents", "/documents", "DELETE", "Document Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Fix response model", "MEDIUM", self._test_clear_documents),
            
            # Query Tools
            ToolTest("query_text", "/query", "POST", "Query", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Fix response model: expects query field", "HIGH", self._test_query_text),
            
            ToolTest("query_text_stream", "/query/stream", "POST", "Query", 
                    ToolStatus.NOT_TESTED, IssueCategory.WORKING, None, 
                    "Already working", "LOW", self._test_query_text_stream),
            
            # Knowledge Graph Tools
            ToolTest("get_knowledge_graph", "/graphs", "GET", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Add required label parameter", "HIGH", self._test_get_knowledge_graph),
            
            ToolTest("get_graph_labels", "/graph/label/list", "GET", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Handle array response", "MEDIUM", self._test_get_graph_labels),
            
            ToolTest("check_entity_exists", "/graph/entity/exists", "GET", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Fix parameter name mapping", "MEDIUM", self._test_check_entity_exists),
            
            ToolTest("update_entity", "/graph/entity/edit", "POST", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Fix parameter structure", "MEDIUM", self._test_update_entity),
            
            ToolTest("update_relation", "/graph/relation/edit", "POST", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.REQUEST_PARAMS, None, 
                    "Fix parameter structure", "MEDIUM", self._test_update_relation),
            
            ToolTest("delete_entity", "/documents/delete_entity", "DELETE", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.HTTP_CLIENT, None, 
                    "Fix DELETE with JSON body", "MEDIUM", self._test_delete_entity),
            
            ToolTest("delete_relation", "/documents/delete_relation", "DELETE", "Knowledge Graph", 
                    ToolStatus.NOT_TESTED, IssueCategory.HTTP_CLIENT, None, 
                    "Fix DELETE with JSON body", "MEDIUM", self._test_delete_relation),
            
            # System Management Tools
            ToolTest("get_pipeline_status", "/documents/pipeline_status", "GET", "System Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Fix response model", "MEDIUM", self._test_get_pipeline_status),
            
            ToolTest("get_track_status", "/documents/track_status/{track_id}", "GET", "System Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Fix response model", "MEDIUM", self._test_get_track_status),
            
            ToolTest("get_document_status_counts", "/documents/status_counts", "GET", "System Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.WORKING, None, 
                    "Already working", "LOW", self._test_get_document_status_counts),
            
            ToolTest("clear_cache", "/documents/clear_cache", "POST", "System Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.RESPONSE_MODEL, None, 
                    "Fix response model", "MEDIUM", self._test_clear_cache),
            
            ToolTest("get_health", "/health", "GET", "System Management", 
                    ToolStatus.NOT_TESTED, IssueCategory.WORKING, None, 
                    "Already working", "LOW", self._test_get_health),
        ]
    
    async def _get_client(self) -> LightRAGClient:
        """Get or create LightRAG client."""
        if self.client is None:
            base_url = os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621")
            api_key = os.getenv("LIGHTRAG_API_KEY", "lightragsecretkey")
            self.client = LightRAGClient(base_url=base_url, api_key=api_key)
        return self.client
    
    # Test functions for each tool
    async def _test_insert_text(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.insert_text("Test document for API alignment")
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_insert_texts(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            texts = [{"title": "Test 1", "content": "Content 1"}, {"title": "Test 2", "content": "Content 2"}]
            result = await client.insert_texts(texts)
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_upload_document(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            # This will fail until we implement multipart form-data
            result = await client.upload_document("/tmp/test.txt")
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_scan_documents(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.scan_documents()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_documents(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_documents()
            return ToolStatus.WORKING, None
        except Exception as e:
            if "500" in str(e) and "file_path" in str(e):
                return ToolStatus.BLOCKED, "Server-side validation error"
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_documents_paginated(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_documents_paginated(1, 10)
            return ToolStatus.WORKING, None
        except Exception as e:
            if "500" in str(e) and "file_path" in str(e):
                return ToolStatus.BLOCKED, "Server-side validation error"
            return ToolStatus.BROKEN, str(e)
    
    async def _test_delete_document(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.delete_document("test_doc_id")
            return ToolStatus.WORKING, None
        except Exception as e:
            if "unexpected keyword argument 'json'" in str(e):
                return ToolStatus.BROKEN, "HTTP DELETE with JSON issue"
            return ToolStatus.BROKEN, str(e)
    
    async def _test_clear_documents(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.clear_documents()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_query_text(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.query_text("test query", mode="hybrid")
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_query_text_stream(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            chunks = []
            async for chunk in client.query_text_stream("test query", mode="hybrid"):
                chunks.append(chunk)
                if len(chunks) > 5:  # Limit for testing
                    break
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_knowledge_graph(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_knowledge_graph()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_graph_labels(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_graph_labels()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_check_entity_exists(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.check_entity_exists("test_entity")
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_update_entity(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.update_entity("test_entity_id", {"name": "updated"})
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_update_relation(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.update_relation("test_relation_id", {"weight": 0.9})
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_delete_entity(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.delete_entity("test_entity_id")
            return ToolStatus.WORKING, None
        except Exception as e:
            if "unexpected keyword argument 'json'" in str(e):
                return ToolStatus.BROKEN, "HTTP DELETE with JSON issue"
            return ToolStatus.BROKEN, str(e)
    
    async def _test_delete_relation(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.delete_relation("test_relation_id")
            return ToolStatus.WORKING, None
        except Exception as e:
            if "unexpected keyword argument 'json'" in str(e):
                return ToolStatus.BROKEN, "HTTP DELETE with JSON issue"
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_pipeline_status(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_pipeline_status()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_track_status(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_track_status("test_track_id")
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_document_status_counts(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_document_status_counts()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_clear_cache(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.clear_cache()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def _test_get_health(self) -> Tuple[ToolStatus, Optional[str]]:
        try:
            client = await self._get_client()
            result = await client.get_health()
            return ToolStatus.WORKING, None
        except Exception as e:
            return ToolStatus.BROKEN, str(e)
    
    async def run_all_tests(self, phase: str = "baseline") -> TestResults:
        """Run all tool tests and return results."""
        print(f"\n🧪 Running API Alignment Tests - Phase: {phase}")
        print("=" * 60)
        
        working_count = 0
        broken_count = 0
        
        for tool in self.tools:
            if tool.test_function:
                print(f"Testing {tool.name}...", end=" ")
                try:
                    status, error = await tool.test_function()
                    tool.status = status
                    tool.error_message = error
                    
                    if status == ToolStatus.WORKING:
                        working_count += 1
                        print("✅")
                    elif status == ToolStatus.BLOCKED:
                        print("🚫 (blocked)")
                    else:
                        broken_count += 1
                        print(f"❌ ({error[:50]}...)" if error else "❌")
                        
                except Exception as e:
                    tool.status = ToolStatus.BROKEN
                    tool.error_message = str(e)
                    broken_count += 1
                    print(f"❌ (Exception: {str(e)[:50]}...)")
        
        # Calculate success rate
        total_testable = len([t for t in self.tools if t.test_function])
        success_rate = (working_count / total_testable) * 100 if total_testable > 0 else 0
        
        # Create results (exclude test_function from serialization)
        tools_data = []
        for tool in self.tools:
            tool_dict = {
                'name': tool.name,
                'endpoint': tool.endpoint,
                'method': tool.method,
                'category': tool.category,
                'status': tool.status.value if hasattr(tool.status, 'value') else str(tool.status),
                'issue_category': tool.issue_category.value if tool.issue_category and hasattr(tool.issue_category, 'value') else str(tool.issue_category) if tool.issue_category else None,
                'error_message': tool.error_message,
                'expected_fix': tool.expected_fix,
                'priority': tool.priority
            }
            tools_data.append(tool_dict)
        
        results = TestResults(
            timestamp=datetime.now().isoformat(),
            total_tools=total_testable,
            working_tools=working_count,
            broken_tools=broken_count,
            success_rate=success_rate,
            phase=phase,
            tools=tools_data
        )
        
        # Save results
        self._save_results(results)
        self._update_progress_report(results)
        
        print(f"\n📊 Results Summary:")
        print(f"   Working: {working_count}/{total_testable} ({success_rate:.1f}%)")
        print(f"   Broken: {broken_count}")
        print(f"   Phase: {phase}")
        
        return results
    
    def _save_results(self, results: TestResults):
        """Save test results to JSON file."""
        # Load existing results
        all_results = []
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    all_results = json.load(f)
            except:
                all_results = []
        
        # Add new results
        all_results.append(asdict(results))
        
        # Save updated results
        with open(self.results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
    
    def _update_progress_report(self, results: TestResults):
        """Update the progress markdown report."""
        report = f"""# API Alignment Progress Report

## Current Status
- **Phase**: {results.phase}
- **Success Rate**: {results.success_rate:.1f}% ({results.working_tools}/{results.total_tools})
- **Last Updated**: {results.timestamp}

## Tool Status by Category

### Document Management Tools
"""
        
        # Group tools by category
        categories = {}
        for tool_data in results.tools:
            category = tool_data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_data)
        
        for category, tools in categories.items():
            report += f"\n### {category}\n"
            for tool in tools:
                status_icon = tool['status']
                error_msg = f" - {tool['error_message'][:100]}..." if tool['error_message'] else ""
                report += f"- **{tool['name']}**: {status_icon}{error_msg}\n"
        
        report += f"""
## Progress History
- Phase: {results.phase} - {results.success_rate:.1f}% success rate

## Next Steps
Based on current results, focus on:
1. HTTP Client Issues (DELETE requests)
2. Request Parameter Mismatches
3. Response Model Alignment

---
*Generated automatically by api_alignment_tracker.py*
"""
        
        with open(self.progress_file, 'w') as f:
            f.write(report)
    
    def get_tools_by_issue_category(self, category: IssueCategory) -> List[ToolTest]:
        """Get all tools with a specific issue category."""
        return [tool for tool in self.tools if tool.issue_category == category]
    
    def get_tools_by_priority(self, priority: str) -> List[ToolTest]:
        """Get all tools with a specific priority."""
        return [tool for tool in self.tools if tool.priority == priority]

async def main():
    """Main function to run the tracker."""
    if len(sys.argv) > 1:
        phase = sys.argv[1]
    else:
        phase = "baseline"
    
    tracker = APIAlignmentTracker()
    results = await tracker.run_all_tests(phase)
    
    print(f"\n📋 Detailed results saved to: {tracker.results_file}")
    print(f"📋 Progress report saved to: {tracker.progress_file}")
    
    # Show next steps based on results
    if results.success_rate < 50:
        print(f"\n🎯 Recommended Next Steps:")
        print(f"   1. Fix HTTP Client Issues (5 tools)")
        print(f"   2. Fix Request Parameter Mismatches (6 tools)")
        print(f"   3. Fix Response Model Issues (8 tools)")

if __name__ == "__main__":
    asyncio.run(main())
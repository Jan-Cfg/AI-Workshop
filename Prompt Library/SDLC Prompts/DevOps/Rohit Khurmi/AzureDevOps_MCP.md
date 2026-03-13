## MCP Server
AzureDevOps MCP Server allows AI clients to interact directly with Azure DevOps projects, queries, work items, pipelines, and repositories.

## Tools
1. **wit_get_query_results_by_id**  
   - Purpose: Fetch work item IDs from a saved query in Azure DevOps.  
   - Args: project, queryId  

2. **wit_get_work_items_batch_by_ids**  
   - Purpose: Fetch detailed work item information based on IDs.  
   - Args: project, workItemIds  

## Purpose
- Connects to AzureDevOps MCP Server using interactive authentication  
- Fetches work item IDs from a saved query (e.g., “UAT Completed” items)  
- Retrieves detailed information for those work items in batch  
- Displays structured details (Id, Title, State, Assigned To, Type, Tags) in console  
import os
import json
from mcp.server.fastmcp import FastMCP
try:
    from . import openshift_pípeline_interface as opi
except:
    import openshift_pípeline_interface as opi

mcp = FastMCP("PipelinesTool")

@mcp.resource(uri = "tekton://pipelines", mime_type = "application/json")
def get_pipelines() -> str:
    """Get all Pipelines in the cluster"""
    return json.dumps(opi.list_pipelines(), default=lambda o : o.__dict__)

@mcp.resource(uri = "tekton://pipeline/{namespace}/{pipeline}/pipelineruns", mime_type = "application/json")
def get_pipeline_runs(namespace: str, pipeline: str) -> str:
    """Get PipelineRuns for a specified Pipeline"""
    return json.dumps(opi.list_pipeline_runs(namespace, "pipeline"), default=lambda o : o.__dict__)

@mcp.resource(uri = "tekton://pipeline/{namespace}/{pipeline}/pipelineruns/latest", mime_type = "application/json")
def get_last_pipeline_run(namespace: str, pipeline: str) -> str:
    """Get the last PipelineRun executed for a specified Pipeline"""
    return json.dumps(opi.get_last_pipeline_run(namespace, pipeline), default=lambda o : o.__dict__)

@mcp.resource(uri = "tekton://pipeline/{namespace}/{pipeline}/pipelineruns/failedratio", mime_type = "text/plain")
def get_failed_pipelinerun_ratio(namespace: str, pipeline: str) -> float:
    """Get the ratio of failed PipelineRuns to total PipelineRuns executed"""
    return opi.get_failed_run_ratio(namespace, pipeline)

@mcp.resource(uri = "tekton://pipelinerun/{namespace}/{pipelinerun}/taskruns", mime_type = "application/json")
def get_pipelines(namespace: str, pipelinerun: str) -> str:
    """Get TaskRuns for a specified PipelineRun"""
    return json.dumps(opi.list_task_runs(namespace, pipelinerun), default=lambda o : o.__dict__)

@mcp.resource(uri = "tekton://pipelinerun/{namespace}/{pipelinerun}/taskruns/failedlogs", mime_type = "application/json")
def get_pipelines(namespace: str, pipelinerun: str) -> str:
    """Get the logs for failed TaskRuns for a specified PipelineRun"""
    return json.dumps(opi.get_failed_task_run_logs(namespace, pipelinerun), default=lambda o : o.__dict__)



if __name__ == "__main__":
    mcp.settings.host = os.environ.get("MCP_HOST", "*")
    mcp.settings.port = int(os.environ.get("MCP_PORT", "8080"))
    "http://{host}:{port}/mcp"
    mcp.run(transport = "streamable-http")


# inteligent-pipelines-llamastack

> Note the repository name spelling: `inteligent` (one `l`).

An MCP server that brings OpenShift Tekton pipeline data to AI assistants, so
they can answer questions about pipelines, inspect runs, and help triage
failures — part of the Intelligent Pipelines project: bringing AI/ML into
DevSecOps automation.

## What it does

The server exposes a `PipelinesTool` MCP service (streamable HTTP) backed by the
OpenShift CLI (`oc`) and the `openshift-client` Python library. It talks to the
cluster your `oc` session is authenticated against and offers these tools:

| Tool | What it returns |
| ---- | --------------- |
| `get_pipelines()` | All Pipelines in the cluster, across namespaces |
| `get_pipeline_runs(namespace, pipeline)` | PipelineRuns for a given pipeline, with start/end timestamps and status |
| `get_last_pipeline_run(namespace, pipeline)` | The most recent PipelineRun for a given pipeline |
| `get_failed_pipelinerun_ratio(namespace, pipeline)` | Fraction of PipelineRuns that failed (0 when there are none) |
| `get_task_runs(namespace, pipelinerun)` | TaskRuns of a PipelineRun, including their pods |
| `get_failed_tr_logs(namespace, pipelinerun)` | Logs from the pods of the failed TaskRuns of a PipelineRun |

That last tool is the triage shortcut: instead of hunting through pods by hand,
an assistant can ask for the failed task logs of a run directly.

## Repository layout

```text
mcp/
├── Containerfile                  Fedora-based image: oc CLI + Python deps
└── tekton_mcp_server/
    ├── __init__.py
    ├── mcp_server.py                FastMCP server ("PipelinesTool"), port 8080
    └── openshift_pípeline_interface.py
                                     OpenShift/Tekton queries via openshift-client
```

## Prerequisites

- An OpenShift cluster with Tekton Pipelines installed.
- An authenticated `oc` session against that cluster (the server uses the
  current session; for containers, mount your kubeconfig).
- Python 3, if running locally.
- `podman` or `docker`, if running the container image.

## Run locally

```bash
pip install "mcp[cli]" openshift-client
cd mcp/tekton_mcp_server
python mcp_server.py
```

The server listens on streamable HTTP. Host and port are configurable through
the environment:

```bash
MCP_HOST=127.0.0.1 MCP_PORT=8080 python mcp_server.py
```

Defaults are host `*` and port `8080`.

## Run as a container

Build from the `mcp/` directory so the server sources are in the build context:

```bash
cd mcp
podman build -t tekton-mcp-server .
podman run -p 8080:8080 -v "$HOME/.kube:/root/.kube:ro" tekton-mcp-server
```

The image is based on Fedora, installs the `oc` CLI and the Python
dependencies (`mcp[cli]`, `openshift-client`), copies the server to
`/opt/tekton_mcp_server`, exposes port 8080, and starts `mcp_server.py`.

## Connect an AI assistant

Point any MCP client that supports streamable HTTP transport at
`http://<host>:8080/mcp`. The client will discover the six tools listed above
and can call them with a namespace, pipeline, or pipeline run name, for example:
list the pipelines, get the last run of a pipeline, or fetch the logs of its
failed tasks.

## Related repositories

- [`intelligent-tekton-pipelines`](https://github.com/psehgaft/intelligent-tekton-pipelines)
  — the project overview and concept.
- [`intelligent-tekton-pipeline-app`](https://github.com/psehgaft/intelligent-tekton-pipeline-app)
  — the planned application component of the project.

## License

No license file is present in this repository yet.

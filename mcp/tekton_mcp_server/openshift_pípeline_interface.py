from datetime import datetime
import openshift_client as oc

class Pipeline:
    def __init__(self):
        self.namespace = None
        self.name = None
        self.params = []
        self.tasks = []
        self.pipeline_runs = []

class PipelineRun:
    def __init__(self):
        self.namespace = None
        self.name = None
        self.timestamp_start = None
        self.timestamp_end = None
        self.status = None
        self.task_runs = []

class TaskRun:
    def __init__(self):
        self.namespace = None
        self.name = None
        self.timestamp_start = None
        self.timestamp_end = None
        self.status = None
        self.pod = None
        self.logs = []

class ContainerLog:
    def __init__(self):
        container_name: None
        log = None

def list_pipelines():
    pipelines = []
    with oc.project("default"):
        objects = oc.selector("pipeline", all_namespaces=True).objects()
        for object in objects:
            pipeline = Pipeline()
            pipeline.namespace = object.model.metadata.namespace
            pipeline.name = object.model.metadata.name
            pipelines.append(pipeline)
            #TASKS

    return pipelines


def list_pipeline_runs(namespace,pipeline):
    pipeline_runs = []
    with oc.project(namespace):
        objects = oc.selector("pipelinerun", labels={"tekton.dev/pipeline" : pipeline}).objects()
        for object in objects:
            pipeline_run = PipelineRun()
            pipeline_run.namespace = object.model.metadata.namespace
            pipeline_run.name = object.model.metadata.name
            pipeline_run.timestamp_start = object.model.metadata.creationTimestamp
            pipeline_run.timestamp_end = object.model.status.completionTime
            pipeline_run.status = object.model.status.conditions[0].reason
            #TASKRUNS

            pipeline_runs.append(pipeline_run)

    return pipeline_runs

def get_last_pipeline_run(namespace,pipeline):
    pipeline_runs = list_pipeline_runs(namespace, pipeline)
    pipeline_runs.sort(key = lambda pr : datetime.strptime(pr.timestamp_start, "%Y-%m-%dT%H:%M:%SZ"), reverse=True)

    return pipeline_runs[0]

def get_failed_run_ratio(namespace,pipeline):
    successful_count = 0
    failed_count = 0
    with oc.project(namespace):
        objects = oc.selector("pipelinerun", labels={"tekton.dev/pipeline" : pipeline}).objects()
        if len(objects) > 0:
            for object in objects:
                if  object.model.status.conditions[0].reason == "Succeeded":
                    successful_count += 1
                else:
                    failed_count += 1
            ratio = failed_count / (failed_count + successful_count)
        else:
            ratio = 0
    return ratio

def list_task_runs(namespace,pipeline_run):
    task_runs = []
    with oc.project(namespace):
        objects = oc.selector("pipelinerun/"+pipeline_run).objects()[0].model.status.childReferences

        tr_names = []
        for object in objects:
            tr_names.append("taskrun/" + object.name)
            
        for task_run_object in oc.selector(tr_names).objects():
            task_run = TaskRun()
            task_run.namespace = task_run_object.model.metadata.namespace
            task_run.name = task_run_object.model.metadata.name
            task_run.timestamp_start = task_run_object.model.metadata.creationTimestamp
            task_run.timestamp_end = task_run_object.model.status.completionTime
            task_run.status = task_run_object.model.status.conditions[0].reason
            task_run.pod = task_run_object.model.status.podName

            task_runs.append(task_run)

    return task_runs

def get_failed_task_run_logs(namespace,pipeline_run):
    failed_task_runs = []
    task_runs = list_task_runs(namespace,pipeline_run)
    for run in task_runs:
        if run.status != "Succeeded":
            for name, log in oc.selector("pod/"+run.pod).logs().items():
                container_log = ContainerLog()
                container_log.container_name = name
                container_log.log = log
                run.logs.append(container_log)
            
            failed_task_runs.append(run)
    return failed_task_runs
    
    
KubernetesJobsDemo
==================

Demo files for Kubernetes Jobs and CronJobs 101

Kubernetes Jobs
---------------

There are some Job options:

  1. .spec.completions
  2. .spec.backoffLimit
  3. .spec.activeDeadlineSeconds

There are three types of Jobs:

  1. Non-parallel
  2. Parallel with a fixed number of runs
  3. Parallel with a work queue


**Basic Job Definition**

The [example calculate-pi job in this repo](calculate-pi.yml), describes a basic job definition in Kubernetes YAML-ese.

```
kind: Job
apiVersion: batch/v1
metadata:
  name: calculate-pi
spec:
  backoffLimit: 5
  activeDeadlineSeconds: 3600
  template:
    spec:
      containers:
      - name: pi-thon
        image: clcollins/pithon:1.1
        command: [ '/job.py' ]
      restartPolicy: Never
```

**.spec.completions**

The `.spec.completions` settings describes how many times a job should complete successfully before Kubernets considers the job done. The example above uses leaves `.spec.completions` unset, so the job will create the container and run it once.  If the run is successful, the job is considered successful.  If the container fails, Kubernetes will try again.

If `.spec.completions` is set to a number greater than `1`, Kubernetes will ensure that containers are created and run, until that number of them are successfully completed.  For example, if `.spec.completions` is set to `10`, in the calculate-pi.yml, Kubernetes will create and run python containers until ten of them complete successfully.

```
kind: Job
apiVersion: batch/v1
metadata:
  name: calculate-pi
spec:
  completions: 10
  backoffLimit: 5
  activeDeadlineSeconds: 3600
  template:
    spec:
      containers:
      - name: pi-thon
        image: clcollins/pithon:1.1
        command: [ '/job.py' ]
      restartPolicy: Never
```

**.spec.backoffLimit**

The `.spec.backoffLimit` option tells Kubernetes how many times a job can fail before it considers the job failed and stops trying to run it.  In the calculate-pi.yml file, `.spec.backoffLimit` is set to `5`, so Kubernetes will retry the job five times before marking it as failed.

The default is `6`, interestingly enough.

**.spec.activeDeadlineSeconds**

`.spec.activeDeadlineSeconds` is the amount of time, in seconds, that the job may run before before being terminated by Kubernetes.  For example, calculate-pi.yml specified `3600` seconds, or one hour, before the job is considered to have run too long.


**Non-parallel jobs**

Non-parallel jobs are Kubernetes Job objects that run a single instance of the pod defined in the `.spec.template`, eg:

    This thing needs to be done, once.  Go do that.


**Parallel jobs**

A non-parallel job uses the default value `.spec.parallelism=1`.  A parallel job is specified by setting `.spec.parallelism` to a value greater than `1`.

The value of `.spec.parallelism` defines the number of concurrent copies of the job specified in the `.spec.template` that Kubernetes will run.  Using the calculate-pi example again, if `.spec.parallelism` is set to `10`, Kubernetes will run ten copies of the python container running the `job.py` script, all at the same time:

```
kind: Job
apiVersion: batch/v1
metadata:
  name: calculate-pi
spec:
  parallelism: 10
  backoffLimit: 5
  activeDeadlineSeconds: 3600
  template:
    spec:
      containers:
      - name: pi-thon
        image: clcollins/pithon:1.1
        command: [ '/job.py' ]
      restartPolicy: Never
```

**Parallel with a fixed number of runs**

Parallel jobs can be run with a fixed number of completions, ie:

    Do this job 1000 times, and then stop

For example:

```
kind: Job
apiVersion: batch/v1
metadata:
  name: calculate-pi
spec:
  parallelism: 10
  completions: 100
  backoffLimit: 5
  activeDeadlineSeconds: 3600
  template:
    spec:
      containers:
      - name: pi-thon
        image: clcollins/pithon:1.1
        command: [ '/job.py' ]
      restartPolicy: Never
```

In this example, ten "calculate-pi" pods will be run at a time, until there have been one hundred successful completions.  Then Kubernetes will consider the job done.


**Parallel with a work queue**

An alternative to running parallel pods to a specific number of completions is parallel jobs with a work queue.  By leaving `.spec.completions` unset, the pods will run until they consider their work done, either by coordinating among themselves or working with an external service.

Borrowing directly from the Kubernetes docs:

```
Parallel Jobs with a work queue:  - do not specify .spec.completions, default to .spec.parallelism.  - the pods must coordinate with themselves or an external service to determine what each should work on.

    each pod is independently capable of determining whether or not all its peers are done, thus the entire Job is done.
    when any pod terminates with success, no new pods are created.
    once at least one pod has terminated with success and all pods are terminated, then the job is completed with success.
    once any pod has exited with success, no other pod should still be doing any work or writing any output. They should all be in the process of exiting.
```

An example of this would be a database of jobs to be completed, to which each pods connects.  The pods work down the jobs in the queue until there are no more, and none of the pods are working on any job - eg: they've all checked in and marked their tasks as completed.  Once they're all done, they can begin to terminate as `successful` and Kubernetes will consider the job done.


Kubernetes Cron Jobs
--------------------

Kubernetes Cron Jobs implement a job, using the same format as above, along with a specific schedule in the [Cron](https://en.wikipedia.org/wiki/Cron) format.  For example, the cronulate-pi.yml runs a job just like the calculate-pi.yml, but does so every two minutes, forever - `*/2 * * * *`.

```
kind: CronJob
apiVersion: batch/v1beta1
metadata:
  name: cronculate-pi
  labels:
    name: cronculate-pi
spec:
  schedule: "*/2 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pi-thon
            image: clcollins/pithon:1.1
            command: [ '/job.py' ]
          restartPolicy: Never
```

Note: A cron job will create a job _after the first interval_ if a specific time is not set.  In the example above, the cron job will not create and start the job until two minutes has elapsed.

Job Command Cheat Sheet
-----------------------

```
# List all jobs
kubectl get jobs

NAME                       DESIRED   SUCCESSFUL   AGE
cronculate-pi-1538059200   1         1            4m
cronculate-pi-1538059320   1         1            2m
cronculate-pi-1538059440   1         1            37s

# List all cron jobs
kubectl get cronjobs

NAME            SCHEDULE      SUSPEND   ACTIVE    LAST SCHEDULE   AGE
cronculate-pi   */2 * * * *   False     0         1m              19h

# Describe a job
kubectl describe job cronculate-pi-1538059440

Name:           cronculate-pi-1538059440
Namespace:      jobs-demo
Selector:       controller-uid=c979affa-c263-11e8-b658-0200bf2b4b94
Labels:         controller-uid=c979affa-c263-11e8-b658-0200bf2b4b94
                job-name=cronculate-pi-1538059440
Annotations:    <none>
Controlled By:  CronJob/cronculate-pi
Parallelism:    1
Completions:    1
Start Time:     Thu, 27 Sep 2018 10:44:07 -0400
Pods Statuses:  0 Running / 1 Succeeded / 0 Failed
Pod Template:
  Labels:  controller-uid=c979affa-c263-11e8-b658-0200bf2b4b94
           job-name=cronculate-pi-1538059440
  Containers:
   pi-thon:
    Image:      clcollins/pithon:1.1
    Port:       <none>
    Host Port:  <none>
    Command:
      /job.py
    Environment:  <none>
Events:
  Type    Reason            Age   From            Message
  ----    ------            ----  ----            -------
  Normal  SuccessfulCreate  1m    job-controller  Created pod: cronculate-pi-1538059440-bzzgs
```

## License

The information contained in this repository is licensed:

*Creative Commons CC0 1.0 Universal*

[More Info](LICENSE.md)


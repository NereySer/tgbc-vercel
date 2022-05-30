import json
import requests
import os, sys
from argparse import ArgumentParser

ENDPOINT = 'https://api.cron-job.org'
headers = {
    'Authorization': 'Bearer ' + os.getenv('CRONJOB_API_KEY'),
    'Content-Type': 'application/json'
}

def createParser ():
    parser = ArgumentParser()

    parser.add_argument('-t', '--title', required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('--hours', required=True, type=int, nargs='+')

    return parser

def getLink(jobId = None):
    if jobId is None:
        return '{}/jobs'.format(ENDPOINT)
    else:
        return '{}/jobs/{}'.format(ENDPOINT, jobId)

def createJobDetails(options):
    with open(os.path.join(sys.path[0], "cronjob.json"), "r") as json_file:
        job = json.load(json_file)

        job['job']['title'] = options.title
        job['job']['url'] = options.url
        job['job']['schedule']['hours'] = options.hours

    return job

def getJobs():
    response = requests.get(getLink(), headers=headers)

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Error {} while listing jobs'.format(response.status_code))

    return response.json()['jobs']

def deleteJob(jobId):
    response = requests.delete(getLink(jobId), headers=headers)

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Error {} while deleting {}'.format(response.status_code, job['jobId']))

def getJobInfo(jobId):
    response = requests.get(getLink(jobId), headers=headers)

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Error {} while gettinj job {} info'.format(response.status_code, jobId))

    return response.json()

def updateJob(jobId, jobInfo):
    response = requests.patch(getLink(jobId), headers=headers, data=json.dumps(jobInfo))

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Error {} while patching {}'.format(response.status_code, jobId))

def createJob(jobInfo):
    response = requests.put(getLink(), headers=headers, data=json.dumps(jobInfo))

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Error {} while creating'.format(response.status_code))

    return response.json()['jobId']

def removeDuplicatedJobs(jobs):
    while len(jobs) > 1:
        job = jobs.pop()

        deleteJob(job['jobId'])

        print('Successfully deleted job {}'.format(job['jobId']))

def correctJob(target_job, jobs):
    removeDuplicatedJobs(jobs)

    job_info = getJobInfo(jobs[0]['jobId'])

    job_info['jobDetails'] = {
        key: value for key, value in job_info['jobDetails'].items() if key in target_job['job']
    }

    if target_job['job'] != job_info['jobDetails']:
        updateJob(jobs[0]['jobId'], target_job)

        return True

    return False

def main():
    parser = createParser()
    options = parser.parse_args()
    job_info_create = createJobDetails(options)

    filtered_jobs = list(filter(lambda job: job['title'] == options.title, getJobs()))

    if not filtered_jobs:
        jobId = createJob(job_info_create)

        print('Successfully created job {}'.format(jobId))
    elif correctJob(job_info_create, filtered_jobs):
        print('Successfully patched job {}'.format(filtered_jobs[0]['jobId']))
    else:
        print('Job {} is already present'.format(filtered_jobs[0]['jobId']))

if __name__ == "__main__":
    main()

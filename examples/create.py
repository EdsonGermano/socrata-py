import os
from os import path
from socrata.authorization import Authorization
from socrata.publish import Publish
from time import sleep
import sys
import time
import argparse

parser = argparse.ArgumentParser(description='Create a dataset.')
parser.add_argument('name', type=str, help='Name of your dataset')
parser.add_argument('csv', type=str, help='Path to the CSV')
parser.add_argument('domain', type=str, help='Your Socrata domain')
parser.add_argument('--username', type=str, help='Your Socrata username', default = os.environ['SOCRATA_USERNAME'])
parser.add_argument('--password', type=str, help='Your Socrata password', default = os.environ['SOCRATA_PASSWORD'])
args = parser.parse_args()


domain = 'localhost'
auth = Authorization(
  args.domain,
  args.username,
  args.password
)

if 'localhost' in args.domain:
    auth.live_dangerously()

def path_to_show(resource):
    return '{proto}{domain}{uri}'.format(
        proto = auth.proto,
        domain = auth.domain,
        uri = resource.show_uri
    )

def create(name, filepath):
    publishing = Publish(auth)

    (ok, view) = publishing.new({'name': name})
    assert ok, view

    (ok, revision) = publishing.revisions.create(view['id'])
    assert ok, revision

    (ok, upload) = revision.create_upload({'filename': path.basename(filepath)})
    assert ok, upload

    print("Created an Upload, accessible at: " + path_to_show(upload))

    with open(filepath, 'rb') as csv_file:
        (ok, input_schema) = upload.csv(csv_file)
        assert ok, input_schema

    (ok, output_schema) = input_schema.latest_output()
    assert ok, output_schema

    (ok, output_schema) = output_schema.wait_for_finish()
    assert ok, output_schema

    print("Schema has completed, accessible at: " + path_to_show(output_schema))
    print("Found {error_count} validation errors as the result of applying transforms".format(
        error_count = output_schema.attributes['error_count']
    ))

    (ok, upsert_job) = output_schema.apply()
    assert ok, upsert_job
    print("Started upsert, job is viewable at" + path_to_show(upsert_job))

    upsert_job.wait_for_finish(progress = lambda job: sys.stdout.write(str(job.attributes['log'][0]) + "\n"))

    print("Your view is ready: {url}".format(
        url = auth.proto + auth.domain + '/d/' + view['id']
    ))

create(args.name, args.csv)
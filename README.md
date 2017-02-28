# publish-py
experimental sdk for the socrata publishing api



## Using

### Create a revision
```python
# Import some stuff
from src.authorization import Authorization
from src.publish import Publish

# Boilerplate...
# Make an auth object
auth = Authorization(
  "pete-test.test-socrata.com",
  os.environ['SOCRATA_LOCAL_USER'],
  os.environ['SOCRATA_LOCAL_PASS']
)

publishing = Publish(auth)

# This is our view
fourfour = "ij46-xpxe"

# Make a revision
(ok, rev) = publishing.revisions.create(fourfour)
assert ok

# rev is a Revision object, we can print it
print(rev)
Resource({'created_by': {'display_name': 'rozap',
                'email': 'chris.duranti@socrata.com',
                'user_id': 'tugg-ikce'},
 'fourfour': 'ij46-xpxe',
 'id': 346,
 'inserted_at': '2017-02-27T23:05:08.522796',
 'metadata': None,
 'update_seq': 285,
 'upsert_jobs': []})

# We can also access the attributes of the revision
print(rev.attributes['fourfour'])
'ij46-xpxe'
```

### Make an upload, given a revision
```python
# Using that revision, we can create an upload
(ok, upload) = rev.create_upload({'filename': "foo.csv"})
assert ok

# And print it
print(upload)
Resource({'content_type': None,
 'created_by': {'display_name': 'rozap',
                'email': 'chris.duranti@socrata.com',
                'user_id': 'tugg-ikce'},
 'filename': 'foo.csv',
 'finished_at': None,
 'id': 290,
 'inserted_at': '2017-02-27T23:07:18.309676',
 'schemas': []})
```
### Upload a csv, given an upload
```python
# And using that upload we just created, we can put bytes into it
# We can also attach a progress callback
with open('test/fixtures/simple.csv', 'rb') as f:
    (ok, input_schema) = upload.csv(f, progress = lambda p: print("Uploaded %s" % p['total_bytes']))
    assert ok
```

### Transform a file, given an input schema
```python
# Putting bytes into an upload gives us an input schema. We can call `transform` on the 
# input schema to get a new output schema with our transforms applied. 
# We can also attach a progress callback, which will give us progress events, 
# error events, and finish events to let us know when our transform is done.
(ok, output_schema) = input_schema.transform({
    'output_columns': [
        {
            "field_name": "b",
            "display_name": "b, but as a number",
            "position": 0,
            "description": "b but with a bunch of errors",
            "transform": {
                "transform_expr": "to_number(b)"
            }
        }
    ]},
    progress = lambda event: print('Column %s has transformed %s rows' % (event['column']['field_name'], event['end_row_offset']))
)
```

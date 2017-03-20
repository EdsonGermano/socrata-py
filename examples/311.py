import os
from socrata.authorization import Authorization
from socrata.publish import Publish
from time import sleep
import sys

def write_progress(progresses):
    def k(wat):
        (label, _c, _t) = wat
        return label
    progresses = sorted(progresses, key = k)
    for _ in progresses:
        sys.stdout.write('\x1b[1A')

    for label, current, total in progresses:
        bar_len = 60
        filled_len = int(round(bar_len * current / float(total)))

        percents = round(100.0 * current / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s | %s (%s / %s)\r\n' % (bar, percents, '%', label, current, total))

    sys.stdout.flush()

def row_count(path):
    return 105381
    with open(path) as f:
        for i, _ in enumerate(f):
            pass
    return i

auth = Authorization(
  "localhost",
  os.environ['SOCRATA_LOCAL_USER'],
  os.environ['SOCRATA_LOCAL_PASS']
)

fourfour = "ij46-xpxe"

path = '/home/chris/Downloads/Crimes_-_2001_to_present.csv'
path = '/home/chris/Downloads/boo.csv'
path = '/home/chris/Downloads/metcalf.csv'

def main():
    p = Publish(auth) #
    (ok, rev) = p.revisions.create(fourfour) #
    assert ok
    (ok, upload) = rev.create_upload({'filename': "311.csv"}) #

    total_row_count = row_count(path)

    def upload_progress(p):
        write_progress(
            [('Rows Uploaded', p['end_row_offset'], total_row_count)]
        )

    with open(path, 'rb') as f:
        print("Starting...\n")
        (ok, input_schema) = upload.csv(f, progress = upload_progress) #
        assert ok, "Failed to upload the file! %s" % input_schema

        input_schema.show()
        print(input_schema.show_uri())
        return

        print("\nStarting transform...")

        columns = [
            {
                "field_name": "latlng",
                "display_name": "LatLng WKT",
                "position": 0,
                "description": "WKT of lat lng",
                "transform": {
                    "transform_expr": '"POINT(" || to_text(`latitude`) || " " || to_text(`longitude`) || ")"'
                }
            },
            {
                "field_name": "x_coord",
                "display_name": "X",
                "position": 1,
                "description": "x plus 20",
                "transform": {
                    "transform_expr": "to_number(`x_coordinate`) + 20"
                }
            },
            {
                "field_name": "y_coord",
                "display_name": "y",
                "position": 2,
                "description": "y plus 10",
                "transform": {
                    "transform_expr": "to_number(`y_coordinate`) + 10"
                }
            }
        ]

        for _ in columns:
            print('')

        total = input_schema.attributes['total_rows']
        ps = {c['field_name']: 0 for c in columns}

        finished = 0
        def transform_progress(event):
            nonlocal finished
            name = event['column']['field_name']

            if event['type'] == 'max_ptr':
                now = event['end_row_offset']
                old = ps[name]
                ps[name] = max(now, old)
                write_progress(
                    [(field_name, current, total) for (field_name, current) in ps.items()]
                )
            elif event['type'] == 'finished':
                write_progress(
                    [(field_name, total, total) for (field_name, current) in ps.items()]
                )
                finished += 1

        (ok, output_schema) = input_schema.transform(
            {'output_columns': columns},
            progress = transform_progress
        )

        assert ok, "Failed to transform %s" % output_schema

        while finished < len(columns):
            sleep(1)

    print("\n\nDone!\n\n")

if __name__ == '__main__':
    main()
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import sqlite3

@shared_task
def render_images(uid, outdir):
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()
    
    if 'status' not in get_tables():
        query = 'CREATE TABLE status (uid INTEGER PRIMARY KEY, status BIT default "FALSE")'
        c.execute(query)

    c.execute('INSERT OR REPLACE INTO status VALUES (?, ?);', (uid, False,))

    """ Load images from DB and render """
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()

    # Load users image data
    c.execute('SELECT * FROM pulses WHERE uid=?;', (uid,))
    table = c.fetchall()
    table = [t for t in table if t[4] == uid]

    # Load CNN
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    model = load_model(__location__ + '/CNN200x300ep30.h5')

    fig, ax = plt.subplots()

    for i, row in enumerate(table):
        # Only render files that haven't been rendered yet
        if row[2] == '1':
            continue

        # Mark pulse as rendered
        with conn:
            c.execute(f"UPDATE pulses SET classification = '1' WHERE {str(i)} = ROWID;")

        # Convert DB string to 2d list
        pulse = ast.literal_eval(row[1])

        # Split pulse into x and y coords
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # Generate image path
        save_path = f"{outdir}/^_{row[0].replace('#', '')}_{i}.png"

        # Render the image
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, format='png', Transparency=True, dpi=50)
        plt.cla()
        gc.collect()
        # Classify as normal or abnormal
        # TODO- perform at insert?
        if not CNN.classifyCNN(save_path, model) == 0:
            os.rename(save_path, save_path.replace('^', 'e'))
        else:
            os.rename(save_path, save_path.replace('^', 'a'))

    c.execute('INSERT OR REPLACE INTO status VALUES (?, ?);', (uid, True,))

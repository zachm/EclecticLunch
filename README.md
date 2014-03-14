EclecticLunch
=============

Setup
-----

* virtualenv venv
* source venv/bin/activate
* pip install -r requirements.txt
* <pre>./main.py shell &lt;&lt;EOF
import models
models.db.create_all()
models.db.session.commit()
EOF</pre>

Running
-------

<dl>
    <dt>python main.py</dt>
    <dd>
        This will bind to all interfaces on port 8008.<br />
        Other options are found under --help.
    </dd>
</dl>

Hack'13!!!

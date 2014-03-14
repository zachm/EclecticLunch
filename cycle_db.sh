#!/bin/bash
rm development.db
./main.py shell <<EOF
import models
models.db.create_all()
models.db.session.commit()
EOF

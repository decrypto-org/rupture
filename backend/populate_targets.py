import django
import os
import yaml
from backend.settings import BASE_DIR
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from breach.models import Target


def create_target(target):
    t = Target(
        name=target['name'],
        endpoint=target['endpoint'],
        prefix=target['prefix'],
        alphabet=target['alphabet'],
        secretlength=target['secretlength'],
        alignmentalphabet=target['alignmentalphabet'],
        recordscardinality=target['recordscardinality']
    )
    t.save()
    print '''Created Target:
             \tname: {}
             \tendpoint: {}
             \tprefix: {}
             \talphabet: {}
             \tsecretlength: {}
             \talignmentalphabet: {}
             \trecordscardinality'''.format(
                t.name,
                t.endpoint,
                t.prefix,
                t.alphabet,
                t.secretlength,
                t.alignmentalphabet,
                t.recordscardinality
            )

if __name__ == '__main__':
    try:
        with open(os.path.join(BASE_DIR, 'target_config.yml'), 'r') as ymlconf:
            cfg = yaml.load(ymlconf)
    except IOError, err:
        print 'IOError: %s' % err
        exit(1)
    targets = cfg.items()

    for t in targets:
        target = t[1]
        target['name'] = t[0]
        try:
            create_target(target)
        except (IntegrityError, ValueError), err:
            if isinstance(err, IntegrityError):
                print '[!] Target "{}" already exists.'.format(target['name'])
            elif isinstance(err, ValueError):
                print '[!] Invalid parameters for target "{}".'.format(target['name'])

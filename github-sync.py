#!/usr/bin/python

import  argparse
import  atexit
import  json
import  os
import  re
import  subprocess
import  sys
import  urllib2

results = dict()

def report():
    # Q&D saving
    fmt = '{0:<2} {1}'
    with open( 'STATUS', 'w' ) as f:
        for repo in sorted( results ):
            state = results[ repo ]
            if isinstance( state, bool ):
                print >>f, fmt.format(
                    '  ' if state else '**',
                    repo
                )
            elif isinstance( state, list ):
                print >>f, fmt.format( '->', repo )
                for line in state:
                    print >>f, fmt.format( '**', line )
            else:
                print >>f, fmt.format( '**', state )
    return

p = argparse.ArgumentParser(
         description = 'Mirror all GitHub repos for a given user locally.'
)
p.add_argument(
    '-n',
    '--dry-run',
    dest   = 'dry_run',
    action = 'store_true',
    help   = 'Just kidding.  Really!'
)
p.add_argument(
    '--forks',
    dest   = 'forks',
    action = 'store_true',
    help   = 'Include forked repos'
)
p.add_argument(
    '-u',
    '--user',
    dest    = 'user',
    action  = 'store',
    type    = str,
    default = 'megacoder',
    help    = 'GitHub user name to sync'
)
here = os.getenv( 'PWD' )
if not here:
    here = '.'
p.add_argument(
    '-d',
    '--directory',
    dest    = 'directory',
    action  = 'store',
    type    = str,
    default = here,
    help    = 'Directory to store repos in'
)
p.set_defaults( forks = False )
args = p.parse_args()

if not args.dry_run:
    os.chdir(args.directory)

def run( cmd ):
    print '$ {0}'.format( ' '.join( cmd ) )
    if args.dry_run:
        cmd = [ '/bin/echo' ] + cmd
    try:
        output = subprocess.check_output(
            cmd,
            stderr = subprocess.STDOUT
        )
        err = None
    except subprocess.CalledProcessError, e:
        output = None
        err = e.output
    except Exception, e:
        raise e
    return output, err

URL = u'https://api.github.com/users/{0}/repos'.format( args.user )
URL += u'?sort=full_name'
URL += u'&type=all'
URL += u'&per_page=100'

atexit.register( report )

bar = '#' * 80
pageno = 0
while True:
    pageno += 1
    print
    print bar
    print '# Page {0}'.format( pageno )
    print bar
    print
    which = '&page={0}'.format( pageno )
    f = urllib2.urlopen( URL + which )
    repos = json.loads(
        urllib2.urlopen( URL + which ).read()
    )
    if len(repos) == 0:
        break
    for repo in sorted(
        repos,
        key = lambda r : r['name']
    ):
        name, url = repo["name"], repo["clone_url"]
        if re.search("[^A-Za-z0-9-_]", name):
            continue
        if re.search("[^A-Za-z0-9-_:/.]", url):
            continue
        if repo["private"]:
            continue
        if repo["fork"] and not args.forks:
            continue
        repo_here = name + '.git'
        if not os.path.exists( repo_here ):
            cmd = [
                '/bin/git',
                'clone',
                '--bare',
                '--mirror',
                url,
                repo_here
            ]
            output, err = run( cmd )
            if err:
                results[ name ] = err
                continue
            if not args.dry_run:
                os.chdir( repo_here )
            cmd = [
                '/bin/git',
                'remote',
                'add',
                'local',
                'ssh://git.darkzone.un/home/vault/depot/{0}'.format(
                    repo_here
                )
            ]
            output, err = run( cmd )
            if not args.dry_run:
                os.chdir("..")
            if err:
                results[ name ] = err
                continue
        if not args.dry_run:
            os.chdir( repo_here )
        cmd = [
            '/bin/git',
            'remote',
            'update'
        ]
        output, err = run( cmd )
        if not args.dry_run:
            os.chdir("..")
        if err:
            results[ name ] = err
            continue
        results[ name ] = True

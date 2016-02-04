ATTACH = 'attach'
COMMIT = 'commit'
COPY = 'copy'
CREATE = 'create'
DESTROY = 'destroy'
DIE = 'die'
EXEC_CREATE = 'exec_create'
EXEC_START = 'exec_start'
EXPORT = 'export'
KILL = 'kill'
OOM = 'oom'
PAUSE = 'pause'
RENAME = 'rename'
RESIZE = 'resize'
RESTART = 'restart'
START = 'start'
STOP = 'stop'
TOP = 'top'
UNPAUSE = 'unpause'

DELETE = 'delete'
IMPORT = 'import'
PULL = 'pull'
PUSH = 'push'
TAG = 'tag'
UNTAG = 'untag'

CONTAINER_EVENTS = (
    ATTACH,
    COMMIT,
    COPY,
    CREATE,
    DESTROY,
    DIE,
    EXEC_CREATE,
    EXEC_START,
    EXPORT,
    KILL,
    OOM,
    PAUSE,
    RENAME,
    RESIZE,
    RESTART,
    START,
    STOP,
    TOP,
    UNPAUSE
)

IMAGE_EVENTS = (
    DELETE,
    IMPORT,
    PULL,
    PUSH,
    TAG,
    UNTAG
)

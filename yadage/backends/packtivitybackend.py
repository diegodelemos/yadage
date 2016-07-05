import logging
import adage.backends
import yadage.yadagestep
from packtivity import packtivity_callable
log = logging.getLogger(__name__)

class PacktivityProxyBase(object):
    '''
    A generic serializable proxy wrapper around a proxy object,
    that is passed in the ctor. Implementations can override details
    and proxyname methods
    '''
    def __init__(self,task,proxy,prepublished = None):
        self.proxy = proxy

    def details(self):
        return None

    def proxyname(self):
        return 'PacktivityProxyBase'

    def json(self):
        details = None
        return {
            'type':self.proxyname(),
            'proxydetails': self.details()
        }

class AdagePacktivityBackendBase(object):
    '''
    A wrapper generic backend base class around an existing adage backend.
    Implementations need to override the submit method and figure out how
    to submit the task and return a appropriate proxy object deriving from
    PacktivityProxyBase
    '''

    def __init__(self,adagebackend):
        self.adagebackend = adagebackend

    def result(self,resultproxy):
        return self.adagebackend.result(resultproxy.proxy)

    def ready(self,resultproxy):
        return self.adagebackend.ready(resultproxy.proxy)

    def successful(self,resultproxy):
        return self.adagebackend.successful(resultproxy.proxy)

    def fail_info(self,resultproxy):
        return self.adagebackend.fail_info(resultproxy.proxy)

class PacktivityMultiProcBackend(AdagePacktivityBackendBase):
    def __init__(self,nparallel = 2):
        super(PacktivityMultiProcBackend,self).__init__(adage.backends.MultiProcBackend(nparallel))

    def submit(self,task):
        '''
        if the task type is a genuine yadagestep we submit is as a packtivity callable,
        if it's an init step, which has a trivial call body, we'll just use it directly
        '''
        tasktype = type(task)
        if tasktype == yadage.yadagestep.yadagestep:
            acallable = packtivity_callable(task.name,task.spec,task.attributes,task.context)
        elif tasktype == yadage.yadagestep.initstep:
            acallable = task
        else:
            raise RuntimeError('cannot figure out how to submit a task of type {}'.format(tasktype))

        multiprocprox = self.adagebackend.submit(acallable)

        #since we can't really persistify the proxies of an in-memory process pool, we'll just return the base
        return PacktivityProxyBase(task,multiprocprox)
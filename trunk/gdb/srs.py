import gdb, traceback;

'''
Usage:
    nn_coroutines
    nn_coroutines 1000
'''
class NnCouroutines(gdb.Command):
    def __init__(self):
        super(NnCouroutines, self).__init__('nn_coroutines', gdb.COMMAND_DATA)

    # https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html#Python-API
    def invoke(self, arg, from_tty):
        nn_coroutines = 1
        # Parse args.
        args = arg.split(' ')
        nn_interval = int(args[0]) if args[0] != '' else 1000
        try:
            pnext = prev = pthis = gdb.parse_and_eval('&_st_this_thread->tlink').__str__()
            print(f'interval: {nn_interval}, first: {pthis}, args({len(args)}): {args}')
            while True:
                v = gdb.parse_and_eval(f'((_st_clist_t*){pnext})->next')
                prev = pnext = str(v.__str__()).split(' ')[0]
                if pnext == pthis:
                    break
                nn_coroutines += 1
                if (nn_coroutines%nn_interval) == 0:
                    print(f'next is {pnext}, total {nn_coroutines}')
        except:
            print(f'Error: prev={prev}, this={pthis}, next={pnext}, v={v}')
            traceback.print_exc()
        # Result.
        print(f'total coroutines: {nn_coroutines}')

NnCouroutines()

'''
Usage:
    show_coroutines
'''
class ShowCouroutines(gdb.Command):
    def __init__(self):
        super(ShowCouroutines, self).__init__('show_coroutines', gdb.COMMAND_DATA)

    # https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html#Python-API
    def invoke(self, arg, from_tty):
        offset = gdb.parse_and_eval('(int)(&(((_st_thread_t*)(0))->tlink))').__str__()
        _st_this_thread = gdb.parse_and_eval('_st_this_thread').__str__()
        pnext = prev = pthis = gdb.parse_and_eval('&_st_this_thread->tlink').__str__()
        this_thread2 = gdb.parse_and_eval(
            f'(_st_thread_t*)({pthis} - {offset})'
        ).__str__()
        #print('offset=%s, _st_this_thread=%s, pthis-offset=%s'%(offset, _st_this_thread, this_thread2))
        try:
            while True:
                trd = gdb.parse_and_eval(f'(_st_thread_t*)({pnext} - {offset})').__str__()
                jmpbuf = (
                    gdb.parse_and_eval(f'((_st_thread_t*){trd})->context.__jmpbuf')
                    .__str__()
                    .split(', ')
                )
                rbp, rsp, crip = int(jmpbuf[1]), int(jmpbuf[6]), None
                if rbp > 0 and rsp > 0:
                    crip = gdb.execute(f'x/2xa {rbp}', to_string=True).split('\t')[2].strip()
                    print(f'thread: {trd}, caller: {crip}')
                v = gdb.parse_and_eval(f'((_st_clist_t*){pnext})->next')
                prev = pnext = str(v.__str__()).split(' ')[0]
                if pnext == pthis:
                    break
        except:
            print(f'Error: prev={prev}, this={pthis}, next={pnext}')
            traceback.print_exc()

ShowCouroutines()

from array import array
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class VM(object):

    def __init__(self):
        self.registers = [None, None, None, None, None, None, None, None]
        self.stack = []
        self.memory = array('H')
        self.current_element = 0
        self.exit = False
        self.str_buffer = ''

    def load_data(self, filename):
        logger.info('Loading data from %s' % filename)
        code_str = file(filename, 'rb').read()
        self.memory.fromstring(code_str)
        logger.info('Read %s items into memory' % len(self.memory))

    def get_value(self, v):
        if v in range(0, 32767+1):
            return v
        elif v in range(32768, 32775+1):
            _v = self.registers[v-32768]
            if _v in range(32768, 32775+1):
                return self.get_value(_v)
            else:
                return _v

    def set_register(self, address, value):
        register = address-32768
        self.registers[register] = value
        logger.info('Setting register %s value to %s' % (register, value))

    def execute(self):

        while self.exit is False:

            _v = self.memory[self.current_element]
            try:
                arg1 = self.memory[self.current_element+1]
            except IndexError:
                arg1 = None
            try:
                arg2 = self.memory[self.current_element+2]
            except IndexError:
                arg2 = None
            try:
                arg3 = self.memory[self.current_element+3]
            except IndexError:
                arg3 = None

            logger.debug('cel: %s _v: %s arg1: %s arg2: %s arg3: %s' % (
                self.current_element, _v, arg1, arg2, arg3))

            if self.str_buffer is not None and _v != 19:
                print self.str_buffer
                self.str_buffer = None

            if _v == 0:
                self._halt()
            elif _v == 1:
                self._set(arg1, arg2)
            elif _v == 2:
                self._push(arg1)
            elif _v == 3:
                self._pop(arg1)
            elif _v == 4:
                self._eq(arg1, arg2, arg3)
            elif _v == 5:
                self._gt(arg1, arg2, arg3)
            elif _v == 6:
                self._jmp(arg1)
            elif _v == 7:
                self._jt(arg1, arg2)
            elif _v == 8:
                self._jf(arg1, arg2)
            elif _v == 9:
                self._add(arg1, arg2, arg3)
            elif _v == 10:
                self._mult(arg1, arg2, arg3)
            elif _v == 11:
                self._mod(arg1, arg2, arg3)
            elif _v == 12:
                self._and(arg1, arg2, arg3)
            elif _v == 13:
                self._or(arg1, arg2, arg3)
            elif _v == 14:
                self._not(arg1, arg2)
            elif _v == 15:
                self._rmem(arg1, arg2)
            elif _v == 16:
                self._wmem(arg1, arg2)
            elif _v == 17:
                self._call(arg1)
            elif _v == 18:
                self._ret()
            elif _v == 19:
                self._out(arg1)
            elif _v == 20:
                self._in(arg1)
            elif _v == 21:
                self._noop()
            else:
                print 'Unknown instruction: %s' % _v
                print self.registers
                print self.stack
                print self.memory[:10]
                break

    def _halt(self):
        self.exit = True

    def _set(self, arg1, arg2):
        logger.info('Set register %s value to %s' % (arg1, arg2))
        self.set_register(32768, arg2)
        self.current_element += 3

    def _push(self, arg1):
        _v_tp_push = self.get_value(arg1)
        logger.info('Push %s to the top of the stack' % _v_tp_push)
        self.stack.append(_v_tp_push)
        self.current_element += 2

    def _pop(self, r_address):
        if len(self.stack) == 0:
            raise Exception('Trying to pop value from empty stack')
        _v = self.stack.pop()
        logger.info('Setting register %s to %s' % (r_address, _v))
        self.set_register(r_address, _v)
        self.current_element += 2

    def _eq(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        logger.info('Checking if %s equals %s' % (_p1, _p2))
        if _p1 == _p2:
            logger.info('Did equal, setting %s to 1' % r_address)
            self.set_register(r_address, 1)
        else:
            logger.info('Did not equal, setting %s to 0' % r_address)
            self.set_register(r_address, 0)
        self.current_element += 4

    def _gt(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        logger.info('Checking if %s is greater than %s' % (_p1, _p2))
        if _p1 > _p2:
            self.set_register(r_address, 1)
        else:
            self.set_register(r_address, 0)
        self.current_element += 4

    def _jmp(self, arg1):
        logger.info('Jump to %s' % arg1)
        self.current_element = arg1

    def _jt(self, arg1, arg2):
        logger.info('Jump to %s if %s is nonzero' % (arg2, arg1))
        if self.get_value(arg1) != 0 and self.get_value(arg1) is not None:
                logger.info('Jumping to %s' % self.get_value(arg2))
                self.current_element = self.get_value(arg2)
        else:
            self.current_element += 3

    def _jf(self, arg1, arg2):
        logger.info('Jump to %s if %s is zero' % (arg2, arg1))
        if arg1 == 0:
            logger.info('Jumping to %s' % arg2)
            self.current_element = arg2
        else:
            self.current_element += 3

    def _add(self, r_address, arg2, arg3):
        logger.info('Adding %s to %s and storing in %s' % (
            arg2, arg3, r_address))
        value = (self.get_value(arg2)+self.get_value(arg3)) % 32768
        self.set_register(r_address, value)
        self.current_element += 4

    def _mult(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        _v = (_p1*_p2) % 32768
        self.set_register(r_address, _v)
        self.current_element += 4

    def _mod(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        _v = _p1 % _p2
        self.set_register(r_address, _v)
        self.current_element += 4

    def _and(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        _v = _p1 & _p2
        self.set_register(r_address, _v)
        self.current_element += 4

    def _or(self, r_address, arg2, arg3):
        _p1 = self.get_value(arg2)
        _p2 = self.get_value(arg3)
        _v = _p1 | _p2
        self.set_register(r_address, _v)
        self.current_element += 4

    def _not(self, r_address, arg2):
        _p1 = self.get_value(arg2)
        _v = ~_p1
        self.set_register(r_address, _v)
        self.current_element += 3

    def _rmem(self, r_address, arg2):
        _m_address = self.get_value(arg2)
        logger.info('Reading value from memory %s into register %s' % (
            _m_address, r_address))
        _v = self.memory[self.get_value(arg2)]
        self.set_register(r_address, _v)
        self.current_element += 3

    def _wmem(self, m_address, arg2):
        _v = self.get_value(arg2)
        self.memory[self.get_value(m_address)] = _v
        self.current_element += 3

    def _call(self, arg1):
        _p1 = self.get_value(arg1)
        _v = self.current_element + 2
        self._push(_v)
        self._jmp(_p1)

    def _ret(self):
        if len(self.stack) == 0:
            self._halt()
        _v_to_pop = self.stack.pop()
        self._jmp(_v_to_pop)

    def _out(self, arg1):
        if self.str_buffer is None:
            self.str_buffer = chr(arg1)
        else:
            self.str_buffer += chr(arg1)
        self.current_element += 2

    def _in(self):
        pass

    def _noop(self):
        self.current_element += 1


vm = VM()
vm.load_data('challenge.bin')
vm.execute()

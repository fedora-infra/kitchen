import unittest
from nose.plugins.skip import SkipTest
from kitchen.pycompat27.subprocess import _subprocess as subprocess
import sys
import StringIO
import signal
import os
import errno
import tempfile
import time
import re
# Not available on python2.6 or less
#import sysconfig

mswindows = (sys.platform == "win32")

#
# Depends on the following external programs: Python
#

if mswindows:
    SETBINARY = ('import msvcrt; msvcrt.setmode(sys.stdout.fileno(), '
                                                'os.O_BINARY);')
else:
    SETBINARY = ''

def reap_children():
    """Use this function at the end of test_main() whenever sub-processes
    are started.  This will help ensure that no extra children (zombies)
    stick around to hog resources and create problems when looking
    for refleaks.
    """

    # Reap all our dead child processes so we don't leave zombies around.
    # These hog resources and might be causing some of the buildbots to die.
    if hasattr(os, 'waitpid'):
        any_process = -1
        while True:
            try:
                # This will raise an exception on Windows.  That's ok.
                pid, status = os.waitpid(any_process, os.WNOHANG)
                if pid == 0:
                    break
            except:
                break

test_support = None
try:
    from test import test_support
    if not hasattr(test_support, 'reap_children'):
        # No reap_children in python-2.3
        test_support.reap_children = reap_children
except ImportError:
    pass

# In a debug build, stuff like "[6580 refs]" is printed to stderr at
# shutdown time.  That frustrates tests trying to check stderr produced
# from a spawned Python process.
def remove_stderr_debug_decorations(stderr):
    return re.sub(r"\[\d+ refs\]\r?\n?$", "", stderr)

try:
    mkstemp = tempfile.mkstemp
except AttributeError:
    # tempfile.mkstemp is not available
    def mkstemp():
        """Replacement for mkstemp, calling mktemp."""
        fname = tempfile.mktemp()
        return os.open(fname, os.O_RDWR|os.O_CREAT), fname


class BaseTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        if not hasattr(self, '_cleanups'):
            self._cleanups = []
        if not hasattr(self, 'addCleanup'):
            self.addCleanup = self._addCleanup

    def _addCleanup(self, function, *args, **kwargs):
        self._cleanups.append((function, args, kwargs))

    def setUp(self):
        # Try to minimize the number of children we have so this test
        # doesn't crash on some buildbots (Alphas in particular).
        if test_support:
            test_support.reap_children()

    def tearDown(self):
        for inst in subprocess._active:
            inst.wait()
        subprocess._cleanup()
        # assertFalse is not available in python-2.3
        self.failIf(subprocess._active, "subprocess._active not empty")

        if not hasattr(self, 'doCleanups'):
            ok = True
            while self._cleanups:
                function, args, kwargs = self._cleanups.pop(-1)
                try:
                    function(*args, **kwargs)
                except Exception:
                    ok = False

    def assertStderrEqual(self, stderr, expected, msg=None):
        # In a debug build, stuff like "[6580 refs]" is printed to stderr at
        # shutdown time.  That frustrates tests trying to check stderr produced
        # from a spawned Python process.
        actual = re.sub(r"\[\d+ refs\]\r?\n?$", "", stderr)
        self.assertEqual(actual, expected, msg)


class ProcessTestCase(BaseTestCase):

    def test_call_seq(self):
        # call() function with sequence argument
        rc = subprocess.call([sys.executable, "-c",
                              "import sys; sys.exit(47)"])
        self.assertEqual(rc, 47)

    def test_check_call_zero(self):
        # check_call() function with zero return code
        rc = subprocess.check_call([sys.executable, "-c",
                                    "import sys; sys.exit(0)"])
        self.assertEqual(rc, 0)

    def test_check_call_nonzero(self):
        # check_call() function with non-zero return code
        #with self.assertRaises(subprocess.CalledProcessError) as c:
        try:
            subprocess.check_call([sys.executable, "-c",
                                   "import sys; sys.exit(47)"])
        #self.assertEqual(c.exception.returncode, 47)
        except subprocess.CalledProcessError, e:
            self.assertEqual(e.returncode, 47)
        else:
            self.fail("Expected CalledProcessError")

    def test_check_output(self):
        # check_output() function with zero return code
        output = subprocess.check_output(
                [sys.executable, "-c", "print 'BDFL'"])
        #self.assertIn('BDFL', output)
        self.assert_('BDFL' in output)

    def test_check_output_nonzero(self):
        # check_call() function with non-zero return code
        #with self.assertRaises(subprocess.CalledProcessError) as c:
        try:
            subprocess.check_output(
                    [sys.executable, "-c", "import sys; sys.exit(5)"])
        #self.assertEqual(c.exception.returncode, 5)
        except subprocess.CalledProcessError, e:
            self.assertEqual(e.returncode, 5)
        else:
            self.fail("Expected CalledProcessError")

    def test_check_output_stderr(self):
        # check_output() function stderr redirected to stdout
        output = subprocess.check_output(
                [sys.executable, "-c", "import sys; sys.stderr.write('BDFL')"],
                stderr=subprocess.STDOUT)
        #self.assertIn('BDFL', output)
        self.assert_('BDFL' in output)

    def test_check_output_stdout_arg(self):
        # check_output() function stderr redirected to stdout
        #with self.assertRaises(ValueError) as c:
        try:
            output = subprocess.check_output(
                    [sys.executable, "-c", "print 'will not be run'"],
                    stdout=sys.stdout)
            #self.fail("Expected ValueError when stdout arg supplied.")
        #self.assertIn('stdout', c.exception.args[0])
        except ValueError, e:
            #self.assertIn('stdout', e.args[0])
            self.assert_('stdout' in e.args[0])
        else:
            self.fail("Expected ValueError when stdout arg supplied.")

    def test_call_kwargs(self):
        # call() function with keyword args
        newenv = os.environ.copy()
        newenv["FRUIT"] = "banana"
        rc = subprocess.call([sys.executable, "-c",
                              'import sys, os;'
                              'sys.exit(os.getenv("FRUIT")=="banana")'],
                             env=newenv)
        self.assertEqual(rc, 1)

    def test_invalid_args(self):
        # Popen() called with invalid arguments should raise TypeError
        # but Popen.__del__ should not complain (issue #12085)
        #with test_support.captured_stderr() as s:
        orig_stderr = getattr(sys, 'stderr')
        setattr(sys, 'stderr', StringIO.StringIO())
        s = sys.stderr
        try:
            try:
                subprocess.Popen(invalid_arg_name=1)
            except TypeError:
                pass
            except:
                self.fail("Expected TypeError")
            else:
                self.fail("Expected TypeError")
            argcount = subprocess.Popen.__init__.func_code.co_argcount
            too_many_args = [0] * (argcount + 1)
            try:
                subprocess.Popen(*too_many_args)
            except TypeError:
                pass
            except:
                self.fail("Expected TypeError")
            else:
                self.fail("Expected TypeError")
        finally:
            setattr(sys, 'stderr', orig_stderr)
        self.assertEqual(s.getvalue(), '')

    def test_stdin_none(self):
        # .stdin is None when not redirected
        p = subprocess.Popen([sys.executable, "-c", 'print "banana"'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        p.wait()
        self.assertEqual(p.stdin, None)

    def test_stdout_none(self):
        # .stdout is None when not redirected
        p = subprocess.Popen([sys.executable, "-c",
                             'print "    this bit of output is from a '
                             'test of stdout in a different '
                             'process ..."'],
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        self.addCleanup(p.stderr.close)
        p.wait()
        self.assertEqual(p.stdout, None)

    def test_stderr_none(self):
        # .stderr is None when not redirected
        p = subprocess.Popen([sys.executable, "-c", 'print "banana"'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stdin.close)
        p.wait()
        self.assertEqual(p.stderr, None)

    def test_executable_with_cwd(self):
        python_dir = os.path.dirname(os.path.realpath(sys.executable))
        p = subprocess.Popen(["somethingyoudonthave", "-c",
                              "import sys; sys.exit(47)"],
                             executable=sys.executable, cwd=python_dir)
        p.wait()
        self.assertEqual(p.returncode, 47)

    # Not available on python2.3 and we know we're not building python itself
    #@unittest.skipIf(sysconfig.is_python_build(),
    #                 "need an installed Python. See #7774")
    def test_executable_without_cwd(self):
        # For a normal installation, it should work without 'cwd'
        # argument.  For test runs in the build directory, see #7774.
        p = subprocess.Popen(["somethingyoudonthave", "-c",
                              "import sys; sys.exit(47)"],
                             executable=sys.executable)
        p.wait()
        self.assertEqual(p.returncode, 47)

    def test_stdin_pipe(self):
        # stdin redirection
        p = subprocess.Popen([sys.executable, "-c",
                         'import sys; sys.exit(sys.stdin.read() == "pear")'],
                        stdin=subprocess.PIPE)
        p.stdin.write("pear")
        p.stdin.close()
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdin_filedes(self):
        # stdin is set to open file descriptor
        tf = tempfile.TemporaryFile()
        d = tf.fileno()
        os.write(d, "pear")
        os.lseek(d, 0, 0)
        p = subprocess.Popen([sys.executable, "-c",
                         'import sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=d)
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdin_fileobj(self):
        # stdin is set to open file object
        tf = tempfile.TemporaryFile()
        tf.write("pear")
        tf.seek(0)
        p = subprocess.Popen([sys.executable, "-c",
                         'import sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=tf)
        p.wait()
        self.assertEqual(p.returncode, 1)

    def test_stdout_pipe(self):
        # stdout redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stdout.write("orange")'],
                         stdout=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read(), "orange")

    def test_stdout_filedes(self):
        # stdout is set to open file descriptor
        tf = tempfile.TemporaryFile()
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stdout.write("orange")'],
                         stdout=d)
        p.wait()
        os.lseek(d, 0, 0)
        self.assertEqual(os.read(d, 1024), "orange")

    def test_stdout_fileobj(self):
        # stdout is set to open file object
        tf = tempfile.TemporaryFile()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stdout.write("orange")'],
                         stdout=tf)
        p.wait()
        tf.seek(0)
        self.assertEqual(tf.read(), "orange")

    def test_stderr_pipe(self):
        # stderr redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stderr.write("strawberry")'],
                         stderr=subprocess.PIPE)
        self.addCleanup(p.stderr.close)
        #self.assertStderrEqual(p.stderr.read(), "strawberry")
        self.assertEqual(remove_stderr_debug_decorations(p.stderr.read()),
                         "strawberry")

    def test_stderr_filedes(self):
        # stderr is set to open file descriptor
        tf = tempfile.TemporaryFile()
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stderr.write("strawberry")'],
                         stderr=d)
        p.wait()
        os.lseek(d, 0, 0)
        #self.assertStderrEqual(os.read(d, 1024), "strawberry")
        self.assertEqual(remove_stderr_debug_decorations(os.read(d, 1024)),
                         "strawberry")

    def test_stderr_fileobj(self):
        # stderr is set to open file object
        tf = tempfile.TemporaryFile()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys; sys.stderr.write("strawberry")'],
                         stderr=tf)
        p.wait()
        tf.seek(0)
        #self.assertStderrEqual(tf.read(), "strawberry")
        self.assertEqual(remove_stderr_debug_decorations(tf.read()),
                         "strawberry")

    def test_stdout_stderr_pipe(self):
        # capture stdout and stderr to the same pipe
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys;'
                          'sys.stdout.write("apple");'
                          'sys.stdout.flush();'
                          'sys.stderr.write("orange")'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        self.addCleanup(p.stdout.close)
        #self.assertStderrEqual(p.stdout.read(), "appleorange")
        output = p.stdout.read()
        stripped = remove_stderr_debug_decorations(output)
        self.assertEqual(stripped, "appleorange")

    def test_stdout_stderr_file(self):
        # capture stdout and stderr to the same open file
        tf = tempfile.TemporaryFile()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys;'
                          'sys.stdout.write("apple");'
                          'sys.stdout.flush();'
                          'sys.stderr.write("orange")'],
                         stdout=tf,
                         stderr=tf)
        p.wait()
        tf.seek(0)
        #self.assertStderrEqual(tf.read(), "appleorange")
        output = tf.read()
        stripped = remove_stderr_debug_decorations(output)
        self.assertEqual(stripped, "appleorange")

    def test_stdout_filedes_of_stdout(self):
        # stdout is set to 1 (#1531862).
        cmd = r"import sys, os; sys.exit(os.write(sys.stdout.fileno(), '.\n'))"
        rc = subprocess.call([sys.executable, "-c", cmd], stdout=1)
        self.assertEqual(rc, 2)

    def test_cwd(self):
        tmpdir = tempfile.gettempdir()
        # We cannot use os.path.realpath to canonicalize the path,
        # since it doesn't expand Tru64 {memb} strings. See bug 1063571.
        cwd = os.getcwd()
        os.chdir(tmpdir)
        tmpdir = os.getcwd()
        os.chdir(cwd)
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;'
                          'sys.stdout.write(os.getcwd())'],
                         stdout=subprocess.PIPE,
                         cwd=tmpdir)
        self.addCleanup(p.stdout.close)
        normcase = os.path.normcase
        self.assertEqual(normcase(p.stdout.read()), normcase(tmpdir))

    def test_env(self):
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange"
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;'
                          'sys.stdout.write(os.getenv("FRUIT"))'],
                         stdout=subprocess.PIPE,
                         env=newenv)
        self.assertEqual(p.stdout.read(), "orange")

    def test_communicate_stdin(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'import sys;'
                              'sys.exit(sys.stdin.read() == "pear")'],
                             stdin=subprocess.PIPE)
        p.communicate("pear")
        self.assertEqual(p.returncode, 1)

    def test_communicate_stdout(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'import sys; sys.stdout.write("pineapple")'],
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, "pineapple")
        self.assertEqual(stderr, None)

    def test_communicate_stderr(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'import sys; sys.stderr.write("pineapple")'],
                             stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, None)
        #self.assertStderrEqual(stderr, "pineapple")
        self.assertEqual(remove_stderr_debug_decorations(stderr), "pineapple")

    def test_communicate(self):
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;'
                          'sys.stderr.write("pineapple");'
                          'sys.stdout.write(sys.stdin.read())'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        (stdout, stderr) = p.communicate("banana")
        self.assertEqual(stdout, "banana")
        #self.assertStderrEqual(stderr, "pineapple")
        self.assertEqual(remove_stderr_debug_decorations(stderr),
                         "pineapple")

    # Not available with python-2.6's unittest:  Reimplement by
    # raising SkipTest from nose
    # This test is Linux specific for simplicity to at least have
    # some coverage.  It is not a platform specific bug.
    #@unittest.skipUnless(os.path.isdir('/proc/%d/fd' % os.getpid()),
    #                     "Linux specific")
    # Test for the fd leak reported in http://bugs.python.org/issue2791.
    def test_communicate_pipe_fd_leak(self):
        if not os.path.isdir('/proc/%d/fd' % os.getpid()):
            raise SkipTest('Linux specific')
        fd_directory = '/proc/%d/fd' % os.getpid()
        num_fds_before_popen = len(os.listdir(fd_directory))
        p = subprocess.Popen([sys.executable, "-c", "print()"],
                             stdout=subprocess.PIPE)
        p.communicate()
        num_fds_after_communicate = len(os.listdir(fd_directory))
        del p
        num_fds_after_destruction = len(os.listdir(fd_directory))
        self.assertEqual(num_fds_before_popen, num_fds_after_destruction)
        self.assertEqual(num_fds_before_popen, num_fds_after_communicate)

    def test_communicate_returns(self):
        # communicate() should return None if no redirection is active
        p = subprocess.Popen([sys.executable, "-c",
                              "import sys; sys.exit(47)"])
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, None)
        self.assertEqual(stderr, None)

    def test_communicate_pipe_buf(self):
        # communicate() with writes larger than pipe_buf
        # This test will probably deadlock rather than fail, if
        # communicate() does not work properly.
        x, y = os.pipe()
        if mswindows:
            pipe_buf = 512
        else:
            pipe_buf = os.fpathconf(x, "PC_PIPE_BUF")
        os.close(x)
        os.close(y)
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;'
                          'sys.stdout.write(sys.stdin.read(47));'
                          'sys.stderr.write("xyz"*%d);'
                          'sys.stdout.write(sys.stdin.read())' % pipe_buf],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        string_to_write = "abc"*pipe_buf
        (stdout, stderr) = p.communicate(string_to_write)
        self.assertEqual(stdout, string_to_write)

    def test_writes_before_communicate(self):
        # stdin.write before communicate()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;'
                          'sys.stdout.write(sys.stdin.read())'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.stdin.write("banana")
        (stdout, stderr) = p.communicate("split")
        self.assertEqual(stdout, "bananasplit")
        #self.assertStderrEqual(stderr, "")
        self.assertEqual(remove_stderr_debug_decorations(stderr), "")

    def test_universal_newlines(self):
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;' + SETBINARY +
                          'sys.stdout.write("line1\\n");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line2\\r");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line3\\r\\n");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line4\\r");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("\\nline5");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("\\nline6");'],
                         stdout=subprocess.PIPE,
                         universal_newlines=1)
        self.addCleanup(p.stdout.close)
        stdout = p.stdout.read()
        if hasattr(file, 'newlines'):
            # Interpreter with universal newline support
            self.assertEqual(stdout,
                             "line1\nline2\nline3\nline4\nline5\nline6")
        else:
            # Interpreter without universal newline support
            self.assertEqual(stdout,
                             "line1\nline2\rline3\r\nline4\r\nline5\nline6")

    def test_universal_newlines_communicate(self):
        # universal newlines through communicate()
        p = subprocess.Popen([sys.executable, "-c",
                          'import sys,os;' + SETBINARY +
                          'sys.stdout.write("line1\\n");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line2\\r");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line3\\r\\n");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("line4\\r");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("\\nline5");'
                          'sys.stdout.flush();'
                          'sys.stdout.write("\\nline6");'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=1)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        (stdout, stderr) = p.communicate()
        if hasattr(file, 'newlines'):
            # Interpreter with universal newline support
            self.assertEqual(stdout,
                             "line1\nline2\nline3\nline4\nline5\nline6")
        else:
            # Interpreter without universal newline support
            self.assertEqual(stdout,
                             "line1\nline2\rline3\r\nline4\r\nline5\nline6")

    def test_no_leaking(self):
        if not test_support:
            raise SkipTest("No test_support module available.")

        # Make sure we leak no resources
        if not mswindows:
            max_handles = 1026 # too much for most UNIX systems
        else:
            max_handles = 2050 # too much for (at least some) Windows setups
        handles = []
        try:
            for i in range(max_handles):
                try:
                    handles.append(os.open(test_support.TESTFN,
                                           os.O_WRONLY | os.O_CREAT))
                except OSError, e:
                    if e.errno != errno.EMFILE:
                        raise
                    break
            else:
                # python-2.3  unittest doesn't have skipTest.  Reimplement with nose
                #self.skipTest("failed to reach the file descriptor limit "
                #    "(tried %d)" % max_handles)
                raise SkipTest("failed to reach the file descriptor limit "
                    "(tried %d)" % max_handles)

            # Close a couple of them (should be enough for a subprocess)
            for i in range(10):
                os.close(handles.pop())
            # Loop creating some subprocesses. If one of them leaks some fds,
            # the next loop iteration will fail by reaching the max fd limit.
            for i in range(15):
                p = subprocess.Popen([sys.executable, "-c",
                                      "import sys;"
                                      "sys.stdout.write(sys.stdin.read())"],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                data = p.communicate("lime")[0]
                self.assertEqual(data, "lime")
        finally:
            for h in handles:
                os.close(h)

    def test_list2cmdline(self):
        self.assertEqual(subprocess.list2cmdline(['a b c', 'd', 'e']),
                         '"a b c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab"c', '\\', 'd']),
                         'ab\\"c \\ d')
        self.assertEqual(subprocess.list2cmdline(['ab"c', ' \\', 'd']),
                         'ab\\"c " \\\\" d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\\\b', 'de fg', 'h']),
                         'a\\\\\\b "de fg" h')
        self.assertEqual(subprocess.list2cmdline(['a\\"b', 'c', 'd']),
                         'a\\\\\\"b c d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b c', 'd', 'e']),
                         '"a\\\\b c" d e')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b\\ c', 'd', 'e']),
                         '"a\\\\b\\ c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab', '']),
                         'ab ""')


    def test_poll(self):
        p = subprocess.Popen([sys.executable,
                          "-c", "import time; time.sleep(1)"])
        count = 0
        while p.poll() is None:
            time.sleep(0.1)
            count += 1
        # We expect that the poll loop probably went around about 10 times,
        # but, based on system scheduling we can't control, it's possible
        # poll() never returned None.  It "should be" very rare that it
        # didn't go around at least twice.
        #self.assertGreaterEqual(count, 2)
        self.assert_(count >= 2)
        # Subsequent invocations should just return the returncode
        self.assertEqual(p.poll(), 0)


    def test_wait(self):
        p = subprocess.Popen([sys.executable,
                          "-c", "import time; time.sleep(2)"])
        self.assertEqual(p.wait(), 0)
        # Subsequent invocations should just return the returncode
        self.assertEqual(p.wait(), 0)


    def test_invalid_bufsize(self):
        # an invalid type of the bufsize argument should raise
        # TypeError.
        #with self.assertRaises(TypeError):
        try:
            subprocess.Popen([sys.executable, "-c", "pass"], "orange")
        except TypeError:
            pass
        else:
            self.fail("Expected TypeError")

    def test_leaking_fds_on_error(self):
        # see bug #5179: Popen leaks file descriptors to PIPEs if
        # the child fails to execute; this will eventually exhaust
        # the maximum number of open fds. 1024 seems a very common
        # value for that limit, but Windows has 2048, so we loop
        # 1024 times (each call leaked two fds).
        for i in range(1024):
            # Windows raises IOError.  Others raise OSError.
            #with self.assertRaises(EnvironmentError) as c:
            try:
                subprocess.Popen(['nonexisting_i_hope'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            #if c.exception.errno != 2:  # ignore "no such file"
            #    raise c.exception
            # Windows raises IOError
            except EnvironmentError, err:
                if err.errno not in (errno.ENOENT, errno.EACCES):  # ignore "no such file"
                    raise err
            except:
                self.fail("Expected EnvironmentError")
            else:
                self.fail("Expected EnvironmentError")

    def test_handles_closed_on_exception(self):
        # If CreateProcess exits with an error, ensure the
        # duplicate output handles are released
        ifhandle, ifname = mkstemp()
        ofhandle, ofname = mkstemp()
        efhandle, efname = mkstemp()
        try:
            subprocess.Popen(["*"], stdin=ifhandle, stdout=ofhandle,
              stderr=efhandle)
        except OSError:
            os.close(ifhandle)
            os.remove(ifname)
            os.close(ofhandle)
            os.remove(ofname)
            os.close(efhandle)
            os.remove(efname)
        self.assert_(not os.path.exists(ifname))
        self.assert_(not os.path.exists(ofname))
        self.assert_(not os.path.exists(efname))

    def test_communicate_epipe(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pass'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.communicate("x" * 2**20)

    def test_communicate_epipe_only_stdin(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pass'],
                             stdin=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        time.sleep(2)
        p.communicate("x" * 2**20)

# context manager
class _SuppressCoreFiles(object):
    """Try to prevent core files from being created."""
    old_limit = None

    def __enter__(self):
        """Try to save previous ulimit, then set it to (0, 0)."""
        try:
            import resource
            self.old_limit = resource.getrlimit(resource.RLIMIT_CORE)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except (ImportError, ValueError, resource.error):
            pass

        if sys.platform == 'darwin':
            # Check if the 'Crash Reporter' on OSX was configured
            # in 'Developer' mode and warn that it will get triggered
            # when it is.
            #
            # This assumes that this context manager is used in tests
            # that might trigger the next manager.
            value = subprocess.Popen(['/usr/bin/defaults', 'read',
                    'com.apple.CrashReporter', 'DialogType'],
                    stdout=subprocess.PIPE).communicate()[0]
            if value.strip() == 'developer':
                print "this tests triggers the Crash Reporter, that is intentional"
                sys.stdout.flush()

    def __exit__(self, *args):
        """Return core file behavior to default."""
        if self.old_limit is None:
            return
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CORE, self.old_limit)
        except (ImportError, ValueError, resource.error):
            pass

    # python-2.3 unittest doesn't have skipUnless.  Reimplement as SkipTest from nose
    #@unittest.skipUnless(hasattr(signal, 'SIGALRM'),
    #                     "Requires signal.SIGALRM")
    def test_communicate_eintr(self):
        if not hasattr(signal, 'SIGALRM'):
            raise SkipTest('Requires signal.SIGALRM')
        # Issue #12493: communicate() should handle EINTR
        def handler(signum, frame):
            pass
        old_handler = signal.signal(signal.SIGALRM, handler)
        self.addCleanup(signal.signal, signal.SIGALRM, old_handler)

        # the process is running for 2 seconds
        args = [sys.executable, "-c", 'import time; time.sleep(2)']
        for stream in ('stdout', 'stderr'):
            kw = {stream: subprocess.PIPE}
            #with subprocess.Popen(args, **kw) as process:
            try:
                process = subprocess.Popen(args, **kw)
                signal.alarm(1)
                # communicate() will be interrupted by SIGALRM
                process.communicate()
            finally:
                process.close()


# Not available with python-2.3's unittest.  Reimplement with SkipTest from
# nose
#@unittest.skipIf(mswindows, "POSIX specific tests")
class POSIXProcessTestCase(BaseTestCase):
    def setUp(self):
        if mswindows:
            raise SkipTest('POSIX specific tests')

    def test_exceptions(self):
        # caught & re-raised exceptions
        #with self.assertRaises(OSError) as c:
        try:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 cwd="/this/path/does/not/exist")
        # The attribute child_traceback should contain "os.chdir" somewhere.
        #self.assertIn("os.chdir", c.exception.child_traceback)
        except OSError, e:
            self.assertNotEqual(e.child_traceback.find("os.chdir"), -1)
        except:
            self.fail("Expected OSError")
        else:
            self.fail("Expected OSError")

    def _suppress_core_files(self):
        """Try to prevent core files from being created.
        Returns previous ulimit if successful, else None.
        """
        try:
            import resource
            old_limit = resource.getrlimit(resource.RLIMIT_CORE)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            return old_limit
        except (ImportError, ValueError, resource.error):
            return None

    def _unsuppress_core_files(self, old_limit):
        """Return core file behavior to default."""
        if old_limit is None:
            return
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CORE, old_limit)
        except (ImportError, ValueError, resource.error):
            return

    def test_run_abort(self):
        # returncode handles signal termination
        #with _SuppressCoreFiles():
        old_limit = self._suppress_core_files()
        try:
            p = subprocess.Popen([sys.executable, "-c",
                                  "import os; os.abort()"])
        finally:
            self._unsuppress_core_files(old_limit)

            #p.wait()
        p.wait()
        self.assertEqual(-p.returncode, signal.SIGABRT)

    def test_preexec(self):
        # preexec function
        p = subprocess.Popen([sys.executable, "-c",
                              "import sys, os;"
                              "sys.stdout.write(os.getenv('FRUIT'))"],
                             stdout=subprocess.PIPE,
                             preexec_fn=lambda: os.putenv("FRUIT", "apple"))
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read(), "apple")

    def test_args_string(self):
        # args is a string
        f, fname = mkstemp()
        os.write(f, "#!/bin/sh\n")
        os.write(f, "exec '%s' -c 'import sys; sys.exit(47)'\n" %
                    sys.executable)
        os.close(f)
        # 0o is not available in python2.5
        #os.chmod(fname, 0o700)
        os.chmod(fname, 0700)
        p = subprocess.Popen(fname)
        p.wait()
        os.remove(fname)
        self.assertEqual(p.returncode, 47)

    def test_invalid_args(self):
        # invalid arguments should raise ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "import sys; sys.exit(47)"],
                          startupinfo=47)
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "import sys; sys.exit(47)"],
                          creationflags=47)

    def test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen(["echo $FRUIT"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read().strip(), "apple")

    def test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen("echo $FRUIT", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        self.assertEqual(p.stdout.read().strip(), "apple")

    def test_call_string(self):
        # call() function with string argument on UNIX
        f, fname = mkstemp()
        os.write(f, "#!/bin/sh\n")
        os.write(f, "exec '%s' -c 'import sys; sys.exit(47)'\n" %
                    sys.executable)
        os.close(f)
        os.chmod(fname, 0700)
        rc = subprocess.call(fname)
        os.remove(fname)
        self.assertEqual(rc, 47)

    def test_specific_shell(self):
        # Issue #9265: Incorrect name passed as arg[0].
        shells = []
        for prefix in ['/bin', '/usr/bin/', '/usr/local/bin']:
            for name in ['bash', 'ksh']:
                sh = os.path.join(prefix, name)
                if os.path.isfile(sh):
                    shells.append(sh)
        if not shells: # Will probably work for any shell but csh.

            # skipTest unavailable on python<2.7 reimplement with nose
            #self.skipTest("bash or ksh required for this test")
            raise SkipTest("bash or ksh required for this test")
        sh = '/bin/sh'
        if os.path.isfile(sh) and not os.path.islink(sh):
            # Test will fail if /bin/sh is a symlink to csh.
            shells.append(sh)
        for sh in shells:
            p = subprocess.Popen("echo $0", executable=sh, shell=True,
                                 stdout=subprocess.PIPE)
            self.addCleanup(p.stdout.close)
            self.assertEqual(p.stdout.read().strip(), sh)

    def _kill_process(self, method, *args):
        # Do not inherit file handles from the parent.
        # It should fix failures on some platforms.
        p = subprocess.Popen([sys.executable, "-c", """if 1:
                             import sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             time.sleep(30)
                             """],
                             close_fds=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # Wait for the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        getattr(p, method)(*args)
        return p

    # These are still hanging with x86_64 Fedora 12 (python-2.6)  subprocess
    # backport from current trunk run under nosetests

    def test_send_signal(self):
        #if hang DISABLED #2777
        p = self._kill_process('send_signal', signal.SIGINT)
        _, stderr = p.communicate()
        self.assert_('KeyboardInterrupt' in stderr)
        self.assertNotEqual(p.wait(), 0)

    def test_kill(self):
        #if hang DISABLED #2777
        p = self._kill_process('kill')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, '')
        self.assertEqual(p.wait(), -signal.SIGKILL)

    def test_terminate(self):
        #if hang DISABLED #2777
        p = self._kill_process('terminate')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, '')
        self.assertEqual(p.wait(), -signal.SIGTERM)

    def check_close_std_fds(self, fds):
        # Issue #9905: test that subprocess pipes still work properly with
        # some standard fds closed
        stdin = 0
        newfds = []
        for a in fds:
            b = os.dup(a)
            newfds.append(b)
            if a == 0:
                stdin = b
        try:
            for fd in fds:
                os.close(fd)
            out, err = subprocess.Popen([sys.executable, "-c",
                              'import sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                       stdin=stdin,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE).communicate()
            err = re.sub(r"\[\d+ refs\]\r?\n?$", "", err).strip()
            self.assertEqual((out, err), ('apple', 'orange'))
        finally:
            for b, a in zip(newfds, fds):
                os.dup2(b, a)
            for b in newfds:
                os.close(b)

    def test_close_fd_0(self):
        self.check_close_std_fds([0])

    def test_close_fd_1(self):
        self.check_close_std_fds([1])

    def test_close_fd_2(self):
        self.check_close_std_fds([2])

    def test_close_fds_0_1(self):
        self.check_close_std_fds([0, 1])

    def test_close_fds_0_2(self):
        self.check_close_std_fds([0, 2])

    def test_close_fds_1_2(self):
        self.check_close_std_fds([1, 2])

    def test_close_fds_0_1_2(self):
        # Issue #10806: test that subprocess pipes still work properly with
        # all standard fds closed.
        self.check_close_std_fds([0, 1, 2])

    def check_swap_fds(self, stdin_no, stdout_no, stderr_no):
        # open up some temporary files
        temps = [mkstemp() for i in range(3)]
        temp_fds = [fd for fd, fname in temps]
        try:
            # unlink the files -- we won't need to reopen them
            for fd, fname in temps:
                os.unlink(fname)

            # save a copy of the standard file descriptors
            saved_fds = [os.dup(fd) for fd in range(3)]
            try:
                # duplicate the temp files over the standard fd's 0, 1, 2
                for fd, temp_fd in enumerate(temp_fds):
                    os.dup2(temp_fd, fd)

                # write some data to what will become stdin, and rewind
                os.write(stdin_no, "STDIN")
                os.lseek(stdin_no, 0, 0)

                # now use those files in the given order, so that subprocess
                # has to rearrange them in the child
                p = subprocess.Popen([sys.executable, "-c",
                    'import sys; got = sys.stdin.read();'
                    'sys.stdout.write("got %s"%got); sys.stderr.write("err")'],
                    stdin=stdin_no,
                    stdout=stdout_no,
                    stderr=stderr_no)
                p.wait()

                for fd in temp_fds:
                    os.lseek(fd, 0, 0)

                out = os.read(stdout_no, 1024)
                err = re.sub(r"\[\d+ refs\]\r?\n?$", "", os.read(stderr_no, 1024)).strip()
            finally:
                for std, saved in enumerate(saved_fds):
                    os.dup2(saved, std)
                    os.close(saved)

            self.assertEqual(out, "got STDIN")
            self.assertEqual(err, "err")

        finally:
            for fd in temp_fds:
                os.close(fd)

    # When duping fds, if there arises a situation where one of the fds is
    # either 0, 1 or 2, it is possible that it is overwritten (#12607).
    # This tests all combinations of this.
    def test_swap_fds(self):
        self.check_swap_fds(0, 1, 2)
        self.check_swap_fds(0, 2, 1)
        self.check_swap_fds(1, 0, 2)
        self.check_swap_fds(1, 2, 0)
        self.check_swap_fds(2, 0, 1)
        self.check_swap_fds(2, 1, 0)

    def test_wait_when_sigchild_ignored(self):
        # NOTE: sigchild_ignore.py may not be an effective test on all OSes.
        if not test_support:
            raise SkipTest("No test_support module available.")
        sigchild_ignore = test_support.findfile(os.path.join("subprocessdata",
            "sigchild_ignore.py"))
        p = subprocess.Popen([sys.executable, sigchild_ignore],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        self.assertEqual(0, p.returncode, "sigchild_ignore.py exited"
                         " non-zero with this error:\n%s" % stderr)


    def test_zombie_fast_process_del(self):
        # Issue #12650: on Unix, if Popen.__del__() was called before the
        # process exited, it wouldn't be added to subprocess._active, and would
        # remain a zombie.
        # spawn a Popen, and delete its reference before it exits
        p = subprocess.Popen([sys.executable, "-c",
                              'import sys, time;'
                              'time.sleep(0.2)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        del p
        # check that p is in the active processes list
        # assertIn not in python< 2.7
        #self.assertIn(ident, [id(o) for o in subprocess._active])
        self.assert_(ident in [id(o) for o in subprocess._active])

    def test_leak_fast_process_del_killed(self):
        # Issue #12650: on Unix, if Popen.__del__() was called before the
        # process exited, and the process got killed by a signal, it would never
        # be removed from subprocess._active, which triggered a FD and memory
        # leak.
        # spawn a Popen, delete its reference and kill it
        p = subprocess.Popen([sys.executable, "-c",
                              'import time;'
                              'time.sleep(3)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        del p
        os.kill(pid, signal.SIGKILL)
        # check that p is in the active processes list
        # assertIn not in python < 2.7
        self.assert_(ident in [id(o) for o in subprocess._active])
        #self.assertIn(ident, [id(o) for o in subprocess._active])

        # let some time for the process to exit, and create a new Popen: this
        # should trigger the wait() of p
        time.sleep(0.2)
        #with self.assertRaises(EnvironmentError) as c:
        try:
            try:
                proc = subprocess.Popen(['nonexisting_i_hope'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            finally:
                pass
        except EnvironmentError:
            pass
        except:
            self.fail('Expected EnvironmentError')
        else:
            self.fail('Expected EnvironmentError')
        # p should have been wait()ed on, and removed from the _active list
        #self.assertRaises(OSError, os.waitpid, pid, 0)
        try:
            os.waitpid(pid, 0)
        except OSError:
            pass
        except:
            self.fail('Expected OSError')
        else:
            self.fail('Expected OSError')
        #self.assertNotIn(ident, [id(o) for o in subprocess._active])
        self.assert_(ident not in [id(o) for o in subprocess._active])

    def test_pipe_cloexec(self):
        # Issue 12786: check that the communication pipes' FDs are set CLOEXEC,
        # and are not inherited by another child process.
        p1 = subprocess.Popen([sys.executable, "-c",
                               'import os;'
                               'os.read(0, 1)'
                              ],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        p2 = subprocess.Popen([sys.executable, "-c", """if True:
                               import os, errno, sys
                               for fd in %r:
                                   try:
                                       os.close(fd)
                                   except OSError, e:
                                       if e.errno != errno.EBADF:
                                           raise
                                   else:
                                       sys.exit(1)
                               sys.exit(0)
                               """ % [f.fileno() for f in (p1.stdin, p1.stdout,
                                                           p1.stderr)]
                              ],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, close_fds=False)
        p1.communicate('foo')
        _, stderr = p2.communicate()

        self.assertEqual(p2.returncode, 0, "Unexpected error: " + repr(stderr))


# Not available with python-2.3's unittest, reimplement with SkipTest from
# nose
##@unittest.skipUnless(mswindows, "Windows specific tests")
class Win32ProcessTestCase(BaseTestCase):
    def setUp(self):
        if not mswindows:
            raise SkipTest('Windows specific tests')

    def test_startupinfo(self):
        # startupinfo argument
        # We uses hardcoded constants, because we do not want to
        # depend on win32all.
        STARTF_USESHOWWINDOW = 1
        SW_MAXIMIZE = 3
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_MAXIMIZE
        # Since Python is a console process, it won't be affected
        # by wShowWindow, but the argument should be silently
        # ignored
        subprocess.call([sys.executable, "-c", "import sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    def test_creationflags(self):
        # creationflags argument
        CREATE_NEW_CONSOLE = 16
        sys.stderr.write("    a DOS box should flash briefly ...\n")
        subprocess.call(sys.executable +
                        ' -c "import time; time.sleep(0.25)"',
                        creationflags=CREATE_NEW_CONSOLE)

    def test_invalid_args(self):
        # invalid arguments should raise ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "import sys; sys.exit(47)"],
                          preexec_fn=lambda: 1)
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "import sys; sys.exit(47)"],
                          stdout=subprocess.PIPE,
                          close_fds=True)

    def test_close_fds(self):
        # close file descriptors
        rc = subprocess.call([sys.executable, "-c",
                              "import sys; sys.exit(47)"],
                              close_fds=True)
        self.assertEqual(rc, 47)

    def test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen(["set"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        #self.assertIn("physalis", p.stdout.read())
        self.assert_("physalis" in p.stdout.read())

    def test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen("set", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        self.addCleanup(p.stdout.close)
        #self.assertIn("physalis", p.stdout.read())
        self.assert_("physalis" in p.stdout.read())

    def test_call_string(self):
        # call() function with string argument on Windows
        rc = subprocess.call(sys.executable +
                             ' -c "import sys; sys.exit(47)"')
        self.assertEqual(rc, 47)

    def _kill_process(self, method, *args):
        # Some win32 buildbot raises EOFError if stdin is inherited
        p = subprocess.Popen([sys.executable, "-c", """if 1:
                             import sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             time.sleep(30)
                             """],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        # Wait for the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        getattr(p, method)(*args)
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, '')
        returncode = p.wait()
        self.assertNotEqual(returncode, 0)

    def test_send_signal(self):
        #if hang DISABLED #2777
        self._kill_process('send_signal', signal.SIGTERM)

    def test_kill(self):
        #if hang DISABLED #2777
        self._kill_process('kill')

    def test_terminate(self):
        #if hang DISABLED #2777
        self._kill_process('terminate')


# Not available with python-2.3's unittest.  reimplement with SkipTest from
# nose
#@unittest.skipUnless(getattr(subprocess, '_has_poll', False),
#                     "poll system call not supported")
class ProcessTestCaseNoPoll(ProcessTestCase):
    def setUp(self):
        if not getattr(subprocess, '_has_poll', False):
            raise SkipTest('poll system call not supported')
        subprocess._has_poll = False
        ProcessTestCase.setUp(self)

    def tearDown(self):
        subprocess._has_poll = True
        ProcessTestCase.tearDown(self)


class HelperFunctionTests(unittest.TestCase):
    # Not available with python-2.3's unittest.  reimplement with SkipTest from
    # nose
    #@unittest.skipIf(mswindows, "errno and EINTR make no sense on windows")
    def test_eintr_retry_call(self):
        if mswindows:
            raise SkipTest('errno and EINTR make no sense on windows')
        record_calls = []
        def fake_os_func(*args):
            record_calls.append(args)
            if len(record_calls) == 2:
                raise OSError(errno.EINTR, "fake interrupted system call")
            # reversed() is not available in python-2.3
            args = list(args)
            args.reverse()
            return tuple(args)

        self.assertEqual((999, 256),
                         subprocess._eintr_retry_call(fake_os_func, 256, 999))
        self.assertEqual([(256, 999)], record_calls)
        # This time there will be an EINTR so it will loop once.
        self.assertEqual((666,),
                         subprocess._eintr_retry_call(fake_os_func, 666))
        self.assertEqual([(256, 999), (666,), (666,)], record_calls)


# SkipUnless is not available on python < 2.7, reimplement with nose
#@unittest.skipUnless(mswindows, "mswindows only")
class CommandsWithSpaces (BaseTestCase):

    def setUp(self):
        if not mswindows:
            raise SkipTest('mswindows only')

        super(CommandsWithSpaces, self).setUp()
        f, fname = mkstemp(".py", "te st")
        self.fname = fname.lower()
        os.write(f, "import sys;"
                    "sys.stdout.write('%d %s' % (len(sys.argv), [a.lower () for a in sys.argv]))"
        )
        os.close(f)

    def tearDown(self):
        os.remove(self.fname)
        super(CommandsWithSpaces, self).tearDown()

    def with_spaces(self, *args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(*args, **kwargs)
        self.addCleanup(p.stdout.close)
        self.assertEqual(
          p.stdout.read().decode("mbcs"),
          "2 [%r, 'ab cd']" % self.fname
        )

    def test_shell_string_with_spaces(self):
        # call() function with string argument with spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                                             "ab cd"), shell=1)

    def test_shell_sequence_with_spaces(self):
        # call() function with sequence argument with spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"], shell=1)

    def test_noshell_string_with_spaces(self):
        # call() function with string argument with spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                             "ab cd"))

    def test_noshell_sequence_with_spaces(self):
        # call() function with sequence argument with spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"])


# We're using nosetests so we don't need this.  This just leads to tests being
# run twice
#def test_main():
#    unit_tests = (ProcessTestCase,
#                  POSIXProcessTestCase,
#                  Win32ProcessTestCase,
#                  ProcessTestCaseNoPoll,
#                  HelperFunctionTests
#                  )
#
#    test_support.run_unittest(*unit_tests)
#    test_support.reap_children()
#
#if __name__ == "__main__":
#    test_main()

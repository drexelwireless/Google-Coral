"""
Notes:
    - use sys.executable to run strings of code
    - use args parameter to run external programs
"""



from subprocess import run, PIPE
import sys

prgm = "hello.py"
prgm2 = "for.py"
code = "print(\"Hello, World!\")"


#result = run([sys.executable, "-c", code], capture_output=True, text=True)
result = run(args=["python", "hello.py"], capture_output=True, text=True)
#print("stdout: ", result.stdout)
#print("stderr: ", result.stderr)



print(type(result))

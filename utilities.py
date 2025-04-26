import sys
status = 0

def print_status(current,total):
    progress_percent = min(100, int((current/total  ) * 100))
    mod_increment = 0
    global status
    if( (progress_percent%10 == 0) and (progress_percent > status)):
        bar = "[" + "=" * (progress_percent // 10) + " " * (10 - (progress_percent // 10)) + "]"
        print(f"\r{bar} {progress_percent}%", end="")
        print("Current Time: " + str(current))
        status += 10
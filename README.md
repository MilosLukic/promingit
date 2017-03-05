# ProMinGit
A process mining tool for analyzing git repositories.

Version 0.1

Usage: 
In your project, generate a git log file with the next command:

```git log --pretty=format:"start%n%h;%ae;%at;%cE;%ct;%d;%nstartcomment%n%s;%nend" --numstat > project_gitlog.log```

Copy the created git file to logs folder in promingit project. Run the main.py file, the result will be available in result.html file
# ProMinGit
A process mining tool for analyzing git repositories.

Programmed with python 3.5

Version 0.2 (Coming soon)

Extend the results to include history changes, graphs and extract them to a special folder.

Version 0.1

Usage: 
In your project, generate a git log file with the next command:

```git log --pretty=format:"start%n%h;%ae;%at;%cE;%ct;%d;%nstartcomment%n%s;%nend" --numstat > project_gitlog.log```

Copy the created git file to logs folder in promingit project. Run the main.py file, the result will be available in result.html file

OR

Copy the promingit folder to your GIT folder and run extraction_script.sh

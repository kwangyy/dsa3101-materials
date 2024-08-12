# dsa3101

To "install" / get the contents of this repo (we call it git pull):
1. Have a GitHub account and download git.
2. Navigate to the directory on the command line that you want to put the DSA3101 materials in.
   - The command line can be accessed via searching for the "command prompt", but I personally use a terminal on the Windows Store
   - Following instructions should be the same for both Windows and Mac
   - To go to a directory, you can use cd
   - To create a directory, you can use mkdir <filename>.
4. Type git init to initialise a repository
5. git checkout -b <branch_name> to change to a different branch. Name the branch whatever you like
6. git clone `https://github.com/kwangyy/dsa3101.git` to clone the content in here

To access Anaconda:
1. Download it, obviously. You can download it [here](https://repo.anaconda.com/miniconda/).
   - Honestly, if you want to use a later version it should be ok :) 
3. Do NOT put it on PATH, but rather put it separately
  - e.g. for me, the path for anaconda is: "C:\Users\chiak\miniconda3\Scripts"
  - type env in your search bar and you should be able to access your PATH
3. `conda install jupyter` to install jupyter notebooks. 
4. `jupyter notebooks` to access it!

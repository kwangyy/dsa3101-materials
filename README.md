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
1. Download it, obviously. You can download it [here](https://www.anaconda.com/download/success).
   - Python 3.12 is not supported for some libraries, but we will configure that shortly.
2. Run the Anaconda Prompt.
3. Run `jupyter notebooks` to make sure you can run jupyter notebooks
4. When we want to create a new environment in Anaconda, we can do that with "conda create -n test_env python=3.10.0".

The rest of the software should be quite easy :) 

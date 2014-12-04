<h1>
DeveloperTools
==============
</h1>

<h2>
Building python scripts for AEM UI developers
</h2>
Once you setup the script, on running the script from your git repository  folder it will check for the uncommited changes(does git status) and deploys it to your localinstance. This is a developer script for AEM.


Setup:

1) Clone this repository on your local machine

2)  please make sure you call it deploycq
   
   Windows: 
    Open EnvironmentalVariables and add
	deploycq="{gitlocationofbuildscript}/build.py"

   Mac:
    vi ~/.bash_profile
	export deploycq="{gitlocationofbuildscript}/build.py"
	:wq
	source ~/.bash_profile

3) Install atleast python 2.7, make sure curl is setup on your local

4) go back to the git folder of your AEM Code base, and run the script with options below


Running script Options:

1) Detects the changes on your git , and deploys your git status changes
Mac: python $deploycq
win: python %deploycq%

2) If you have done a recent pull, use can use this command. It detects  the changes happened in the last pull request and deploys them. Doesn't go back more than 1 pull request

Mac: python $deploycq -i pull
win: python %deploycq% -i pull

3) If your default is not localhost:4502

MAC: python $deploycq -s {customserverurl} -c {customcredentials}
WIN: python %deploycq% -s {customserverurl} -c {customcredentials}
 

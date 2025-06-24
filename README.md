# g2g-py
*note: Please run all commands listed below in the directory where main.py can be seen.*

Account details for testing can be found on the portfolio.

In order to run the website locally and/or on a webserver,


## For running locally

We need to work in a virtual environment to ensure all our downloaded modules are in the same spot so we can keep track of them (rather than downloading them onto your PC).

`
.venv\Scripts\activate
`

Once the virtual environment has been activated, the packages need to be installed.

`
pip install -r requirements.txt
`

In the event that the modules do not load on the computer and the IDE cannot identify the modules, please run this in the terminal.

`
python main.py
`

## For running on a webserver

The webserver needs to install the packages in the requirements.txt file using 

`
pip install -r requirements.txt
`

To host the webserver, the webserver needs to run
`
python main.py
`


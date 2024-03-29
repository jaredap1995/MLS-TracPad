# MLS-TracPad
MLS-TracPad is a data pipeline designed to process individual player and team TracPad information distributed by the MLS.

Overview: 

- The pipeline extracts ASCII Tracpad data from available MLS team APIs, preprocesses the data for storage in MongoDB, and loads the data appropriately.
- The script can be run in a Jupyter notebook or in the terminal. Any data manipulation should be done in a Jupyter Notebook.
  
Getting Started:
- These instructions will guide you through the process of setting up MLS-TracPad on your local machine for development and testing purposes.

Prerequisites: 
Before you begin, ensure you have the following installed:

- Python 3.x
- pip (Python package manager)
- Git
- MongoDB (if you're planning to run the pipeline locally)
  
Cloning the Repository: 
- To clone the repository, open your terminal and run:

bash
```
git clone https://github.com/jaredap1995/MLS-TracPad.git
cd MLS-TracPad
```


Setting Up the Virtual Environment: 
- It's recommended to use a virtual environment for Python projects. This keeps dependencies required by different projects separate. To set up a virtual environment:


```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Installing Dependencies:
- To install the required dependencies, run:


```
pip install -r requirements.txt
```

This command will install all the necessary Python packages as listed in the requirements.txt file.

Running the Program: 
- You can run the program in the terminal and follow along with the prompted commands (UI coming soon). Make sure to correctly modify your config.json before running the program:

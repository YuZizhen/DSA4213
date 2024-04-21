# DSA4213 Project
DSA4213 Natural Language Processing for Data Science

## Team member infomation
Our team comprises of 5 members:

**Huang Ruitong**: Front-end developer

**Song Xiaoya**: Back-end developer

**Sun Peizhi**: Back-end developer
    
**Yu Zizhen**: Front-end developer
    
**Zhong Haozhe**: Front-end developer

## Project name: MCQ Generator 
**Project description**: MCQ Generator is a app designed to generate MCQ questions on selected teaching materials, for assessing students’ understanding of the contents.​
## How to use
- **Generate question**: Select the chapter and the number of question want to generate. Click the `Generate Question` button and wait for the questions to be generated.
- **Select good questions**: From the generated questions, select the desired ones and click `Submit Selections` button to temporarily save them in a separate box. User may continue to generate different questions based on the same chapter or choose other chapters to generate. 
- **Delete chosen question**: Finalize the chosen question by selecting the unwanted ones and and click `Remove Selected`.
- **Output google form**: Click `Generate Google Form` and get a google form with the final set of questions.
  
![image](https://github.com/YuZizhen/DSA4213/assets/142798627/54493cc7-67a8-42ae-8c91-ac8a305fb3e5)


## Local Development
```python
python3.11 -m venv venv
./venv/bin/pip install -r requirements_current.txt
./venv/bin/app_v1/src/wave run app.py

export H2OGPT_API_TOKEN=""
export H2OGPT_URL="https://**.h2ogpt.h2o.ai"

export LOGO="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"
```

# Project Directory Structure

- `/app_v1` - Frontend directory of the project.
  - `/src` - Contains all the source code files for frontend design.
    - `app.py` - The main entry point of the application.
    - `generate_content.py` - Define layout and detail function of the app.
    - `wave_utils`
  - `/static` - Contains all the static content required by the app.
  - `LongDescription.md`
  - `README.md` - The README file provides an overview of frontend development.
- `/backend_api` - DESCRIPTION
  - `/functions` - DESCRIPTION
    - `parse_output.py`
  - `/gform` - DESCRIPTION
    - `gform_functions.py`
    - `gform_generate.py`
    - `question_format_conversion.py`
  - `/prompts_4` - DESCRIPTION
- `requirements_current.txt`
- `README.md` - The README file provides an overview of the project.


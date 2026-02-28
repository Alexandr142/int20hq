DUMAAI: PROJECT SETUP AND EXECUTION

First ensure that Python 3.10 or a newer version is installed on your system. You also need to install Ollama to serve as the local LLM engine for this project. Once Ollama is installed open your terminal and run the command ollama pull qwen3:8b to download the required model.

Download the project by cloning the GitHub repository to your local directory. Navigate into the project folder and install the required Python libraries by running the command pip install -r requirements.txt.

To run the project in standard mode start with the generation script by executing python generate.py --samples 3. This will create a synthetic dataset of customer support chats in the data folder. Next perform the quality audit by running python analyze.py --input data/dataset.json. To view the final performance metrics and accuracy scores execute python evaluate_results.py.

For a containerized setup ensure that Docker and Docker Compose are installed and running. You can initiate the entire pipeline including environment configuration by using the command docker-compose up --build. This command automatically handles the dependencies and script execution within the container environment.

Team: DumaAI
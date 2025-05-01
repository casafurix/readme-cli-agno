[34m
                                                                                                                                                
 # readme-cli-agno                                                                                                                              
                                                                                                                                                
 !(https://img.shields.io/badge/python-%3E%3D3.8-blue?style=flat)                                                                               
 !(https://img.shields.io/badge/license-MIT-green?style=flat)                                                                                   
 !(https://img.shields.io/badge/typer-%E2%9C%93-brightgreen?style=flat)                                                                         
 !(https://img.shields.io/badge/rich-%E2%9C%93-brightgreen?style=flat)                                                                          
 !(https://img.shields.io/badge/pydantic-%E2%9C%93-brightgreen?style=flat)                                                                      
                                                                                                                                                
 **Automate professional README generation for Python projects using AI.**                                                                      
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Overview                                                                                                                                    
                                                                                                                                                
 `readme-cli-agno` is a command-line tool that analyzes your Python project and automatically generates a high-quality README.md. Powered by    
 OpenAI and the agno framework, it parses your codebase, summarizes modules and functions, detects dependencies, and formats the output using   
 best practices and Markdown enhancements.                                                                                                      
                                                                                                                                                
 Whether you want to kickstart documentation on a new repo or standardize READMEs across projects, `readme-cli-agno` is your easy, automated    
 solution.                                                                                                                                      
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Features                                                                                                                                    
                                                                                                                                                
 - **Automated README Generation:** Instantly creates detailed and structured README.md files from your project.                                
 - **AI-Powered Summarization:** Leverages OpenAI's language models to summarize and explain code automatically.                                
 - **Comprehensive Parsing:** Detects modules, classes, functions, dependencies and license information.                                        
 - **Customizable Output:** Supports different output paths, preview modes, and model selection.                                                
 - **Rich Markdown Formatting:** Adds badges, tables of contents, and formatted sections for best-in-class documentation.                       
 - **Environment Variable Support:** Securely manage API keys and configurations using `.env` files.                                            
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Installation                                                                                                                                
                                                                                                                                                
 Install via pip:                                                                                                                               
                                                                                                                                                
 ```bash                                                                                                                                        
 pip install readme-cli-agno                                                                                                                    
 ```                                                                                                                                            
                                                                                                                                                
 ### Requirements                                                                                                                               
                                                                                                                                                
 - Python 3.8+                                                                                                                                  
 - Dependencies (installed automatically):                                                                                                      
   - typer==0.15.3                                                                                                                              
   - rich==14.0.0                                                                                                                               
   - pydantic==2.11.4                                                                                                                           
   - python-dotenv==1.1.0                                                                                                                       
   - agno==1.4.3                                                                                                                                
   - openai==1.76.2                                                                                                                             
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Quick Start                                                                                                                                 
                                                                                                                                                
 1. **Set Your OpenAI API Key**                                                                                                                 
                                                                                                                                                
    Create a `.env` file in your project root, and add:                                                                                         
                                                                                                                                                
    ```                                                                                                                                         
    OPENAI_API_KEY=sk-...                                                                                                                       
    ```                                                                                                                                         
                                                                                                                                                
    > *Alternatively, set it as an environment variable directly.*                                                                              
                                                                                                                                                
 2. **Run the CLI Tool**                                                                                                                        
                                                                                                                                                
    In your project directory, simply run:                                                                                                      
                                                                                                                                                
    ```bash                                                                                                                                     
    readme-cli-agno .                                                                                                                           
    ```                                                                                                                                         
                                                                                                                                                
    This will analyze your codebase and generate a `README.md` file.                                                                            
                                                                                                                                                
 3. **Preview or Customize**                                                                                                                    
                                                                                                                                                
    - Preview without writing to file:                                                                                                          
      ```bash                                                                                                                                   
      readme-cli-agno . --preview                                                                                                               
      ```                                                                                                                                       
    - Specify output file:                                                                                                                      
      ```bash                                                                                                                                   
      readme-cli-agno . --output CUSTOM_README.md                                                                                               
      ```                                                                                                                                       
    - Select model (default: gpt-3.5-turbo):                                                                                                    
      ```bash                                                                                                                                   
      readme-cli-agno . --model gpt-4                                                                                                           
      ```                                                                                                                                       
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Configuration and Environment Variables                                                                                                     
                                                                                                                                                
 `readme-cli-agno` supports both CLI options and environment variables for flexible configuration.                                              
                                                                                                                                                
 ### Environment Variables                                                                                                                      
                                                                                                                                                
 | Variable               | Description                        | Default                   |                                                    
 |------------------------|------------------------------------|---------------------------|                                                    
 | `OPENAI_API_KEY`       | Your OpenAI API key *(required)*   | -                         |                                                    
 | `OPENAI_MODEL`         | Model name for summarization       | `gpt-3.5-turbo`           |                                                    
                                                                                                                                                
 > Set these in a `.env` file or your shell environment.                                                                                        
                                                                                                                                                
 ### CLI Options                                                                                                                                
                                                                                                                                                
 ```bash                                                                                                                                        
 readme-cli-agno [PATH] [OPTIONS]                                                                                                               
 ```                                                                                                                                            
                                                                                                                                                
 - `PATH` (required): Path to the root of your Python project.                                                                                  
                                                                                                                                                
 **Options:**                                                                                                                                   
                                                                                                                                                
 | Option         | Description                                                         | Default            |                                  
 |----------------|---------------------------------------------------------------------|--------------------|                                  
 | `--output`     | Path for the generated README file                                  | `README.md`        |                                  
 | `--preview`    | Print the generated README to console without writing to disk       | `False`            |                                  
 | `--model`      | Specify the OpenAI model to use for code summarization              | `gpt-3.5-turbo`    |                                  
 | `--env-file`   | Custom path to your `.env` file for configuration                   | `.env` (project root) |                               
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## Usage Examples                                                                                                                              
                                                                                                                                                
 Generate a README in the current directory:                                                                                                    
                                                                                                                                                
 ```bash                                                                                                                                        
 readme-cli-agno .                                                                                                                              
 ```                                                                                                                                            
                                                                                                                                                
 Preview the output without saving:                                                                                                             
                                                                                                                                                
 ```bash                                                                                                                                        
 readme-cli-agno . --preview                                                                                                                    
 ```                                                                                                                                            
                                                                                                                                                
 Save to a custom filename and use GPT-4:                                                                                                       
                                                                                                                                                
 ```bash                                                                                                                                        
 readme-cli-agno . --output DOC.md --model gpt-4                                                                                                
 ```                                                                                                                                            
                                                                                                                                                
 Use a custom environment file:                                                                                                                 
                                                                                                                                                
 ```bash                                                                                                                                        
 readme-cli-agno . --env-file configs/secrets.env                                                                                               
 ```                                                                                                                                            
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## How It Works                                                                                                                                
                                                                                                                                                
 1. **Parsing:** Scans your Python project to find modules, classes, and functions.                                                             
 2. **Summarization:** Uses OpenAI's API to generate natural language summaries of your code.                                                   
 3. **Formatting:** Assembles badges, installation instructions, usage examples, API reference, and more using rich Markdown.                   
 4. **Output:** Produces a well-structured `README.md` reflecting your project's details.                                                       
                                                                                                                                                
 *Under the hood, `readme-cli-agno` uses the `agno` agent framework, `typer` for CLI, and `rich` for console formatting.*                       
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## API Reference (for Developers)                                                                                                              
                                                                                                                                                
 See [API Details](#) for technical breakdown. Main commands and modules include:                                                               
                                                                                                                                                
 - **cli:** Entrypoint for the CLI application.                                                                                                 
 - **coordinator:** Orchestrates code analysis and README assembly.                                                                             
 - **formatter:** Formats parsed and summarized data into Markdown sections.                                                                    
 - **parser:** Extracts project data, dependencies, and code structure.                                                                         
 - **summarizer:** Generates natural language summaries of code using an LLM.                                                                   
 - **utils/env & markdown:** Utility functions for environment and Markdown formatting.                                                         
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 ## License                                                                                                                                     
                                                                                                                                                
 This project is licensed under the [MIT License](LICENSE).                                                                                     
                                                                                                                                                
 ---                                                                                                                                            
                                                                                                                                                
 *Contributions, questions, or issues? Feel free to open an issue or PR!*                                                                       
                                                                                                                                                
